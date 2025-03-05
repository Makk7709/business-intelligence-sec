import plotly.graph_objects as go
import plotly.express as px
import json
import os
import pandas as pd
from flask import render_template_string

def load_financial_data(company):
    """
    Charge les données financières d'une entreprise à partir des fichiers JSON disponibles.
    
    Args:
        company (str): Le nom de l'entreprise (tesla, apple, microsoft)
        
    Returns:
        dict: Les données financières de l'entreprise
    """
    # Liste des chemins possibles pour les données
    possible_paths = [
        f"data/results/{company}_financial_data.json",
        f"data/results/demo/{company}_financial_data.json",
        f"data/results/demo/enhanced/{company}_enhanced_analysis.json",
        f"data/results/demo/hybrid_single/{company}_financial_data.json",
        f"data/results/langchain_test/{company}_financial_data.json"
    ]
    
    # Essayer de charger les données à partir des chemins possibles
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement de {path}: {e}")
    
    # Si aucun fichier n'est trouvé, retourner des données par défaut
    return {
        "metrics": {
            "revenue": {"2022": 81.5, "2023": 94.0, "2024": 99.3},
            "net_income": {"2022": 12.6, "2023": 11.3, "2024": 10.9},
            "gross_profit": {"2022": 30.1, "2023": 32.5, "2024": 34.2}
        },
        "ratios": {
            "net_margin": {"2022": 15.5, "2023": 12.0, "2024": 11.0},
            "gross_margin": {"2022": 37.0, "2023": 34.5, "2024": 34.4},
            "debt_ratio": {"2022": 0.28, "2023": 0.31, "2024": 0.33}
        }
    }

def metrics_to_dataframe(metrics):
    """
    Convertit les métriques en DataFrame pandas pour faciliter la visualisation.
    
    Args:
        metrics (dict): Dictionnaire de métriques financières
        
    Returns:
        pd.DataFrame: DataFrame contenant les métriques par année
    """
    data = {}
    years = set()
    
    # Collecter toutes les années disponibles
    for metric, values in metrics.items():
        for year in values.keys():
            years.add(year)
    
    # Créer un dictionnaire pour le DataFrame
    for year in sorted(years):
        data[year] = {}
        for metric, values in metrics.items():
            if year in values:
                data[year][metric] = values[year]
    
    # Convertir en DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = 'year'
    df.reset_index(inplace=True)
    return df

