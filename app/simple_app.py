import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# Configuration de la page
st.set_page_config(
    page_title="Analyse Financière - Version Simple",
    page_icon="📊",
    layout="wide"
)

# Titre de l'application
st.title("Analyse Financière - Version Simple")
st.write("Cette version simplifiée permet de tester l'affichage des données financières.")

# Fonction pour charger les données
def load_data(company_code):
    try:
        base_path = f"data/results/comparative/{company_code}"
        
        # Correction des noms de fichiers
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

# Interface utilisateur simplifiée
companies = {
    "Tesla": "tsla",
    "Apple": "aapl",
    "Microsoft": "msft"
}

company_name = st.selectbox("Sélectionnez une entreprise", list(companies.keys()))
company_code = companies[company_name]

# Chargement des données
metrics = load_data(company_code)

# Affichage du contenu brut pour le débogage
st.subheader("Contenu brut du fichier (pour débogage)")
st.json(metrics)

# Affichage des données
if metrics:
    st.subheader(f"Métriques financières de {company_name}")
    
    # Créer un DataFrame simple
    data = {}
    for metric, values in metrics.items():
        if isinstance(values, dict):
            for year, value in values.items():
                if year not in data:
                    data[year] = {}
                data[year][metric] = value
    
    if data:
        df = pd.DataFrame.from_dict(data, orient='index')
        st.dataframe(df)
        
        # Afficher un graphique simple
        available_metrics = list(metrics.keys())
        if available_metrics:
            selected_metric = st.selectbox("Sélectionnez une métrique à visualiser", available_metrics)
            
            if selected_metric in metrics:
                st.subheader(f"Évolution de {selected_metric}")
                
                metric_data = metrics[selected_metric]
                years = sorted([int(year) for year in metric_data.keys()])
                values = [metric_data[str(year)] for year in years]
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(years, values, marker='o')
                ax.set_title(f"Évolution de {selected_metric} - {company_name}")
                ax.set_xlabel("Année")
                ax.set_ylabel(f"{selected_metric} (en millions $)")
                ax.grid(True)
                
                st.pyplot(fig)
    else:
        st.warning("Aucune donnée structurée disponible")
else:
    st.error(f"Aucune donnée disponible pour {company_name}") 