# Choix de l'image de base
FROM python:3.10.9-slim

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installe les dépendances nécessaires
RUN pip install --no-cache-dir -r requirements.txt

# Copie le contenu du répertoire src dans le répertoire de travail
COPY src .

# Définit la commande par défaut à exécuter lors du démarrage du conteneur
CMD ["python3", "main.py"]