import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from app.data_loader import metrics_to_dataframe

def plot_metric_evolution(metrics, metric_name, title=None):
    """
    Crée un graphique d'évolution d'une métrique financière
    
    Args:
        metrics (dict): Dictionnaire des métriques financières
        metric_name (str): Nom de la métrique à afficher
        title (str, optional): Titre du graphique
    """
    if not metrics or metric_name not in metrics:
        st.error(f"Données non disponibles pour la métrique: {metric_name}")
        return
    
    metric_data = metrics[metric_name]
    years = sorted([int(year) for year in metric_data.keys()])
    values = [metric_data[str(year)] for year in years]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, values, marker='o', linewidth=2, markersize=8)
    
    # Ajouter les valeurs sur le graphique
    for i, value in enumerate(values):
        ax.annotate(f"{value:,.0f}", 
                   (years[i], values[i]),
                   textcoords="offset points",
                   xytext=(0, 10),
                   ha='center')
    
    if title:
        ax.set_title(title, fontsize=16)
    else:
        ax.set_title(f"Évolution de {metric_name}", fontsize=16)
    
    ax.set_xlabel("Année", fontsize=12)
    ax.set_ylabel("Valeur (en millions $)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Formater l'axe y pour les grands nombres
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: f"{x:,.0f}")
    )
    
    st.pyplot(fig)

def plot_comparative_metric(all_metrics, metric_name, companies, title=None):
    """
    Crée un graphique comparatif d'une métrique pour plusieurs entreprises
    
    Args:
        all_metrics (dict): Dictionnaire des métriques pour toutes les entreprises
        metric_name (str): Nom de la métrique à comparer
        companies (list): Liste des entreprises à comparer
        title (str, optional): Titre du graphique
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    for company, metrics in all_metrics.items():
        if company in companies and metric_name in metrics:
            metric_data = metrics[metric_name]
            years = sorted([int(year) for year in metric_data.keys()])
            values = [metric_data[str(year)] for year in years]
            
            ax.plot(years, values, marker='o', linewidth=2, markersize=8, label=company.upper())
    
    if title:
        ax.set_title(title, fontsize=16)
    else:
        ax.set_title(f"Comparaison de {metric_name}", fontsize=16)
    
    ax.set_xlabel("Année", fontsize=12)
    ax.set_ylabel("Valeur (en millions $)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Formater l'axe y pour les grands nombres
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: f"{x:,.0f}")
    )
    
    st.pyplot(fig)

def plot_prediction(predictions, metric_name, title=None):
    """
    Crée un graphique de prédiction pour une métrique
    
    Args:
        predictions (dict): Dictionnaire des prédictions
        metric_name (str): Nom de la métrique à afficher
        title (str, optional): Titre du graphique
    """
    if not predictions or metric_name not in predictions:
        st.error(f"Données de prédiction non disponibles pour: {metric_name}")
        return
    
    metric_pred = predictions[metric_name]
    years = sorted([int(year) for year in metric_pred.keys()])
    values = [metric_pred[str(year)]["value"] for year in years]
    confidence = [metric_pred[str(year)]["confidence_level"] for year in years]
    
    # Créer des intervalles de confiance
    upper_bound = [values[i] * (1 + (100 - confidence[i]) / 100) for i in range(len(values))]
    lower_bound = [values[i] * (1 - (100 - confidence[i]) / 100) for i in range(len(values))]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Tracer la ligne principale
    ax.plot(years, values, marker='o', linewidth=2, markersize=8, label="Prédiction")
    
    # Ajouter l'intervalle de confiance
    ax.fill_between(years, lower_bound, upper_bound, alpha=0.2, label="Intervalle de confiance")
    
    # Ajouter les valeurs sur le graphique
    for i, value in enumerate(values):
        ax.annotate(f"{value:,.0f}", 
                   (years[i], values[i]),
                   textcoords="offset points",
                   xytext=(0, 10),
                   ha='center')
    
    if title:
        ax.set_title(title, fontsize=16)
    else:
        ax.set_title(f"Prédiction de {metric_name}", fontsize=16)
    
    ax.set_xlabel("Année", fontsize=12)
    ax.set_ylabel("Valeur prédite (en millions $)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Formater l'axe y pour les grands nombres
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, loc: f"{x:,.0f}")
    )
    
    st.pyplot(fig)

def display_metrics_table(metrics):
    """
    Affiche un tableau des métriques financières
    
    Args:
        metrics (dict): Dictionnaire des métriques financières
    """
    if not metrics:
        st.error("Aucune donnée disponible")
        return
    
    df = metrics_to_dataframe(metrics)
    
    # Formater les nombres dans le DataFrame
    formatted_df = df.copy()
    for col in formatted_df.columns:
        formatted_df[col] = formatted_df[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else "N/A")
    
    st.dataframe(formatted_df, use_container_width=True) 