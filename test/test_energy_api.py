import sys
import os
import pytest
import sqlite3
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application import app
from database import get_db_connection, init_db, DATABASE_PATH
from models.ville import Ville
from models.foyer import Foyer
from models.consommation_gaz import ConsommationGaz
from models.prix_gaz import PrixGaz

@pytest.fixture(autouse=True)
def setup_db():
    """Nettoie et initialise la BD avant chaque test"""
    # Supprimer la BD si elle existe
    if Path(DATABASE_PATH).exists():
        Path(DATABASE_PATH).unlink()
    
    # Réinitialiser la BD
    init_db()
    yield
    
    # Cleanup après les test
    if Path(DATABASE_PATH).exists():
        Path(DATABASE_PATH).unlink()

@pytest.fixture
def client():
    """Crée un client Flask pour les tests"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

HEADERS = {'X-API-Key': 'api-key-123'}

# ==================== TESTS VILLES ====================

def test_create_ville():
    """Test création d'une ville"""
    ville = Ville.create('Paris', 'Île-de-France')
    assert ville is not None
    assert ville['nom'] == 'Paris'
    assert ville['region'] == 'Île-de-France'

def test_get_ville():
    """Test récupération d'une ville"""
    ville_created = Ville.create('Lyon', 'Rhône-Alpes')
    ville = Ville.get_by_id(ville_created['id'])
    assert ville is not None
    assert ville['nom'] == 'Lyon'

def test_get_all_villes():
    """Test récupération de toutes les villes"""
    Ville.create('Paris', 'Île-de-France')
    Ville.create('Lyon', 'Rhône-Alpes')
    villes = Ville.get_all()
    assert len(villes) == 2

def test_update_ville():
    """Test mise à jour d'une ville"""
    ville_created = Ville.create('Marseille', 'PACA')
    ville_updated = Ville.update(ville_created['id'], 'Marseille', 'Provence-Alpes-Côte-d\'Azur')
    assert ville_updated['region'] == 'Provence-Alpes-Côte-d\'Azur'

def test_delete_ville():
    """Test suppression d'une ville"""
    ville = Ville.create('Toulouse', 'Occitanie')
    Ville.delete(ville['id'])
    ville_deleted = Ville.get_by_id(ville['id'])
    assert ville_deleted is None

# ==================== TESTS FOYERS ====================

def test_create_foyer():
    """Test création d'un foyer"""
    ville = Ville.create('Paris', 'Île-de-France')
    foyer = Foyer.create('123 Rue de la Paix', ville['id'], 4, 'gaz')
    assert foyer is not None
    assert foyer['adresse'] == '123 Rue de la Paix'
    assert foyer['nombre_habitants'] == 4

def test_get_foyer():
    """Test récupération d'un foyer"""
    ville = Ville.create('Lyon', 'Rhône-Alpes')
    foyer_created = Foyer.create('456 Avenue Principale', ville['id'])
    foyer = Foyer.get_by_id(foyer_created['id'])
    assert foyer is not None
    assert foyer['adresse'] == '456 Avenue Principale'

def test_get_foyers_by_ville():
    """Test récupération des foyers d'une ville"""
    ville = Ville.create('Marseille', 'PACA')
    Foyer.create('111 Rue A', ville['id'])
    Foyer.create('222 Rue B', ville['id'])
    foyers = Foyer.get_by_ville(ville['id'])
    assert len(foyers) == 2

def test_update_foyer():
    """Test mise à jour d'un foyer"""
    ville = Ville.create('Toulouse', 'Occitanie')
    foyer = Foyer.create('789 Rue C', ville['id'], 2, 'électrique')
    foyer_updated = Foyer.update(foyer['id'], nombre_habitants=5)
    assert foyer_updated['nombre_habitants'] == 5

def test_delete_foyer():
    """Test suppression d'un foyer"""
    ville = Ville.create('Nice', 'PACA')
    foyer = Foyer.create('999 Rue D', ville['id'])
    Foyer.delete(foyer['id'])
    foyer_deleted = Foyer.get_by_id(foyer['id'])
    assert foyer_deleted is None

# ==================== TESTS CONSOMMATION GAZ ====================

