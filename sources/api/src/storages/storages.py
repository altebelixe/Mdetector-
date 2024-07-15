"""
Permet de travailer avec les services Azure.
"""
import logging

from azure.storage.blob import BlobServiceClient

def azure_storage_connect(uri: str):
    """
    Fonction permettant de se connecter au stockage Azure.
c
    Args:
        uri: URI de connexion au stockage Azure

    Returns:
        Client Azure
    """
    try:
        # On se connecte au stockage Azure
        blob_service_client = BlobServiceClient.from_connection_string(uri)

        # On retourne le client
        return blob_service_client

    except Exception as e:
        # On log l'erreur
        logging.error(f"Erreur lors de la connexion au stockage Azure: {e}")
        return None


def azure_storage_download_file(client, container_name: str, blob_name: str, file_path: str):
    """
    Fonction permettant de télécharger un fichier depuis le stockage Azure.

    Args:
        client: Client Azure
        container_name: Nom du conteneur
        blob_name: Nom du blob
        file_path: Chemin du fichier
    """
    try:
        # On récupère le client du conteneur
        container_client = client.get_container_client(container_name)

        # On télécharge le fichier
        blob_client = container_client.get_blob_client(blob_name)
        with open(file_path, "wb") as f:
            data = blob_client.download_blob()
            data.readinto(f)

    except Exception as e:
        # On log l'erreur
        logging.error(f"Erreur lors du téléchargement du fichier {blob_name}: {e}")


def azure_storage_list_files(client, container_name: str):
    """
    Fonction permettant de lister les fichiers d'un conteneur Azure.

    Args:
        client: Client Azure
        container_name: Nom du conteneur

    Returns:
        Liste des fichiers
    """
    try:
        # On récupère le client du conteneur
        container_client = client.get_container_client(container_name)

        # On liste les fichiers
        blobs_list = container_client.list_blobs()

        return [blob.name for blob in blobs_list]

    except Exception as e:
        # On log l'erreur
        logging.error(f"Erreur lors de la récupération des fichiers du conteneur {container_name}: {e}")
        return None


def azure_storage_upload_file(client, container_name: str, blob_name: str, file_path: str):
    """
    Fonction permettant d'uploader un fichier dans le stockage Azure.

    Args:
        client: Client Azure
        container_name: Nom du conteneur
        blob_name: Nom du blob
        file_path: Chemin du fichier
    """
    try:
        # On récupère le client du conteneur
        container_client = client.get_container_client(container_name)

        # On upload le fichier
        with open(file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data)

    except Exception as e:
        # On log l'erreur
        logging.error(f"Erreur lors de l'upload du fichier {blob_name}: {e}")
