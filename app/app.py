import streamlit as st
import os
import sys

# Ajout du chemin pour les importations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importation des modules
try:
    from app.pages import home_page, individual_analysis_page, comparative_analysis_page, predictions_page
except ImportError:
    st.error("Erreur d'importation des modules. Vérifiez les chemins d'accès.")
    st.stop()

# Configuration de la page
st.set_page_config(
    page_title="Analyse Financière - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de l'application
st.title("Analyse Financière - Dashboard")
st.write("Bienvenue dans l'application d'analyse financière des rapports 10-K")

# Menu de navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Choisir une page", 
    ["Accueil", "Analyse individuelle", "Analyse comparative", "Prédictions"]
)

# Afficher la page sélectionnée
try:
    if page == "Accueil":
        home_page()
    elif page == "Analyse individuelle":
        individual_analysis_page()
    elif page == "Analyse comparative":
        comparative_analysis_page()
    elif page == "Prédictions":
        predictions_page()
except Exception as e:
    st.error(f"Une erreur s'est produite lors du chargement de la page: {e}")

# Pied de page
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **À propos**
    
    Cette application a été développée pour analyser les données financières 
    extraites des rapports 10-K de différentes entreprises.
    
    Source des données : Rapports 10-K de Tesla, Apple et Microsoft.
    """
) 