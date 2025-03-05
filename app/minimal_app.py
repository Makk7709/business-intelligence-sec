import streamlit as st
import json
import os
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Financial Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# Titre de l'application
st.title("Financial Analysis Dashboard")

# Fonction pour lister les fichiers JSON dans un répertoire
def list_json_files(directory):
    files = []
    for file in os.listdir(directory):
        if file.endswith('.json'):
            files.append(file)
    return files

# Fonction pour charger un fichier JSON
def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Sidebar pour la navigation
st.sidebar.title("Navigation")

# Chemin vers le répertoire des données
data_dir = Path("data/results")

# Vérifier si le répertoire existe
if data_dir.exists():
    # Lister les sous-répertoires
    subdirs = [d for d in data_dir.iterdir() if d.is_dir()]
    
    if subdirs:
        selected_subdir = st.sidebar.selectbox(
            "Select Analysis Type",
            options=[d.name for d in subdirs],
            index=0
        )
        
        # Chemin complet vers le sous-répertoire sélectionné
        selected_path = data_dir / selected_subdir
        
        # Lister les fichiers JSON dans le sous-répertoire
        json_files = list_json_files(selected_path)
        
        if json_files:
            selected_file = st.sidebar.selectbox(
                "Select File",
                options=json_files,
                index=0
            )
            
            # Charger et afficher les données JSON
            file_path = selected_path / selected_file
            try:
                data = load_json_file(file_path)
                
                # Afficher les données
                st.subheader(f"Data from {selected_file}")
                st.json(data)
                
                # Afficher quelques informations de base
                st.subheader("Summary")
                st.write(f"Number of keys: {len(data)}")
                
                # Afficher les clés principales
                st.subheader("Main Keys")
                for key in data.keys():
                    st.write(f"- {key}")
                
            except Exception as e:
                st.error(f"Error loading file: {e}")
        else:
            st.info(f"No JSON files found in {selected_path}")
    else:
        st.info(f"No subdirectories found in {data_dir}")
else:
    st.error(f"Directory {data_dir} does not exist")

# Pied de page
st.sidebar.markdown("---")
st.sidebar.info("Financial Analysis Dashboard v1.0")