from flask import Flask, render_template_string, request, jsonify
import plotly.graph_objects as go
import json
import os
# Importer le blueprint SEC - correction du chemin d'importation
try:
    from app.sec_search import sec_bp
except ImportError:
    # Si l'importation échoue, essayer un chemin relatif
    try:
        from sec_search import sec_bp
    except ImportError:
        print("AVERTISSEMENT: Impossible d'importer le module sec_search. La fonctionnalité de recherche SEC ne sera pas disponible.")
        # Créer un blueprint factice pour éviter les erreurs
        from flask import Blueprint
        sec_bp = Blueprint('sec', __name__)

app = Flask(__name__)
# Enregistrer le blueprint SEC
app.register_blueprint(sec_bp, url_prefix='/sec')

def load_financial_data(company):
    """
    Charge les données financières d'une entreprise à partir des fichiers JSON disponibles.
    
    Args:
        company (str): Le nom de l'entreprise (tesla, apple, microsoft)
        
    Returns:
        dict: Les données financières de l'entreprise
    """
    # Chemin principal pour les données
    file_path = f"data/results/{company}_financial_data.json"
    
    # Si le fichier existe, le charger
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de {file_path}: {e}")
    
    # Si le fichier n'existe pas ou s'il y a une erreur, retourner des données par défaut
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

