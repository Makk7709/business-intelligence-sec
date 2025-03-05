import streamlit as st
import os
import json
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="Application avec Pandas",
    page_icon="📊"
)

# Contenu simple
st.title("Application Streamlit avec Pandas")
st.write("Cette application ajoute Pandas pour la manipulation des données.")

# Fonction pour lister les fichiers
def list_files(directory):
    try:
        files = os.listdir(directory)
        return files
    except Exception as e:
        return [f"Erreur: {str(e)}"]

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

# Afficher les répertoires disponibles
st.subheader("Répertoires disponibles")
directories = {
    "Tesla": "data/results/comparative/tsla",
    "Apple": "data/results/comparative/aapl",
    "Microsoft": "data/results/comparative/msft"
}

# Sélection du répertoire
selected_dir = st.selectbox("Sélectionnez une entreprise", list(directories.keys()))
directory_path = directories[selected_dir]

# Déterminer le fichier JSON à lire
if selected_dir == "Tesla":
    json_file = "tesla_financial_data.json"
elif selected_dir == "Apple":
    json_file = "apple_financial_data.json"
elif selected_dir == "Microsoft":
    json_file = "microsoft_financial_data.json"
else:
    json_file = ""

# Bouton pour charger les données
if json_file and st.button("Charger les données"):
    file_path = os.path.join(directory_path, json_file)
    st.write(f"Tentative de lecture du fichier: {file_path}")
    data = read_json_file(file_path)
    
    # Afficher seulement si ce n'est pas une erreur
    if "error" not in data:
        st.success(f"Fichier lu avec succès: {json_file}")
        
        # Stocker les données dans la session
        st.session_state.data = data
    else:
        st.error(data["error"])

# Afficher les données si elles sont disponibles
if 'data' in st.session_state:
    data = st.session_state.data
    
    # Afficher le contenu brut
    with st.expander("Contenu brut du fichier"):
        st.json(data)
    
    # Extraire les métriques
    metrics = data
    if "metrics" in data:
        metrics = data["metrics"]
    
    # Convertir en DataFrame
    if metrics:
        st.subheader("Données en format tableau")
        
        # Créer un dictionnaire pour le DataFrame
        df_data = {}
        for metric, values in metrics.items():
            if isinstance(values, dict):
                for year, value in values.items():
                    if year not in df_data:
                        df_data[year] = {}
                    df_data[year][metric] = value
        
        if df_data:
            # Créer le DataFrame
            df = pd.DataFrame.from_dict(df_data, orient='index')
            
            # Afficher le DataFrame
            st.dataframe(df)
        else:
            st.warning("Impossible de créer un tableau à partir des données") 