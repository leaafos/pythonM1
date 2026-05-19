import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db

def migrate():
    print("Initialisation de la base de données...")
    init_db()
    print("✓ Base de données initialisée avec succès!")
    print("✓ Tables créées: villes, foyers, consommation_gaz, prix_gaz")
    print('Migration terminée.')

if __name__ == '__main__':
    migrate()

