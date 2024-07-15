"""
Fichier permettant d'entrainer un modèle de machine learning avec mlflow et de le sauvegarder.
"""
# Importation des modules
import re
import os
import sys
import logging

# Importation des librairies
import pandas as pd
import nltk
import mlflow
import dotenv
import pickle
import mlflow.sklearn
import pymongo
import time

# Importation des classes et fonctions des librairies
from xgboost import XGBClassifier
from sklearn.cluster import MiniBatchKMeans
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from azure.storage.blob import BlobServiceClient

from storage.storage import azure_storage_connect, azure_storage_upload_file

# Chargement des variables d'environnement
dotenv.load_dotenv()

# Téléchargement des stopwords
nltk.download("stopwords")

# Liste des stopwords
STOP_WORDS = set(nltk.corpus.stopwords.words("english"))

# Initialisation des variables d'environnement MongoDB
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

# Initialisation des variables d'environnement Azure Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def preprocessing_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Fonction permettant de prétraiter les données
    :param data: pd.DataFrame: données à prétraiter
    :return: pd.DataFrame: données prétraitées
    """
    # Suppression des colonnes inutiles
    data = data.drop(columns=["_id", "ip_add", "js_obf_len"])

    # Suppression des lignes avec des valeurs manquantes
    data = data.dropna()

    # On supprime les doublons
    data = data.drop_duplicates()

    # Suppression des stopwords
    stop_words = set(nltk.corpus.stopwords.words("english"))

    #  Nettoyage des stopwords
    data['content'] = data['content'].apply(
        lambda x: ' '.join([word for word in x.split() if word not in stop_words][:50]))

    # Nettoyage des caractères spéciaux
    data['content'] = data['content'].str.replace('[^\w\s]', '')

    # Mise en minuscule
    data['content'] = data['content'].apply(lambda x: x.lower())

    # Nettoyage des urls
    data['url'] = data['url'].apply(lambda x: x.replace('https://www.', ''))
    data['url'] = data['url'].apply(lambda x: x.replace('http://www.', ''))
    data['url'] = data['url'].apply(
        lambda x: ' '.join(re.sub(r'^(?:http|ftp)s?://|www\.|\.|/', ' ', x).strip().split()))

    # Encodage des labels
    data['label'] = data['label'].map({'good': 0, 'bad': 1})

    return data


# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# On essaye de se connecter à la base de données
try:
    logging.info("Connexion à la base de données")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    logging.info("Connexion réussie")

except Exception as e:
    logging.error(f"Erreur lors de la connexion à la base de données : {e}")
    sys.exit(1)

# On récupère les données d'entraînement
logging.info("Récupération des données d'entraînement")
df_train = pd.DataFrame(db.train.find({}))

# On récupère les données de test
logging.info("Récupération des données de test")
df_test = pd.DataFrame(db.test.find({}))

try:
    # On effectue le prétraitement des données
    logging.info("Prétraitement des données d'entraînement")
    df_train_preprocessed = preprocessing_data(df_train)

    logging.info("Prétraitement des données de test")
    df_test_preprocessed = preprocessing_data(df_test)

except Exception as e:
    logging.error(f"Erreur lors du prétraitement des données : {e}")
    sys.exit(1)

with mlflow.start_run():
    # Préparation des données pour l'entraînement
    logging.info("Préparation des données pour l'entraînement")

    # On sépare les données et les labels
    X_train = df_train_preprocessed.drop("label", axis=1)
    y_train = df_train_preprocessed["label"]

    X_test = df_test_preprocessed.drop("label", axis=1)
    y_test = df_test_preprocessed["label"]

    # Paramètres du modèle
    logging.info("Préparation du modèle")

    # Paramètres de la transformation TfidfVectorizer
    tfidf_params = {
        'min_df': 5, 'max_df': 0.95,
        'ngram_range': (1, 2),
        'stop_words': 'english',
        'max_features': 100000
    }

    # Paramètres de la transformation MiniBatchKMeans
    kmeans_params = {
        'n_clusters': 4,
        'init': 'k-means++',
        'init_size': 2048,
        'batch_size': 4096,
        'random_state': 20
    }

    # Création du preprocessor
    preprocessor = ColumnTransformer(transformers=[
        ('content_tfidf_kmeans', Pipeline([
            ('tfidf', TfidfVectorizer(**tfidf_params)),
            # Transformation TfidfVectorizer pour content (permet de convertir le texte en vecteurs)
            ('kmeans', MiniBatchKMeans(**kmeans_params))
            # Transformation MiniBatchKMeans pour content (permet de regrouper les vecteurs en clusters)
        ]), 'content'),
        ('url_tfidf_kmeans', Pipeline([
            ('tfidf', TfidfVectorizer(**tfidf_params)),
            # Transformation TfidfVectorizer pour url (permet de convertir le texte en vecteurs)
            ('kmeans', MiniBatchKMeans(**kmeans_params))
            # Transformation MiniBatchKMeans pour url (permet de regrouper les vecteurs en clusters)
        ]), 'url'),
        ('categorical', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1),
         ['geo_loc', 'tld', 'who_is', 'https']),  # Transformation OrdinalEncoder pour les variables catégorielles
        ('passthrough', 'passthrough', ['js_len', 'url_len'])
    ], remainder='passthrough')  # Les colonnes non mentionnées dans les transformations seront ignorées

    # Création du pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier())
    ])

    # Entraînement du modèle
    logging.info("Entraînement du modèle")

    pipeline.fit(X_train, y_train)

    # Prédiction sur les données de test
    y_pred = pipeline.predict(X_test)

    # Calcul de la précision
    accuracy = accuracy_score(y_test, y_pred)

    # Log de la précision
    mlflow.log_metric("accuracy", str(accuracy))

    # Log de la matrice de confusion
    confusion = confusion_matrix(y_test, y_pred)

    # On calcul le pourcentage de faux positif et de faux négatif
    false_positive = confusion[0][1] / confusion[0].sum()
    false_negative = confusion[1][0] / confusion[1].sum()

    # Log du pourcentage de faux positif et de faux négatif
    mlflow.log_metric("false_positive", str(false_positive))
    mlflow.log_metric("false_negative", str(false_negative))

    # On calcul le pourcentage de vrai positif et de vrai négatif
    true_positive = confusion[1][1] / confusion[1].sum()
    true_negative = confusion[0][0] / confusion[0].sum()

    # Log du pourcentage de vrai positif et de vrai négatif
    mlflow.log_metric("true_positive", str(true_positive))
    mlflow.log_metric("true_negative", str(true_negative))

    # On calcul le pourcentage de précision et de rappel
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)

    # Log du pourcentage de précision et de rappel
    mlflow.log_metric("precision", str(precision))
    mlflow.log_metric("recall", str(recall))

    # On calcul le score F1
    f1_score = 2 * (precision * recall) / (precision + recall)

    # Log du score F1
    mlflow.log_metric("f1_score", str(f1_score))

    # Log de la validation du modèle
    logging.info("Fin de la validation du modèle")

    # Sauvegarde du modèle
    logging.info("Sauvegarde du modèle entraîné")

    # Sauvegarde du modèle
    mlflow.sklearn.log_model(pipeline, "model")

    # Réccupération de l'identifiant du modèle
    model_id = mlflow.active_run().info.run_id

    # Sauvegarde du modèle dans la base de données
    logging.info("Sauvegarde du modèle dans la base de données")

    db.models.insert_one({
        "model_id": model_id,
        "accuracy": accuracy,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_positive": true_positive,
        "true_negative": true_negative,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score
    })

    try:
        # On se connecte au stockage Azure
        client = azure_storage_connect(AZURE_STORAGE_CONNECTION_STRING)
    except Exception as e:
        logging.error(f"Erreur lors de la connexion au stockage Azure: {e}")
        exit(1)

    # On sauvegarde le modèle dans le stockage Azure
    logging.info("Sauvegarde du modèle dans le stockage Azure")

    # On récupère le chemin du modèle
    mlflow_model_path = f"mlruns/0/{mlflow.active_run().info.run_id}/artifacts/model/model.pkl"

    try:
        # On se connecte au stockage Azure
        client = azure_storage_connect(AZURE_STORAGE_CONNECTION_STRING)

        # On upload le modèle
        azure_storage_upload_file(client, "models",f"{mlflow.active_run().info.run_id}.pkl", mlflow_model_path)

    except Exception as e:
        logging.error(f"Erreur lors de la sauvegarde du modèle dans le stockage Azure: {e}")
        exit(1)

    # Fin de l'entraînement du modèle
    logging.info("Fin de l'entraînement du modèle")

    # On supprime les données d'entraînement et de test
    logging.info("Suppression des données d'entraînement et de test pour libérer de l'espace en mémoire")

    df_train = None
    df_test = None

    # On attend 24h avant de relancer le script pour l'entraînement d'un nouveau modèle
    logging.info("Attente de 24h avant de relancer le script")
    time.sleep(86400)