def test_create_consommation():
    """Test création d'une consommation"""
    ville = Ville.create('Paris', 'Île-de-France')
    foyer = Foyer.create('123 Rue Test', ville['id'])
    consommation = ConsommationGaz.create(foyer['id'], 1, 2026, 150.5)
    assert consommation is not None
    assert consommation['quantite_kwh'] == 150.5
    assert consommation['mois'] == 1

def test_get_consommation():
    """Test récupération d'une consommation"""
    ville = Ville.create('Lyon', 'Rhône-Alpes')
    foyer = Foyer.create('456 Rue Test', ville['id'])
    cons_created = ConsommationGaz.create(foyer['id'], 2, 2026, 200.0)
    consommation = ConsommationGaz.get_by_id(cons_created['id'])
    assert consommation is not None
    assert consommation['quantite_kwh'] == 200.0

def test_get_consommation_by_foyer():
    """Test récupération des consommations d'un foyer"""
    ville = Ville.create('Marseille', 'PACA')
    foyer = Foyer.create('789 Rue Test', ville['id'])
    ConsommationGaz.create(foyer['id'], 1, 2026, 100.0)
    ConsommationGaz.create(foyer['id'], 2, 2026, 120.0)
    consommations = ConsommationGaz.get_by_foyer(foyer['id'])
    assert len(consommations) == 2

def test_update_consommation():
    """Test mise à jour d'une consommation"""
    ville = Ville.create('Toulouse', 'Occitanie')
    foyer = Foyer.create('101 Rue Test', ville['id'])
    cons = ConsommationGaz.create(foyer['id'], 3, 2026, 150.0)
    cons_updated = ConsommationGaz.update(cons['id'], 200.0)
    assert cons_updated['quantite_kwh'] == 200.0

def test_delete_consommation():
    """Test suppression d'une consommation"""
    ville = Ville.create('Nice', 'PACA')
    foyer = Foyer.create('202 Rue Test', ville['id'])
    cons = ConsommationGaz.create(foyer['id'], 4, 2026, 180.0)
    ConsommationGaz.delete(cons['id'])
    cons_deleted = ConsommationGaz.get_by_id(cons['id'])
    assert cons_deleted is None

# ==================== TESTS PRIX GAZ ====================

def test_create_prix():
    """Test création d'un prix"""
    ville = Ville.create('Paris', 'Île-de-France')
    prix = PrixGaz.create(ville['id'], 1, 2026, 0.15)
    assert prix is not None
    assert prix['prix_par_kwh'] == 0.15

def test_get_prix():
    """Test récupération d'un prix"""
    ville = Ville.create('Lyon', 'Rhône-Alpes')
    prix_created = PrixGaz.create(ville['id'], 2, 2026, 0.18)
    prix = PrixGaz.get_by_id(prix_created['id'])
    assert prix is not None
    assert prix['prix_par_kwh'] == 0.18

def test_get_prix_by_ville():
    """Test récupération des prix d'une ville"""
    ville = Ville.create('Marseille', 'PACA')
    PrixGaz.create(ville['id'], 1, 2026, 0.16)
    PrixGaz.create(ville['id'], 2, 2026, 0.17)
    prix_list = PrixGaz.get_by_ville(ville['id'])
    assert len(prix_list) == 2

def test_update_prix():
    """Test mise à jour d'un prix"""
    ville = Ville.create('Toulouse', 'Occitanie')
    prix = PrixGaz.create(ville['id'], 3, 2026, 0.14)
    prix_updated = PrixGaz.update(prix['id'], 0.20)
    assert prix_updated['prix_par_kwh'] == 0.20

def test_delete_prix():
    """Test suppression d'un prix"""
    ville = Ville.create('Nice', 'PACA')
    prix = PrixGaz.create(ville['id'], 4, 2026, 0.19)
    PrixGaz.delete(prix['id'])
    prix_deleted = PrixGaz.get_by_id(prix['id'])
    assert prix_deleted is None

# ==================== TESTS API ENDPOINTS ====================