def create_revenue_chart(company):
    """
    Crée un graphique interactif pour l'évolution des revenus.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        str: Le code HTML du graphique
    """
    data = load_financial_data(company)
    
    # Extraire les données de revenus
    years = list(data["metrics"]["revenue"].keys())
    revenue_values = list(data["metrics"]["revenue"].values())
    
    # Convertir les valeurs en nombres si elles sont des chaînes
    revenue_values = [float(val.replace(',', '')) if isinstance(val, str) else float(val) for val in revenue_values]
    
    # Créer le graphique
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=revenue_values,
        mode='lines+markers',
        name='Revenus',
        line=dict(color='royalblue', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title=f"Évolution des revenus de {company.capitalize()}",
        xaxis_title="Année",
        yaxis_title="Revenus (en millions $)",
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def create_margins_chart(company):
    """
    Crée un graphique interactif pour les marges bénéficiaires.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        str: Le code HTML du graphique
    """
    data = load_financial_data(company)
    
    # Extraire les données de marges
    years = list(data["ratios"]["net_margin"].keys())
    net_margin_values = list(data["ratios"]["net_margin"].values())
    gross_margin_values = list(data["ratios"]["gross_margin"].values())
    
    # Créer le graphique
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=years,
        y=gross_margin_values,
        name="Marge brute",
        marker_color='rgb(55, 83, 109)'
    ))
    
    fig.add_trace(go.Bar(
        x=years,
        y=net_margin_values,
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

def create_debt_chart(company):
    """
    Crée un graphique interactif pour le ratio d'endettement.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        str: Le code HTML du graphique
    """
    data = load_financial_data(company)
    
    # Extraire les données de ratio d'endettement
    years = list(data["ratios"]["debt_ratio"].keys())
    debt_values = list(data["ratios"]["debt_ratio"].values())
    
    # Créer le graphique
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=years,
        y=debt_values,
        mode='lines+markers',
        name='Ratio d\'endettement',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title=f"Évolution du ratio d'endettement de {company.capitalize()}",
        xaxis_title="Année",
        yaxis_title="Ratio d'endettement",
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def get_key_indicators(company):
    """
    Récupère les indicateurs clés pour l'affichage dans les cartes.
    
    Args:
        company (str): Le nom de l'entreprise
        
    Returns:
        dict: Les indicateurs clés avec leurs valeurs et tendances
    """
    data = load_financial_data(company)
    indicators = {}
    
    # Récupérer les années disponibles
    years = sorted(data["metrics"]["revenue"].keys(), reverse=True)
    latest_year = years[0] if years else None
    previous_year = years[1] if len(years) > 1 else None
    
    if latest_year:
        # Revenue
        revenue_value = data["metrics"]["revenue"][latest_year]
        indicators["revenue"] = {
            "value": revenue_value,
            "label": "Revenus",
            "format": "$"
        }
        
        # Calculer la tendance YoY pour le revenu
        if previous_year:
            try:
                current = float(revenue_value) if isinstance(revenue_value, (int, float)) else float(revenue_value.replace(",", ""))
                previous = float(data["metrics"]["revenue"][previous_year]) if isinstance(data["metrics"]["revenue"][previous_year], (int, float)) else float(data["metrics"]["revenue"][previous_year].replace(",", ""))
                if previous > 0:
                    yoy_change = ((current - previous) / previous) * 100
                    indicators["revenue"]["trend"] = yoy_change
                    indicators["revenue"]["trend_direction"] = "up" if yoy_change >= 0 else "down"
            except (ValueError, TypeError):
                pass
        
        # Net Profit
        net_income_value = data["metrics"]["net_income"][latest_year]
        indicators["net_profit"] = {
            "value": net_income_value,
            "label": "Bénéfice net",
            "format": "$"
        }
        
        # Calculer la tendance YoY pour le net income
        if previous_year:
            try:
                current = float(net_income_value) if isinstance(net_income_value, (int, float)) else float(net_income_value.replace(",", ""))
                previous = float(data["metrics"]["net_income"][previous_year]) if isinstance(data["metrics"]["net_income"][previous_year], (int, float)) else float(data["metrics"]["net_income"][previous_year].replace(",", ""))
                if previous > 0:
                    yoy_change = ((current - previous) / previous) * 100
                    indicators["net_profit"]["trend"] = yoy_change
                    indicators["net_profit"]["trend_direction"] = "up" if yoy_change >= 0 else "down"
            except (ValueError, TypeError):
                pass
        
        # Gross Margin
        gross_margin_value = data["ratios"]["gross_margin"][latest_year]
        indicators["gross_margin"] = {
            "value": gross_margin_value,
            "label": "Marge brute",
            "format": "%"
        }
        
        # Calculer la tendance YoY pour la marge brute
        if previous_year:
            try:
                current = float(gross_margin_value) if isinstance(gross_margin_value, (int, float)) else float(gross_margin_value.replace(",", ""))
                previous = float(data["ratios"]["gross_margin"][previous_year]) if isinstance(data["ratios"]["gross_margin"][previous_year], (int, float)) else float(data["ratios"]["gross_margin"][previous_year].replace(",", ""))
                if previous > 0:
                    yoy_change = current - previous
                    indicators["gross_margin"]["trend"] = yoy_change
                    indicators["gross_margin"]["trend_direction"] = "up" if yoy_change >= 0 else "down"
            except (ValueError, TypeError):
                pass
        
        # ROE (Return on Equity) si disponible
        if "roe" in data["ratios"] and latest_year in data["ratios"]["roe"]:
            roe_value = data["ratios"]["roe"][latest_year]
            indicators["roe"] = {
                "value": roe_value,
                "label": "ROE",
                "format": "%"
            }
            
            # Calculer la tendance YoY pour le ROE
            if previous_year and previous_year in data["ratios"]["roe"]:
                try:
                    current = float(roe_value) if isinstance(roe_value, (int, float)) else float(roe_value.replace(",", ""))
                    previous = float(data["ratios"]["roe"][previous_year]) if isinstance(data["ratios"]["roe"][previous_year], (int, float)) else float(data["ratios"]["roe"][previous_year].replace(",", ""))
                    if previous > 0:
                        yoy_change = current - previous
                        indicators["roe"]["trend"] = yoy_change
                        indicators["roe"]["trend_direction"] = "up" if yoy_change >= 0 else "down"
                except (ValueError, TypeError):
                    pass
    
    return indicators

@app.route('/')
def index():
    """Page d'accueil avec sélecteur d'entreprise et graphiques interactifs."""
    # Récupérer l'entreprise sélectionnée (par défaut: tesla)
    company = request.args.get('company', 'tesla').lower()
    
    # Générer les graphiques
    revenue_chart = create_revenue_chart(company)
    margins_chart = create_margins_chart(company)
    debt_chart = create_debt_chart(company)
    
    # Récupérer les indicateurs clés
    indicators = get_key_indicators(company)
    
    # Rendre le template avec les graphiques
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tableau de bord financier interactif</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
                color: #212529;
                margin: 0;
                padding: 0;
                display: flex;
                min-height: 100vh;
            }
            
            /* App container */
            .app-container {
                display: flex;
                width: 100%;
                min-height: 100vh;
            }
            
            /* Sidebar */
            .sidebar {
                width: 250px;
                background-color: #343a40;
                color: white;
                padding: 20px 0;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            }
            
            .sidebar-header {
                padding: 0 20px 20px;
                border-bottom: 1px solid #495057;
                margin-bottom: 20px;
            }
            
            .sidebar-header h3 {
                margin: 0;
                font-size: 1.5rem;
            }
            
            .sidebar-menu {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .sidebar-menu li {
                margin-bottom: 5px;
            }
            
            .sidebar-menu a {
                display: block;
                padding: 10px 20px;
                color: #adb5bd;
                text-decoration: none;
                transition: all 0.3s;
            }
            
            .sidebar-menu a:hover, .sidebar-menu a.active {
                color: white;
                background-color: #495057;
            }
            
            /* Main content */
            .main-content {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                overflow-x: hidden;
            }
            
            header {
                background-color: white;
                padding: 15px 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            header h1 {
                margin: 0;
                font-size: 1.8rem;
                color: #343a40;
            }
            
            /* Indicators row */
            .indicators-row {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                padding: 20px;
            }
            
            .indicator-card {
                flex: 1;
                min-width: 200px;
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .indicator-card h3 {
                margin-top: 0;
                color: #7f8c8d;
                font-size: 14px;
                text-transform: uppercase;
            }
            
            .indicator-value {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }
            
            .indicator-trend {
                font-size: 14px;
            }
            
            .trend-up {
                color: #2ecc71;
            }
            
            .trend-down {
                color: #e74c3c;
            }
            
            /* Content area */
            .content-area {
                flex-grow: 1;
                padding: 0 20px 20px;
                overflow-y: auto;
            }
            
            .content-card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            
            /* Company selector */
            .company-selector {
                margin-bottom: 20px;
            }
            
            select, button {
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            
            button {
                background-color: #3498db;
                color: white;
                border: none;
                cursor: pointer;
            }
            
            button:hover {
                background-color: #2980b9;
            }
            
            .chart-container {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                padding: 20px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Left Sidebar Navigation -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <h3>Finance Dashboard</h3>
                </div>
                <ul class="sidebar-menu">
                    <li><a href="/" class="active">Dashboard</a></li>
                    <li><a href="/sec/search">Recherche SEC</a></li>
                    <li><a href="#">Rapports</a></li>
                    <li><a href="#">Comparaisons</a></li>
                    <li><a href="#">Entreprises</a></li>
                </ul>
                
                <div class="p-3">
                    <h5>Sélectionner une entreprise</h5>
                    <form action="/" method="get">
                        <select name="company" class="form-select mb-3" onchange="this.form.submit()">
                            <option value="tesla" {% if company == 'tesla' %}selected{% endif %}>Tesla</option>
                            <option value="apple" {% if company == 'apple' %}selected{% endif %}>Apple</option>
                            <option value="microsoft" {% if company == 'microsoft' %}selected{% endif %}>Microsoft</option>
                        </select>
                    </form>
                </div>
            </div>
            
            <!-- Main Content Area -->
            <div class="main-content">
                <header>
                    <h1>Financial Analysis Dashboard</h1>
                </header>
                
                <!-- Key Indicators -->
                <div class="indicators-row">
                    {% for key, indicator in indicators.items() %}
                    <div class="indicator-card">
                        <h3>{{ indicator.label }}</h3>
                        <div class="indicator-value">
                            {% if indicator.format == '$' %}${% endif %}{{ indicator.value }}{% if indicator.format == '%' %}%{% endif %}
                        </div>
                        {% if indicator.get('trend') is not none %}
                        <div class="indicator-trend {% if indicator.trend_direction == 'up' %}trend-up{% else %}trend-down{% endif %}">
                            {% if indicator.trend_direction == 'up' %}↑{% else %}↓{% endif %}
                            {{ "%.1f"|format(indicator.trend|float) }}{% if indicator.format == '%' %}pts{% else %}%{% endif %}
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                
                <!-- Charts -->
                <div class="content-area">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="chart-container">
                                <h2>Évolution des revenus</h2>
                                {{ revenue_chart|safe }}
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="chart-container">
                                <h2>Marges bénéficiaires</h2>
                                {{ margins_chart|safe }}
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-12">
                            <div class="chart-container">
                                <h2>Ratio d'endettement</h2>
                                {{ debt_chart|safe }}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """, revenue_chart=revenue_chart, margins_chart=margins_chart, debt_chart=debt_chart, 
       indicators=indicators, company=company)

if __name__ == '__main__':
    # Exécuter l'application sur le port 5002 pour éviter les conflits
    app.run(debug=True, port=5002) 