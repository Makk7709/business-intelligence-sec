import streamlit as st
import pandas as pd
import os
import json

# Configuration de la page
st.set_page_config(
    page_title="Analyse Financière - Version Intermédiaire",
    page_icon="📊",
    layout="wide"
)

# Titre de l'application
st.title("Analyse Financière - Version Intermédiaire")
st.write("Cette version ajoute progressivement des fonctionnalités pour identifier où se situe le problème.")

# Fonction pour charger les données
def load_data(company_code):
    try:
        base_path = f"data/results/comparative/{company_code}"
        
        # Noms de fichiers
        if company_code == "tsla":
            metrics_path = os.path.join(base_path, "tesla_financial_data.json")
        elif company_code == "aapl":
            metrics_path = os.path.join(base_path, "apple_financial_data.json")
        elif company_code == "msft":
            metrics_path = os.path.join(base_path, "microsoft_financial_data.json")
        else:
            metrics_path = os.path.join(base_path, f"{company_code}_financial_data.json")
        
        st.write(f"Tentative de chargement du fichier: {metrics_path}")
        
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                data = json.load(f)
                
            # Extraire les métriques du fichier
            if "metrics" in data:
                metrics = data["metrics"]
            else:
                metrics = data
                
            return metrics
        else:
            st.warning(f"Fichier non trouvé: {metrics_path}")
            return {}
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return {}

# Interface utilisateur
companies = {
    "Tesla": "tsla",
    "Apple": "aapl",
    "Microsoft": "msft"
}

# Sélection de l'entreprise
company_name = st.selectbox("Sélectionnez une entreprise", list(companies.keys()))
company_code = companies[company_name]

# Bouton pour charger les données
if st.button("Charger les données"):
    # Chargement des données
    metrics = load_data(company_code)
    
    # Stockage des données dans la session
    st.session_state.metrics = metrics
    
    # Affichage d'un message de confirmation
    if metrics:
        st.success(f"Données chargées avec succès pour {company_name}")
    else:
        st.error(f"Aucune donnée disponible pour {company_name}")

# Affichage des données si elles sont disponibles
if 'metrics' in st.session_state:
    metrics = st.session_state.metrics
    
    # Affichage du contenu brut pour le débogage
    with st.expander("Contenu brut du fichier (pour débogage)"):
        st.json(metrics)
    
    # Création d'un DataFrame
    data = {}
    for metric, values in metrics.items():
        if isinstance(values, dict):
            for year, value in values.items():
                if year not in data:
                    data[year] = {}
                data[year][metric] = value
    
    if data:
        # Création du DataFrame
        df = pd.DataFrame.from_dict(data, orient='index')
        
        # Affichage du tableau
        st.subheader(f"Métriques financières de {company_name}")
        st.dataframe(df)
        
        # Sélection de la métrique à visualiser
        available_metrics = list(metrics.keys())
        if available_metrics:
            selected_metric = st.selectbox("Sélectionnez une métrique à visualiser", available_metrics)
            
            if selected_metric in metrics and st.button("Afficher le graphique"):
                st.write(f"Vous avez sélectionné la métrique: {selected_metric}")
                # Nous n'affichons pas encore de graphique pour éviter les problèmes potentiels avec matplotlib
    else:
        st.warning("Aucune donnée structurée disponible") 