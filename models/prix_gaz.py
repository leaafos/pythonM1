import sqlite3
from database import get_db_connection

class PrixGaz:
    @staticmethod
    def create(ville_id, mois, annee, prix_par_kwh):
        """Crée un nouveau prix de gaz"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO prix_gaz (ville_id, mois, annee, prix_par_kwh) 
                   VALUES (?, ?, ?, ?)''',
                (ville_id, mois, annee, prix_par_kwh)
            )
            conn.commit()
            prix_id = cursor.lastrowid
            return PrixGaz.get_by_id(prix_id)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(prix_id):
        """Récupère un prix par ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, v.nom as ville_nom 
            FROM prix_gaz p
            LEFT JOIN villes v ON p.ville_id = v.id
            WHERE p.id = ?
        ''', (prix_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_ville_and_period(ville_id, mois, annee):
        """Récupère le prix pour une ville et une période"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, v.nom as ville_nom 
            FROM prix_gaz p
            LEFT JOIN villes v ON p.ville_id = v.id
            WHERE p.ville_id = ? AND p.mois = ? AND p.annee = ?
        ''', (ville_id, mois, annee))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_by_ville(ville_id):
        """Récupère tous les prix d'une ville"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, v.nom as ville_nom 
            FROM prix_gaz p
            LEFT JOIN villes v ON p.ville_id = v.id
            WHERE p.ville_id = ?
            ORDER BY p.annee DESC, p.mois DESC
        ''', (ville_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(prix_id, prix_par_kwh):
        """Met à jour un prix"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE prix_gaz SET prix_par_kwh = ? WHERE id = ?',
            (prix_par_kwh, prix_id)
        )
        conn.commit()
        conn.close()
        return PrixGaz.get_by_id(prix_id)
    
    @staticmethod
    def delete(prix_id):
        """Supprime un prix"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prix_gaz WHERE id = ?', (prix_id,))
        conn.commit()
        conn.close()
        return True
