import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# Ajout du chemin pour les importations
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importation des modules
from app.data_loader import load_financial_data, load_comparative_data, load_prediction_data
from app.visualizations import plot_metric_evolution, plot_comparative_metric, plot_prediction, display_metrics_table

def home_page():
    """Page d'accueil de l'application"""
    st.header("Analyse Financière des Rapports 10-K")
    
    st.write("""
    Cette application permet d'analyser les données financières extraites des rapports 10-K 
    de différentes entreprises. Elle offre plusieurs fonctionnalités :
    
    - **Analyse individuelle** : Visualisation des métriques financières d'une entreprise
    - **Analyse comparative** : Comparaison des performances de plusieurs entreprises
    - **Prédictions** : Visualisation des prédictions de performance future
    
    Utilisez le menu de navigation à gauche pour accéder aux différentes fonctionnalités.
    """)
    
    st.subheader("Entreprises disponibles")
    companies = {
        "Tesla": "tsla",
        "Apple": "aapl",
        "Microsoft": "msft"
    }
    
    for name, code in companies.items():
        metrics, _ = load_financial_data(code)
        if metrics:
            st.write(f"- **{name}** : Données disponibles")
        else:
            st.write(f"- **{name}** : Données non disponibles")
    
    st.subheader("Comment utiliser cette application")
    st.write("""
    1. Sélectionnez une page dans le menu de navigation à gauche
    2. Choisissez l'entreprise ou les métriques que vous souhaitez analyser
    3. Explorez les visualisations et les tableaux de données
    """)

def individual_analysis_page():
    """Page d'analyse individuelle"""
    st.header("Analyse Individuelle")
    
    companies = {
        "Tesla": "tsla",
        "Apple": "aapl",
        "Microsoft": "msft"
    }
    
    company_name = st.selectbox("Sélectionnez une entreprise", list(companies.keys()))
    company_code = companies[company_name]
    
    metrics, ratios = load_financial_data(company_code)
    
    if not metrics:
        st.error(f"Aucune donnée disponible pour {company_name}")
        return
    
    st.subheader(f"Métriques financières de {company_name}")
    
    # Afficher un tableau des métriques
    display_metrics_table(metrics)
    
    # Sélection de la métrique à visualiser
    available_metrics = list(metrics.keys())
    selected_metric = st.selectbox("Sélectionnez une métrique à visualiser", available_metrics)
    
    # Visualisation de la métrique sélectionnée
    plot_metric_evolution(metrics, selected_metric, f"Évolution de {selected_metric} - {company_name}")
    
    # Afficher les ratios financiers
    if ratios:
        st.subheader("Ratios financiers")
        
        # Créer un DataFrame pour les ratios
        ratios_df = pd.DataFrame.from_dict(ratios, orient='index')
        ratios_df = ratios_df.T
        
        # Formater les nombres dans le DataFrame
        formatted_ratios = ratios_df.copy()
        for col in formatted_ratios.columns:
            formatted_ratios[col] = formatted_ratios[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "N/A")
        
        st.dataframe(formatted_ratios, use_container_width=True)