def test_api_create_ville(client):
    """Test API création d'une ville"""
    response = client.post('/villes',
        json={'nom': 'Paris', 'region': 'Île-de-France'},
        headers=HEADERS
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['nom'] == 'Paris'

def test_api_get_villes(client):
    """Test API récupération des villes"""
    Ville.create('Paris', 'Île-de-France')
    Ville.create('Lyon', 'Rhône-Alpes')
    response = client.get('/villes', headers=HEADERS)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2

def test_api_energie_foyer(client):
    """Test API consommation énergétique d'un foyer"""
    ville = Ville.create('Paris', 'Île-de-France')
    foyer = Foyer.create('123 Rue Test', ville['id'])
    ConsommationGaz.create(foyer['id'], 1, 2026, 150.0)
    PrixGaz.create(ville['id'], 1, 2026, 0.15)
    
    response = client.get(f'/energie/foyer/{foyer["id"]}?mois=1&annee=2026', headers=HEADERS)
    assert response.status_code == 200
    data = response.get_json()
    assert data['consommation']['quantite_kwh'] == 150.0
    assert data['cout_total'] == 22.5  # 150 * 0.15

def test_api_energie_ville(client):
    """Test API consommation énergétique d'une ville"""
    ville = Ville.create('Paris', 'Île-de-France')
    foyer1 = Foyer.create('123 Rue A', ville['id'])
    foyer2 = Foyer.create('456 Rue B', ville['id'])
    ConsommationGaz.create(foyer1['id'], 1, 2026, 100.0)
    ConsommationGaz.create(foyer2['id'], 1, 2026, 200.0)
    PrixGaz.create(ville['id'], 1, 2026, 0.20)
    
    response = client.get(f'/energie/ville/{ville["id"]}?mois=1&annee=2026', headers=HEADERS)
    assert response.status_code == 200
    data = response.get_json()
    assert data['consommation_totale_kwh'] == 300.0
    assert data['nombre_foyers'] == 2
    assert data['cout_total'] == 60.0  # 300 * 0.20


def test_api_stats_consommation_filtre_ville_et_range(client):
    """Test stats détaillées avec filtre ville + date range"""
    paris = Ville.create('Paris', 'Île-de-France')
    lyon = Ville.create('Lyon', 'Auvergne-Rhône-Alpes')

    foyer_paris = Foyer.create('10 Rue A', paris['id'])
    foyer_lyon = Foyer.create('20 Rue B', lyon['id'])

    ConsommationGaz.create(foyer_paris['id'], 1, 2026, 100.0)
    ConsommationGaz.create(foyer_paris['id'], 2, 2026, 120.0)
    ConsommationGaz.create(foyer_lyon['id'], 1, 2026, 400.0)

    PrixGaz.create(paris['id'], 1, 2026, 0.10)
    PrixGaz.create(paris['id'], 2, 2026, 0.20)
    PrixGaz.create(lyon['id'], 1, 2026, 0.50)

    response = client.get(
        f'/stats/consommation?ville_id={paris["id"]}&start=2026-01&end=2026-12',
        headers=HEADERS
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['nombre_releves'] == 2
    assert data['consommation_totale_kwh'] == 220.0
    assert data['cout_total_estime'] == 34.0


def test_api_stats_consommation_par_ville(client):
    """Test stats agrégées par ville sur un range de dates"""
    paris = Ville.create('Paris', 'Île-de-France')
    lyon = Ville.create('Lyon', 'Auvergne-Rhône-Alpes')

    foyer_paris = Foyer.create('11 Rue A', paris['id'])
    foyer_lyon = Foyer.create('21 Rue B', lyon['id'])

    ConsommationGaz.create(foyer_paris['id'], 1, 2026, 200.0)
    ConsommationGaz.create(foyer_lyon['id'], 1, 2026, 300.0)

    PrixGaz.create(paris['id'], 1, 2026, 0.10)
    PrixGaz.create(lyon['id'], 1, 2026, 0.20)

    response = client.get(
        '/stats/consommation/par-ville?start=2026-01&end=2026-12',
        headers=HEADERS
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'villes' in data
    assert len(data['villes']) >= 2

    by_name = {row['ville_nom']: row for row in data['villes']}
    assert by_name['Paris']['consommation_totale_kwh'] == 200.0
    assert by_name['Lyon']['consommation_totale_kwh'] == 300.0
