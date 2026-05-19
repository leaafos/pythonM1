from database import get_db_connection

class Ville:
    @staticmethod
    def create(nom, region=None):
        """Crée une nouvelle ville"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO villes (nom, region) VALUES (?, ?)',
                (nom, region)
            )
            conn.commit()
            ville_id = cursor.lastrowid
            return Ville.get_by_id(ville_id)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(ville_id):
        """Récupère une ville par ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM villes WHERE id = ?', (ville_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all():
        """Récupère toutes les villes"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM villes ORDER BY nom')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(ville_id, nom=None, region=None):
        """Met à jour une ville"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if nom and region:
            cursor.execute(
                'UPDATE villes SET nom = ?, region = ? WHERE id = ?',
                (nom, region, ville_id)
            )
        elif nom:
            cursor.execute('UPDATE villes SET nom = ? WHERE id = ?', (nom, ville_id))
        elif region:
            cursor.execute('UPDATE villes SET region = ? WHERE id = ?', (region, ville_id))
        
        conn.commit()
        conn.close()
        return Ville.get_by_id(ville_id)
    
    @staticmethod
    def delete(ville_id):
        """Supprime une ville"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM villes WHERE id = ?', (ville_id,))
        conn.commit()
        conn.close()
        return True

import sqlite3