def comparative_analysis_page():
    """Page d'analyse comparative"""
    st.header("Analyse Comparative")
    
    companies = {
        "Tesla": "tsla",
        "Apple": "aapl",
        "Microsoft": "msft"
    }
    
    selected_companies = st.multiselect(
        "Sélectionnez les entreprises à comparer",
        list(companies.keys()),
        default=list(companies.keys())[:2]
    )
    
    if not selected_companies:
        st.warning("Veuillez sélectionner au moins une entreprise")
        return
    
    # Charger les données pour toutes les entreprises sélectionnées
    all_metrics = {}
    all_ratios = {}
    
    for company_name in selected_companies:
        company_code = companies[company_name]
        metrics, ratios = load_financial_data(company_code)
        
        if metrics:
            all_metrics[company_name] = metrics
            all_ratios[company_name] = ratios
    
    if not all_metrics:
        st.error("Aucune donnée disponible pour les entreprises sélectionnées")
        return
    
    # Trouver les métriques communes à toutes les entreprises
    common_metrics = set()
    for company, metrics in all_metrics.items():
        if not common_metrics:
            common_metrics = set(metrics.keys())
        else:
            common_metrics = common_metrics.intersection(set(metrics.keys()))
    
    # Sélection de la métrique à comparer
    selected_metric = st.selectbox("Sélectionnez une métrique à comparer", list(common_metrics))
    
    # Visualisation comparative
    plot_comparative_metric(all_metrics, selected_metric, selected_companies, 
                           f"Comparaison de {selected_metric}")
    
    # Afficher les données comparatives
    st.subheader("Tableau comparatif")
    
    # Créer un DataFrame pour la comparaison
    comparison_data = {}
    
    for company, metrics in all_metrics.items():
        if selected_metric in metrics:
            metric_data = metrics[selected_metric]
            for year, value in metric_data.items():
                if year not in comparison_data:
                    comparison_data[year] = {}
                comparison_data[year][company] = value
    
    if comparison_data:
        df = pd.DataFrame.from_dict(comparison_data, orient='index')
        df.index = pd.to_numeric(df.index)
        df = df.sort_index()
        
        # Formater les nombres dans le DataFrame
        formatted_df = df.copy()
        for col in formatted_df.columns:
            formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")
        
        st.dataframe(formatted_df, use_container_width=True)
    
    # Afficher les ratios comparatifs
    st.subheader("Comparaison des ratios financiers")
    
    # Trouver les ratios communs
    common_ratios = set()
    for company, ratios in all_ratios.items():
        if not common_ratios:
            common_ratios = set(ratios.keys())
        else:
            common_ratios = common_ratios.intersection(set(ratios.keys()))
    
    # Sélection du ratio à comparer
    if common_ratios:
        selected_ratio = st.selectbox("Sélectionnez un ratio à comparer", list(common_ratios))
        
        # Créer un DataFrame pour la comparaison des ratios
        ratio_comparison = {}
        
        for company, ratios in all_ratios.items():
            if selected_ratio in ratios:
                ratio_comparison[company] = ratios[selected_ratio]
        
        if ratio_comparison:
            ratio_df = pd.DataFrame.from_dict(ratio_comparison, orient='index')
            
            # Formater les pourcentages
            formatted_ratio_df = ratio_df.copy()
            for col in formatted_ratio_df.columns:
                formatted_ratio_df[col] = formatted_ratio_df[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else "N/A")
            
            st.dataframe(formatted_ratio_df, use_container_width=True)

def predictions_page():
    """Page de prédictions"""
    st.header("Prédictions de Performance Future")
    
    predictions = load_prediction_data()
    
    if not predictions:
        st.error("Aucune donnée de prédiction disponible")
        return
    
    # Sélection de la métrique à visualiser
    available_metrics = list(predictions.keys())
    selected_metric = st.selectbox("Sélectionnez une métrique à visualiser", available_metrics)
    
    # Visualisation de la prédiction
    plot_prediction(predictions, selected_metric, f"Prédiction de {selected_metric}")
    
    # Afficher les détails de la prédiction
    st.subheader("Détails de la prédiction")
    
    metric_pred = predictions[selected_metric]
    years = sorted([int(year) for year in metric_pred.keys()])
    
    # Créer un DataFrame pour les détails
    details = []
    for year in years:
        year_str = str(year)
        pred = metric_pred[year_str]
        details.append({
            "Année": year,
            "Valeur prédite": f"{pred['value']:,.0f}",
            "Taux de croissance": f"{pred['growth_rate']:.2f}%",
            "Niveau de confiance": f"{pred['confidence_level']:.2f}%"
        })
    
    details_df = pd.DataFrame(details)
    st.dataframe(details_df, use_container_width=True)
    
    # Afficher la justification
    if "justification" in metric_pred[str(years[0])]:
        st.subheader("Justification")
        for year in years:
            year_str = str(year)
            if "justification" in metric_pred[year_str]:
                st.write(f"**{year}** : {metric_pred[year_str]['justification']}") 