def create_revenue_chart(company):
    """
    Crée un graphique interactif pour l'évolution des revenus.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        str: Le code HTML du graphique
    """
    data = load_financial_data(company)
    df = metrics_to_dataframe(data["metrics"])
    
    fig = px.line(df, x="year", y="revenue", 
                 title=f"Évolution des revenus de {company.capitalize()}",
                 labels={"revenue": "Revenus (en millions $)", "year": "Année"},
                 markers=True)
    
    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    # Ajouter des annotations pour les valeurs
    for i, row in df.iterrows():
        fig.add_annotation(
            x=row['year'],
            y=row['revenue'],
            text=f"${row['revenue']}M",
            showarrow=True,
            arrowhead=1,
            ax=0,
            ay=-30
        )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def create_profit_margins_chart(company):
    """
    Crée un graphique interactif pour les marges bénéficiaires.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        str: Le code HTML du graphique
    """
    data = load_financial_data(company)
    df = metrics_to_dataframe(data["ratios"])
    
    # Convertir les ratios en pourcentages
    if "net_margin" in df.columns:
        df["net_margin"] = df["net_margin"] * 100
    if "gross_margin" in df.columns:
        df["gross_margin"] = df["gross_margin"] * 100
    
    fig = go.Figure()
    
    if "gross_margin" in df.columns:
        fig.add_trace(go.Bar(
            x=df["year"],
            y=df["gross_margin"],
            name="Marge brute",
            marker_color='rgb(55, 83, 109)'
        ))
    
    if "net_margin" in df.columns:
        fig.add_trace(go.Bar(
            x=df["year"],
            y=df["net_margin"],
            name="Marge nette",
            marker_color='rgb(26, 118, 255)'
        ))
    
    fig.update_layout(
        title=f"Marges bénéficiaires de {company.capitalize()}",
        xaxis_title="Année",
        yaxis_title="Pourcentage (%)",
        barmode='group',
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def create_financial_ratios_chart(company):
    """
    Crée un graphique interactif pour les ratios financiers.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        str: Le code HTML du graphique
    """
    data = load_financial_data(company)
    df = metrics_to_dataframe(data["ratios"])
    
    # Sélectionner les ratios à afficher
    ratios_to_display = ["debt_ratio", "financial_autonomy", "roa", "roe"]
    available_ratios = [r for r in ratios_to_display if r in df.columns]
    
    if not available_ratios:
        # Si aucun des ratios souhaités n'est disponible, utiliser tous les ratios disponibles
        available_ratios = [col for col in df.columns if col != "year"]
    
    # Créer un graphique radar
    fig = go.Figure()
    
    for year in df["year"].unique():
        year_data = df[df["year"] == year]
        values = [year_data[ratio].values[0] if ratio in year_data else 0 for ratio in available_ratios]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=available_ratios,
            fill='toself',
            name=f'Année {year}'
        ))
    
    fig.update_layout(
        title=f"Ratios financiers de {company.capitalize()}",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max([df[r].max() if r in df.columns else 0 for r in available_ratios]) * 1.2]
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def create_comparative_chart(metric, companies=["tesla", "apple", "microsoft"]):
    """
    Crée un graphique comparatif pour une métrique spécifique entre plusieurs entreprises.
    
    Args:
        metric (str): La métrique à comparer (revenue, net_income, gross_margin, etc.)
        companies (list): Liste des entreprises à comparer
        
    Returns:
        str: Le code HTML du graphique
    """
    fig = go.Figure()
    
    for company in companies:
        data = load_financial_data(company)
        
        # Déterminer si la métrique est dans metrics ou ratios
        if metric in data["metrics"]:
            values = data["metrics"][metric]
        elif metric in data["ratios"]:
            values = data["ratios"][metric]
        else:
            continue
        
        years = list(values.keys())
        metric_values = list(values.values())
        
        fig.add_trace(go.Scatter(
            x=years,
            y=metric_values,
            mode='lines+markers',
            name=company.capitalize()
        ))
    
    # Déterminer le titre et l'étiquette de l'axe Y en fonction de la métrique
    metric_labels = {
        "revenue": ("Revenus", "Millions $"),
        "net_income": ("Revenu net", "Millions $"),
        "gross_profit": ("Bénéfice brut", "Millions $"),
        "net_margin": ("Marge nette", "%"),
        "gross_margin": ("Marge brute", "%"),
        "debt_ratio": ("Ratio d'endettement", "Ratio"),
        "roa": ("Rendement des actifs", "%"),
        "roe": ("Rendement des capitaux propres", "%")
    }
    
    title, y_label = metric_labels.get(metric, (metric.capitalize(), "Valeur"))
    
    fig.update_layout(
        title=f"Comparaison de {title} entre entreprises",
        xaxis_title="Année",
        yaxis_title=y_label,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def create_dashboard_charts(company):
    """
    Crée tous les graphiques pour le tableau de bord d'une entreprise.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        dict: Dictionnaire contenant les codes HTML des graphiques
    """
    return {
        "revenue_chart": create_revenue_chart(company),
        "margins_chart": create_profit_margins_chart(company),
        "ratios_chart": create_financial_ratios_chart(company),
        "comparative_revenue": create_comparative_chart("revenue", [company, "apple", "microsoft"]),
        "comparative_margin": create_comparative_chart("net_margin", [company, "apple", "microsoft"])
    } 