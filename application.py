from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from database import init_db
from models.ville import Ville
from models.foyer import Foyer
from models.consommation_gaz import ConsommationGaz
from models.prix_gaz import PrixGaz

app = Flask(__name__)
CORS(app)

GLOBAL_API_KEY = "api-key-123"


def _parse_period(period_value):
    """Convertit YYYY-MM en (annee, mois)."""
    if not period_value:
        return None, None

    try:
        annee_str, mois_str = period_value.split('-')
        annee = int(annee_str)
        mois = int(mois_str)
    except (ValueError, AttributeError):
        return None, None

    if mois < 1 or mois > 12:
        return None, None

    return annee, mois

def auth_wrapper(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != GLOBAL_API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Initialiser la BD au démarrage
init_db()

@app.route('/', methods=['GET'])
def hello_world():
    return 'API Consommation Énergétique - Fonctionnelle'

# ==================== VILLES ====================

@app.route('/villes', methods=['POST'])
@auth_wrapper
def create_ville():
    data = request.get_json()
    ville = Ville.create(data.get('nom'), data.get('region'))
    if ville:
        return jsonify(ville), 201
    return jsonify({"error": "Ville déjà existante"}), 400

@app.route('/villes', methods=['GET'])
@auth_wrapper
def list_villes():
    villes = Ville.get_all()
    return jsonify(villes), 200

@app.route('/villes/<int:ville_id>', methods=['GET'])
@auth_wrapper
def get_ville(ville_id):
    ville = Ville.get_by_id(ville_id)
    if not ville:
        return jsonify({"error": "Ville non trouvée"}), 404
    return jsonify(ville), 200

@app.route('/villes/<int:ville_id>', methods=['PUT'])
@auth_wrapper
def update_ville(ville_id):
    data = request.get_json()
    ville = Ville.update(ville_id, data.get('nom'), data.get('region'))
    if not ville:
        return jsonify({"error": "Ville non trouvée"}), 404
    return jsonify(ville), 200

@app.route('/villes/<int:ville_id>', methods=['DELETE'])
@auth_wrapper
def delete_ville(ville_id):
    Ville.delete(ville_id)
    return jsonify({"message": "Ville supprimée"}), 200

# ==================== FOYERS ====================

@app.route('/foyers', methods=['POST'])
@auth_wrapper
def create_foyer():
    data = request.get_json()
    foyer = Foyer.create(
        data.get('adresse'),
        data.get('ville_id'),
        data.get('nombre_habitants'),
        data.get('type_chauffage')
    )
    if foyer:
        return jsonify(foyer), 201
    return jsonify({"error": "Erreur création foyer"}), 400

@app.route('/foyers', methods=['GET'])
@auth_wrapper
def list_foyers():
    foyers = Foyer.get_all()
    return jsonify(foyers), 200

@app.route('/foyers/<int:foyer_id>', methods=['GET'])
@auth_wrapper
def get_foyer(foyer_id):
    foyer = Foyer.get_by_id(foyer_id)
    if not foyer:
        return jsonify({"error": "Foyer non trouvé"}), 404
    return jsonify(foyer), 200

@app.route('/foyers/<int:foyer_id>', methods=['PUT'])
@auth_wrapper
def update_foyer(foyer_id):
    data = request.get_json()
    foyer = Foyer.update(
        foyer_id,
        data.get('adresse'),
        data.get('nombre_habitants'),
        data.get('type_chauffage')
    )
    if not foyer:
        return jsonify({"error": "Foyer non trouvé"}), 404
    return jsonify(foyer), 200

@app.route('/foyers/<int:foyer_id>', methods=['DELETE'])
@auth_wrapper
def delete_foyer(foyer_id):
    Foyer.delete(foyer_id)
    return jsonify({"message": "Foyer supprimé"}), 200

@app.route('/villes/<int:ville_id>/foyers', methods=['GET'])
@auth_wrapper
def get_foyers_by_ville(ville_id):
    foyers = Foyer.get_by_ville(ville_id)
    return jsonify(foyers), 200

# ==================== CONSOMMATION GAZ ====================

@app.route('/consommation', methods=['POST'])
@auth_wrapper
def create_consommation():
    data = request.get_json()
    consommation = ConsommationGaz.create(
        data.get('foyer_id'),
        data.get('mois'),
        data.get('annee'),
        data.get('quantite_kwh')
    )
    if consommation:
        return jsonify(consommation), 201
    return jsonify({"error": "Consommation déjà enregistrée pour cette période"}), 400

@app.route('/consommation/<int:consommation_id>', methods=['GET'])
@auth_wrapper
def get_consommation(consommation_id):
    consommation = ConsommationGaz.get_by_id(consommation_id)
    if not consommation:
        return jsonify({"error": "Consommation non trouvée"}), 404
    return jsonify(consommation), 200

@app.route('/foyers/<int:foyer_id>/consommation', methods=['GET'])
@auth_wrapper
def get_consommation_by_foyer(foyer_id):
    consommations = ConsommationGaz.get_by_foyer(foyer_id)
    return jsonify(consommations), 200

@app.route('/consommation/<int:consommation_id>', methods=['PUT'])
@auth_wrapper
def update_consommation(consommation_id):
    data = request.get_json()
    consommation = ConsommationGaz.update(consommation_id, data.get('quantite_kwh'))
    if not consommation:
        return jsonify({"error": "Consommation non trouvée"}), 404
    return jsonify(consommation), 200

@app.route('/consommation/<int:consommation_id>', methods=['DELETE'])
@auth_wrapper
def delete_consommation(consommation_id):
    ConsommationGaz.delete(consommation_id)
    return jsonify({"message": "Consommation supprimée"}), 200

# ==================== PRIX GAZ ====================

@app.route('/prix-gaz', methods=['POST'])
@auth_wrapper
def create_prix():
    data = request.get_json()
    prix = PrixGaz.create(
        data.get('ville_id'),
        data.get('mois'),
        data.get('annee'),
        data.get('prix_par_kwh')
    )
    if prix:
        return jsonify(prix), 201
    return jsonify({"error": "Prix déjà enregistré pour cette période"}), 400

@app.route('/prix-gaz/<int:prix_id>', methods=['GET'])
@auth_wrapper
def get_prix(prix_id):
    prix = PrixGaz.get_by_id(prix_id)
    if not prix:
        return jsonify({"error": "Prix non trouvé"}), 404
    return jsonify(prix), 200

@app.route('/villes/<int:ville_id>/prix-gaz', methods=['GET'])
@auth_wrapper
def get_prix_by_ville(ville_id):
    prix_list = PrixGaz.get_by_ville(ville_id)
    return jsonify(prix_list), 200

@app.route('/prix-gaz/<int:prix_id>', methods=['PUT'])
@auth_wrapper
def update_prix(prix_id):
    data = request.get_json()
    prix = PrixGaz.update(prix_id, data.get('prix_par_kwh'))
    if not prix:
        return jsonify({"error": "Prix non trouvé"}), 404
    return jsonify(prix), 200

@app.route('/prix-gaz/<int:prix_id>', methods=['DELETE'])
@auth_wrapper
def delete_prix(prix_id):
    PrixGaz.delete(prix_id)
    return jsonify({"message": "Prix supprimé"}), 200

# ==================== ENDPOINTS CONSOMMATION ENERGÉTIQUE ====================

@app.route('/energie/foyer/<int:foyer_id>', methods=['GET'])
@auth_wrapper
def energie_foyer(foyer_id):
    """
    Retourne la consommation énergétique d'un foyer pour une période donnée
    avec le coût associé
    """
    mois = request.args.get('mois', type=int)
    annee = request.args.get('annee', type=int)
    
    if not mois or not annee:
        return jsonify({"error": "Paramètres mois et annee requis"}), 400
    
    foyer = Foyer.get_by_id(foyer_id)
    if not foyer:
        return jsonify({"error": "Foyer non trouvé"}), 404
    
    consommation = ConsommationGaz.get_by_foyer_and_period(foyer_id, mois, annee)
    if not consommation:
        return jsonify({"error": "Aucune consommation enregistrée"}), 404
    
    prix = PrixGaz.get_by_ville_and_period(foyer['ville_id'], mois, annee)
    cout = None
    if prix:
        cout = consommation['quantite_kwh'] * prix['prix_par_kwh']
    
    return jsonify({
        'foyer': foyer,
        'consommation': dict(consommation),
        'prix_unitaire': prix['prix_par_kwh'] if prix else None,
        'cout_total': cout,
        'periode': f"{mois}/{annee}"
    }), 200

@app.route('/energie/ville/<int:ville_id>', methods=['GET'])
@auth_wrapper
def energie_ville(ville_id):
    """
    Retourne la consommation énergétique totale d'une ville pour une période donnée
    """
    mois = request.args.get('mois', type=int)
    annee = request.args.get('annee', type=int)
    
    if not mois or not annee:
        return jsonify({"error": "Paramètres mois et annee requis"}), 400
    
    ville = Ville.get_by_id(ville_id)
    if not ville:
        return jsonify({"error": "Ville non trouvée"}), 404
    
    foyers = Foyer.get_by_ville(ville_id)
    consommation_totale = 0
    foyers_data = []
    
    for foyer in foyers:
        cons = ConsommationGaz.get_by_foyer_and_period(foyer['id'], mois, annee)
        if cons:
            consommation_totale += cons['quantite_kwh']
            foyers_data.append({
                'foyer_id': foyer['id'],
                'adresse': foyer['adresse'],
                'consommation_kwh': cons['quantite_kwh']
            })
    
    prix = PrixGaz.get_by_ville_and_period(ville_id, mois, annee)
    cout_total = None
    if prix:
        cout_total = consommation_totale * prix['prix_par_kwh']
    
    return jsonify({
        'ville': ville,
        'nombre_foyers': len(foyers),
        'consommation_totale_kwh': consommation_totale,
        'prix_unitaire': prix['prix_par_kwh'] if prix else None,
        'cout_total': cout_total,
        'foyers': foyers_data,
        'periode': f"{mois}/{annee}"
    }), 200


# ==================== STATS ====================

@app.route('/stats/consommation', methods=['GET'])
@auth_wrapper
def stats_consommation():
    """
    Extrait des statistiques détaillées avec filtres:
    - ville_id (optionnel)
    - start (obligatoire, format YYYY-MM)
    - end (obligatoire, format YYYY-MM)
    """
    ville_id = request.args.get('ville_id', type=int)
    start = request.args.get('start')
    end = request.args.get('end')

    start_annee, start_mois = _parse_period(start)
    end_annee, end_mois = _parse_period(end)

    if not start_annee or not end_annee:
        return jsonify({"error": "Paramètres start et end requis au format YYYY-MM"}), 400

    if (start_annee, start_mois) > (end_annee, end_mois):
        return jsonify({"error": "La date start doit être <= end"}), 400

    if ville_id is not None and not Ville.get_by_id(ville_id):
        return jsonify({"error": "Ville non trouvée"}), 404

    releves = ConsommationGaz.get_stats(
        start_annee=start_annee,
        start_mois=start_mois,
        end_annee=end_annee,
        end_mois=end_mois,
        ville_id=ville_id
    )

    consommation_totale = sum(r['quantite_kwh'] for r in releves)
    cout_total = sum((r['cout_estime'] or 0) for r in releves)

    return jsonify({
        'filtres': {
            'ville_id': ville_id,
            'start': start,
            'end': end
        },
        'nombre_releves': len(releves),
        'consommation_totale_kwh': consommation_totale,
        'cout_total_estime': cout_total,
        'resultats': releves
    }), 200


@app.route('/stats/consommation/par-ville', methods=['GET'])
@auth_wrapper
def stats_consommation_par_ville():
    """
    Statistiques agrégées par ville sur un range de dates.
    Params: start=YYYY-MM&end=YYYY-MM
    """
    start = request.args.get('start')
    end = request.args.get('end')

    start_annee, start_mois = _parse_period(start)
    end_annee, end_mois = _parse_period(end)

    if not start_annee or not end_annee:
        return jsonify({"error": "Paramètres start et end requis au format YYYY-MM"}), 400

    if (start_annee, start_mois) > (end_annee, end_mois):
        return jsonify({"error": "La date start doit être <= end"}), 400

    stats = ConsommationGaz.get_stats_grouped_by_ville(
        start_annee=start_annee,
        start_mois=start_mois,
        end_annee=end_annee,
        end_mois=end_mois
    )

    return jsonify({
        'filtres': {
            'start': start,
            'end': end
        },
        'villes': stats
    }), 200

# CRUD Users
@app.route('/users', methods=['GET'])
@auth_wrapper
def list_users():
    # Simple listing (pour démo, pas paginé)
    conn = get_db()
    users = conn.execute('SELECT id, username FROM users').fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

@app.route('/users', methods=['POST'])
@auth_wrapper
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return 'Champs manquants', 400
    if get_user_by_username(username):
        return 'Utilisateur déjà existant', 409
    create_user(username, password)
    return 'Utilisateur créé', 201

@app.route('/users/<int:user_id>', methods=['GET'])
@auth_wrapper
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return 'Utilisateur non trouvé', 404
    return jsonify(dict(user))

@app.route('/users/<int:user_id>', methods=['PUT'])
@auth_wrapper
def update_user_route(user_id):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return 'Champs manquants', 400
    update_user(user_id, username, password)
    return 'Utilisateur modifié', 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
@auth_wrapper
def delete_user_route(user_id):
    delete_user(user_id)
    return 'Utilisateur supprimé', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
