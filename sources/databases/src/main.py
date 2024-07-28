"""
Fichier principal de l'application pour remplir la base de données MongoDB avec
les fichiers d'entraînement et de test.
"""
# Importation des modules
import os
import sys
import logging

# Importation des librairies
import dotenv
import pandas
import pymongo

# On charge les variables d'environnement du fichier .env (situé à la racine du projet)
dotenv.load_dotenv()

# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

# Définition des variables d'environnement
MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB = os.environ.get('MONGO_DB')

# Chargement des données d'entraînement
logging.info('Chargement des données d\'entraînement')
df_train = pandas.read_parquet('data/train.parquet')

# Chargement des données de test
logging.info('Chargement des données de test')
df_test = pandas.read_parquet('data/test.parquet')

df_train = df_train.head(250000)
df_test = df_test.head(10000)

# Suppression des colonnes inutiles
logging.info('Suppression des colonnes inutiles')
df_train.drop(columns=['Unnamed: 0'], inplace=True)
df_test.drop(columns=['Unnamed: 0'], inplace=True)

# Connexion à la base de données MongoDB
logging.info('Connexion à la base de données MongoDB')
client = pymongo.MongoClient(MONGO_URI)

# Sélection de la base de données
logging.info('Sélection de la base de données')
db = client[MONGO_DB]

# Suppression des collections
logging.info('Suppression des collections')
db.drop_collection('train')
db.drop_collection('test')

# Insertion des données d'entraînement
logging.info('Insertion des données d\'entraînement')
db.train.insert_many(df_train.to_dict(orient='records'))

# Insertion des données de test
logging.info('Insertion des données de test')
db.test.insert_many(df_test.to_dict(orient='records'))

# Fermeture de la connexion à la base de données MongoDB
logging.info('Fermeture de la connexion à la base de données MongoDB')
client.close()

# Fin du programme
logging.info('Fin du programme')

# Sortie du programme
sys.exit(0)
