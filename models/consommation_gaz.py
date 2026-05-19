import sqlite3
from database import get_db_connection

class ConsommationGaz:
    @staticmethod
    def create(foyer_id, mois, annee, quantite_kwh):
        """Crée une nouvelle consommation de gaz"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO consommation_gaz (foyer_id, mois, annee, quantite_kwh) 
                   VALUES (?, ?, ?, ?)''',
                (foyer_id, mois, annee, quantite_kwh)
            )
            conn.commit()
            consommation_id = cursor.lastrowid
            return ConsommationGaz.get_by_id(consommation_id)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(consommation_id):
        """Récupère une consommation par ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM consommation_gaz WHERE id = ?', (consommation_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_foyer(foyer_id):
        """Récupère toutes les consommations d'un foyer"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM consommation_gaz 
            WHERE foyer_id = ?
            ORDER BY annee DESC, mois DESC
        ''', (foyer_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_foyer_and_period(foyer_id, mois, annee):
        """Récupère la consommation d'un foyer pour une période"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM consommation_gaz 
            WHERE foyer_id = ? AND mois = ? AND annee = ?
        ''', (foyer_id, mois, annee))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def update(consommation_id, quantite_kwh):
        """Met à jour une consommation"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE consommation_gaz SET quantite_kwh = ? WHERE id = ?',
            (quantite_kwh, consommation_id)
        )
        conn.commit()
        conn.close()
        return ConsommationGaz.get_by_id(consommation_id)
    
    @staticmethod
    def delete(consommation_id):
        """Supprime une consommation"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM consommation_gaz WHERE id = ?', (consommation_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_stats(start_annee, start_mois, end_annee, end_mois, ville_id=None):
        """Récupère des statistiques de consommation sur une plage de dates, filtrables par ville."""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                cg.id,
                cg.foyer_id,
                cg.mois,
                cg.annee,
                cg.quantite_kwh,
                f.adresse,
                f.ville_id,
                v.nom AS ville_nom,
                pg.prix_par_kwh,
                CASE
                    WHEN pg.prix_par_kwh IS NOT NULL THEN cg.quantite_kwh * pg.prix_par_kwh
                    ELSE NULL
                END AS cout_estime
            FROM consommation_gaz cg
            INNER JOIN foyers f ON f.id = cg.foyer_id
            INNER JOIN villes v ON v.id = f.ville_id
            LEFT JOIN prix_gaz pg
                ON pg.ville_id = f.ville_id
                AND pg.mois = cg.mois
                AND pg.annee = cg.annee
            WHERE (cg.annee * 100 + cg.mois) BETWEEN (? * 100 + ?) AND (? * 100 + ?)
        '''

        params = [start_annee, start_mois, end_annee, end_mois]

        if ville_id is not None:
            query += ' AND f.ville_id = ?'
            params.append(ville_id)

        query += ' ORDER BY cg.annee ASC, cg.mois ASC, cg.foyer_id ASC'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_stats_grouped_by_ville(start_annee, start_mois, end_annee, end_mois):
        """Récupère les statistiques agrégées par ville sur une plage de dates."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT
                v.id AS ville_id,
                v.nom AS ville_nom,
                COUNT(DISTINCT f.id) AS nombre_foyers,
                COUNT(cg.id) AS nombre_releves,
                COALESCE(SUM(cg.quantite_kwh), 0) AS consommation_totale_kwh,
                COALESCE(
                    SUM(
                        CASE
                            WHEN pg.prix_par_kwh IS NOT NULL THEN cg.quantite_kwh * pg.prix_par_kwh
                            ELSE 0
                        END
                    ),
                    0
                ) AS cout_total_estime
            FROM villes v
            LEFT JOIN foyers f ON f.ville_id = v.id
            LEFT JOIN consommation_gaz cg
                ON cg.foyer_id = f.id
                AND (cg.annee * 100 + cg.mois) BETWEEN (? * 100 + ?) AND (? * 100 + ?)
            LEFT JOIN prix_gaz pg
                ON pg.ville_id = v.id
                AND pg.mois = cg.mois
                AND pg.annee = cg.annee
            GROUP BY v.id, v.nom
            ORDER BY consommation_totale_kwh DESC, v.nom ASC
            ''',
            (start_annee, start_mois, end_annee, end_mois)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
