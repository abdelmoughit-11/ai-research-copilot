FROM python:3.11-slim

<<<<<<< HEAD
# Évite les fichiers .pyc et active les logs immédiats
=======
>>>>>>> ccf84e8 (test pipeline)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

<<<<<<< HEAD
# Installer les dépendances système
=======
>>>>>>> ccf84e8 (test pipeline)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

<<<<<<< HEAD
# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Port Streamlit
EXPOSE 8501

# Lancer Streamlit
=======
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

>>>>>>> ccf84e8 (test pipeline)
CMD ["python", "-m", "streamlit", "run", "app/streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
