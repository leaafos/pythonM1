import sqlite3
from database import get_db_connection

class Foyer:
    @staticmethod
    def create(adresse, ville_id, nombre_habitants=None, type_chauffage=None):
        """Crée un nouveau foyer"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                '''INSERT INTO foyers (adresse, ville_id, nombre_habitants, type_chauffage) 
                   VALUES (?, ?, ?, ?)''',
                (adresse, ville_id, nombre_habitants, type_chauffage)
            )
            conn.commit()
            foyer_id = cursor.lastrowid
            return Foyer.get_by_id(foyer_id)
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(foyer_id):
        """Récupère un foyer par ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, v.nom as ville_nom 
            FROM foyers f
            LEFT JOIN villes v ON f.ville_id = v.id
            WHERE f.id = ?
        ''', (foyer_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @staticmethod
    def get_all():
        """Récupère tous les foyers"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, v.nom as ville_nom 
            FROM foyers f
            LEFT JOIN villes v ON f.ville_id = v.id
            ORDER BY f.id
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_ville(ville_id):
        """Récupère tous les foyers d'une ville"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, v.nom as ville_nom 
            FROM foyers f
            LEFT JOIN villes v ON f.ville_id = v.id
            WHERE f.ville_id = ?
        ''', (ville_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(foyer_id, adresse=None, nombre_habitants=None, type_chauffage=None):
        """Met à jour un foyer"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if adresse is not None:
            updates.append('adresse = ?')
            params.append(adresse)
        if nombre_habitants is not None:
            updates.append('nombre_habitants = ?')
            params.append(nombre_habitants)
        if type_chauffage is not None:
            updates.append('type_chauffage = ?')
            params.append(type_chauffage)
        
        if updates:
            params.append(foyer_id)
            query = f'UPDATE foyers SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        return Foyer.get_by_id(foyer_id)
    
    @staticmethod
    def delete(foyer_id):
        """Supprime un foyer"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM foyers WHERE id = ?', (foyer_id,))
        conn.commit()
        conn.close()
        return True
