import streamlit as st
import os
import json

# Configuration de la page
st.set_page_config(
    page_title="Application Minimale Plus",
    page_icon="🔍"
)

# Contenu simple
st.title("Application Streamlit Minimale Plus")
st.write("Cette application ajoute juste la lecture de fichier JSON pour identifier si c'est la source du problème.")

# Fonction simple pour lister les fichiers
def list_files(directory):
    try:
        files = os.listdir(directory)
        return files
    except Exception as e:
        return [f"Erreur: {str(e)}"]

# Afficher les répertoires disponibles
st.subheader("Répertoires disponibles")
directories = {
    "Tesla": "data/results/comparative/tsla",
    "Apple": "data/results/comparative/aapl",
    "Microsoft": "data/results/comparative/msft"
}

# Sélection du répertoire
selected_dir = st.selectbox("Sélectionnez un répertoire", list(directories.keys()))
directory_path = directories[selected_dir]

# Afficher les fichiers dans le répertoire
if st.button("Lister les fichiers"):
    files = list_files(directory_path)
    st.write(f"Fichiers dans {directory_path}:")
    for file in files:
        st.write(f"- {file}")

# Fonction pour lire un fichier JSON
def read_json_file(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        else:
            return {"error": f"Fichier non trouvé: {file_path}"}
    except Exception as e:
        return {"error": f"Erreur lors de la lecture du fichier: {str(e)}"}

# Lecture d'un fichier JSON spécifique
if selected_dir == "Tesla":
    json_file = "tesla_financial_data.json"
elif selected_dir == "Apple":
    json_file = "apple_financial_data.json"
elif selected_dir == "Microsoft":
    json_file = "microsoft_financial_data.json"
else:
    json_file = ""

if json_file and st.button("Lire le fichier JSON"):
    file_path = os.path.join(directory_path, json_file)
    st.write(f"Tentative de lecture du fichier: {file_path}")
    data = read_json_file(file_path)
    
    # Afficher seulement si ce n'est pas une erreur
    if "error" not in data:
        st.success(f"Fichier lu avec succès: {json_file}")
    else:
        st.error(data["error"]) 