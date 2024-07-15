"""
Fichier contenant les différents services de l'API
"""
import requests

"""
Fichier contenant les fonctions pour extraire les caractéristiques des URL.
"""

import socket as socket
import requests as requests
import whois as whois
import re as re
import nltk

nltk.download('stopwords')

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from urllib.parse import urlparse

# Liste des mots vides
stop = set(stopwords.words('english'))


def service_check_if_website_exists(url: str) -> bool:
    """
    Fonction de vérification de l'existence d'un site web

    Args:
        url (str): URL du site web

    Returns:
        bool: True si le site existe, False sinon
    """
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        return False


def extract_features(url):
    """
    Fonction qui retourne les caractéristiques d'une URL.
    :param url: URL à traiter.
    :return: Caractéristiques de l'URL.
    """
    # Initialisation des caractéristiques
    features = {}

    # Nettoyage de l'URL
    url = clean_url(url)

    # Extraction des caractéristiques
    features['url_length'] = get_url_length(url)
    features['ip_address'] = get_ip_address(url)
    features['tld'] = get_tld(url)
    features['who_is'] = get_who_is(url)
    features['https'] = get_https(url)
    features['js_len'] = get_js_len(url)
    features['js_obf_len'] = get_js_obf_len(url)
    features['content'] = get_content(url)
    features['geo_loc'] = get_geo_loc(features['ip_address'])

    return features

def clean_text(text):
    """
    Nettoyage du texte.
    :param text: Texte à nettoyer.
    :return: Texte nettoyé.
    """
    return text


def clean_url(url):
    """
    Nettoyage de l'URL.
    :param url: URL à nettoyer.
    :return: URL nettoyée.
    """
    # On retire https://www
    url = url.replace('https://www.', '')
    url = url.replace('http://www.', '')

    return ' '.join(re.sub(r'^(?:http|ftp)s?://|www\.|\.|/', ' ', url).strip().split())


def get_url_length(url):
    """
    Fonction qui retourne la longueur d'une URL.
    :param url: URL à traiter.
    :return: Longueur de l'URL.
    """
    return len(url)


def get_ip_address(url):
    """
    Fonction qui retourne l'adresse IP d'une URL.
    :param url: URL à traiter.
    :return: Adresse IP.
    """
    url = url.replace('http://', '').replace('https://', '')

    # On retire le / à la fin de l'URL
    if url.endswith('/'):
        url = url[:-1]

    try:
        # On récupère l'adresse IP
        ip = socket.gethostbyname(url)
        return ip
    except Exception as e:
        print(f"Erreur: {e}")
        return ''


def get_tld(url):
    """
    Fonction qui retourne le domaine de premier niveau d'une URL.
    :param url: URL à traiter.
    :return: Domaine de premier niveau.
    """
    return urlparse(url).netloc.split('.')[-1]


def get_who_is(url):
    """
    Fonction qui retourne les informations WHOIS d'une URL.
    :param url: URL à traiter.
    :return: Informations WHOIS.
    """
    try:
        # On récupère le whois de la page web
        whois.whois(url)
        return 'complete'
    except Exception as e:
        print(f"Erreur: {e}")
        return 'incomplete'


def get_https(url):
    """
    Fonction qui retourne si une URL utilise le protocole HTTPS.
    :param url: URL à traiter.
    :return: Utilisation du protocole HTTPS.
    """
    return 'yes' if urlparse(url).scheme == 'https' else 'no'


def get_js_len(url):
    """
    Fonction qui retourne la longueur du code JavaScript d'une URL.
    :param url: URL à traiter.
    :return: Longueur du code JavaScript.
    """
    response = requests.get(url)

    if response.status_code != 200:
        return 0

    soup = BeautifulSoup(response.content, 'html.parser')
    nb_rows = 0

    for script in soup.find_all('script'):
        if script.string:
            nb_rows += len(script.string.split('\n'))

    # On compte les lignes de code JavaScript dans les scripts externes
    for script in soup.find_all('script', src=True):
        js_url = script['src']
        if not js_url.startswith('http'):
            js_url = requests.compat.urljoin(url, js_url)
        js_code = requests.get(js_url)
        if js_code.status_code == 200:
            nb_rows += len(js_code.text.split('\n'))

    return nb_rows


def get_js_obf_len(url):
    """
    Fonction qui retourne la longueur du code JavaScript obscurci d'une URL.
    :param url: URL à traiter.
    :return: Longueur du code JavaScript obscurci.
    """
    return 0


def get_content(url):
    """
    Fonction qui retourne le contenu d'une URL.
    :param url: URL à traiter.
    :return: Contenu de l'URL.
    """
    try:
        # On récupère le contenu de la page web
        response = requests.get(url)

        # Création d'un objet BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Récupération du texte
        text = soup.get_text()

        # Nettoyage du texte
        text = re.sub(r'[^\w\s]', '', text).lower()

        return ' '.join([item for item in text.split() if item not in stop])

    except Exception as e:
        print(f"Erreur: {e}")
        return ''


def get_geo_loc(ip):
    """
    Fonction qui retourne la localisation géographique d'une URL.
    :param ip: Adresse IP à traiter.
    :return: Localisation géographique.
    """
    try:
        # On récupère la localisation géographique
        response = requests.get(f'http://ip-api.com/json/{ip}')
        data = response.json()

        return data['country']

    except Exception as e:
        print(f"Erreur: {e}")
        return 'Unknown'


