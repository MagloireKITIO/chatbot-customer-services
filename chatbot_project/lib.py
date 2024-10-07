import nltk
import os

# Définir le chemin correct pour nltk_data dans ton environnement virtuel
nltk_data_path = os.path.join("C:/Users/stage.dsi.pmo/Documents/Projet Dev/Activa Hr/chatbot/.venv/nltk_data")

# Créer le dossier s'il n'existe pas déjà
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

# Ajouter ce chemin à NLTK
nltk.data.path.append(nltk_data_path)

# Télécharger le modèle 'punkt'
nltk.download('punkt', download_dir=nltk_data_path)
