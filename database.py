import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / 'energy_consumption.db'

def get_db_connection():
    """Crée une connexion à la base de données SQLite"""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialise les tables de la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table villes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS villes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            region TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table foyers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adresse TEXT NOT NULL,
            ville_id INTEGER NOT NULL,
            nombre_habitants INTEGER,
            type_chauffage TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ville_id) REFERENCES villes(id) ON DELETE CASCADE
        )
    ''')
    
    # Table consommation de gaz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consommation_gaz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            foyer_id INTEGER NOT NULL,
            mois INTEGER NOT NULL,
            annee INTEGER NOT NULL,
            quantite_kwh REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (foyer_id) REFERENCES foyers(id) ON DELETE CASCADE,
            UNIQUE(foyer_id, mois, annee)
        )
    ''')
    
    # Table prix du gaz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prix_gaz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ville_id INTEGER NOT NULL,
            mois INTEGER NOT NULL,
            annee INTEGER NOT NULL,
            prix_par_kwh REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ville_id) REFERENCES villes(id) ON DELETE CASCADE,
            UNIQUE(ville_id, mois, annee)
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Base de données initialisée avec succès!")
