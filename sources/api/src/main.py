# Importation des librairies
import os
import pandas as pd
import schedule
import time
import pickle

# Importation des fonctions.
from services.services import *
from storages.storages import *
from mongo.mongo import *
from dotenv import load_dotenv

# Importation des librairies
from joblib import load, dump
from flask import Flask, request, jsonify, render_template
from flask_crontab import Crontab
from flask_cors import CORS

# Chargement des variables d'environnement
load_dotenv()

# Création de l'application Flask
app = Flask(__name__)

# Activation de CORS
CORS(app)

crontab = Crontab()

# Chargement du modèle (initialisation)
model = None

# On customise le logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# On récupère les variables d'environnement
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')

# Essai de connexion à la base de données
try:
    db = mongo_connect(MONGO_URI, MONGO_DB)
except Exception as e:
    logging.error(f"Erreur lors de la connexion à la base de données : {e}")
    exit(1)


# On lance toutes les 24 heures la récupération des données
@crontab.job(minute="0", hour="24")
def load_model():
    """
    Permet de télécharger le modèle sur Azure.
    """
    global model

    # Connexion à azure
    try:
        blob_service_client = azure_storage_connect(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
    except Exception as e:
        logging.error(f"Erreur lors de la connexion au stockage Azure: {e}")
        return None

    logging.info("Connexion au stockage Azure réussie")

    # On recupère dans la base de données le modèle avec le plus grand f1_score
    best_model = db.models.find_one(sort=[("f1_score", -1)])

    print(f"best_model: {best_model}")

    # On recupère le model_id
    model_id = best_model['model_id']

    # Récupération du modèle en production
    azure_storage_download_file(
        blob_service_client,
        "models",
        f"{model_id}.pkl",
        "models/model.pkl"
    )

    logging.info("Modèle téléchargé avec succès")

    # Chargement du modèle
    model = load('models/model.pkl')


# Définition de la route /
@app.route('/api/predict', methods=['GET', 'POST', 'OPTIONS'])
def index():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'success'}), 200

    if request.method == 'POST':
        if model is None:
            load_model()

        data = request.json

        # Si les données ne sont pas fournies
        if 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400

        # Informations de l'utilisateur fournies dans le formulaire
        url = data['url']

        # On recupère les features
        url_len = get_url_length(url)
        ip_add = get_ip_address(url)
        geo_loc = get_geo_loc(ip_add)
        tld = get_tld(url)
        who_is = get_who_is(url)
        https = get_https(url)
        js_len = get_js_len(url)
        content = get_content(url)

        # Création du DataFrame
        features = pd.DataFrame({
            'url': [url],
            'url_len': [url_len],
            'geo_loc': [geo_loc],
            'tld': [tld],
            'who_is': [who_is],
            'https': [https],
            'js_len': [js_len],
            'content': [content],
        }, index=[0])

        # On nettoie le contenu
        features['content'] = features['content'].apply(clean_text)

        # On nettoie l'URL
        features['url'] = features['url'].apply(clean_url)

        # On prédit la classe
        prediction = model.predict(features)

        # On recupère les probabilités de la prédiction de la classe
        proba = model.predict_proba(features)

        # On ajoute la prédiction à la base de données
        features['ip_add'] = ip_add
        features['js_obf_len'] = 0

        if prediction[0] == 0:
            features['label'] = 'good'
        else:
            features['label'] = 'bad'

        mongo_insert_one(db, "train", features.to_dict(orient='records')[0])

        if prediction[0] == 0:
            return {'prediction': 'good', 'proba': str(round(proba[0][0] * 100, 2))}
        return {'prediction': 'malicious', 'proba': str(round(proba[0][1] * 100, 2))}

    return jsonify({'error': 'Method Not Allowed'}), 405


# Lancement de l'application Flask
if __name__ == '__main__':

    # Création d'un dossiers pour les modèles
    if not os.path.exists('models'):
        os.makedirs('models')

    crontab.init_app(app)

    # On charge le modèle au lancement de l'application
    load_model()

    app.run(debug=True, host='0.0.0.0', port=5000)
