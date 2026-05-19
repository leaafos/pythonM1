FROM python:3.10.18-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Dépendances pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Initialiser la base de données
RUN python scripts/migrate.py

# Exposer le port
EXPOSE 5000

# Démarrer l'application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
