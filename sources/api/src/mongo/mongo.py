"""
Fichier contenant les fonctions de connexion et de gestion de la base de données MongoDB
"""
from typing import Any, Mapping

from pymongo import MongoClient
from pymongo.database import Database


def mongo_connect(uri: str, db: str) -> Database[Mapping[str, Any] | Any]:
    """
    Fonction de connexion à une base de données MongoDB

    Args:
        uri (str): URI de connexion à la base de données
        db (str): Nom de la base de données

    Returns:
        MongoClient: Objet de connexion à la base de données
    """
    client = MongoClient(uri)
    return client[db]


def mongo_insert_many(db: Database[Mapping[str, Any] | Any], collection: str,
                      data: list[Mapping[str, Any] | Any]) -> None:
    """
    Fonction d'insertion de plusieurs documents dans une collection

    Args:
        db (Database): Base de données dans laquelle insérer les documents
        collection (str): Nom de la collection dans laquelle insérer les documents
        data (list): Liste des documents à insérer
    """
    db[collection].insert_many(data)


def mongo_insert_one(db: Database[Mapping[str, Any] | Any], collection: str, data: Mapping[str, Any] | Any) -> None:
    """
    Fonction d'insertion d'un document dans une collection

    Args:
        db (Database): Base de données dans laquelle insérer le document
        collection (str): Nom de la collection dans laquelle insérer le document
        data (dict): Document à insérer
    """
    db[collection].insert_one(data)


def mongo_find_one(db: Database[Mapping[str, Any] | Any], collection: str, query: Mapping[str, Any] | Any) -> Mapping[
                                                                                                                  str, Any] | Any:
    """
    Fonction de recherche d'un document dans une collection

    Args:
        db (Database): Base de données dans laquelle rechercher le document
        collection (str): Nom de la collection dans laquelle rechercher le document
        query (dict): Filtre de recherche

    Returns:
        dict: Document trouvé
    """
    return db[collection].find_one(query)


def mongo_find(db: Database[Mapping[str, Any] | Any], collection: str, query: Mapping[str, Any] | Any) -> list[
    Mapping[str, Any] | Any]:
    """
    Fonction de recherche de plusieurs documents dans une collection

    Args:
        db (Database): Base de données dans laquelle rechercher les documents
        collection (str): Nom de la collection dans laquelle rechercher les documents
        query (dict): Filtre de recherche

    Returns:
        list: Liste des documents trouvés
    """
    return list(db[collection].find(query))
