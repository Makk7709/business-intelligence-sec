from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
import sys

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

# Fonction pour charger les données financières sans pandas
def load_financial_data(company):
    """Charge les données financières à partir des fichiers JSON."""
    try:
        # Chemin vers le fichier de données
        file_path = f"data/results/{company}/metrics.json"
        
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            print(f"Le fichier {file_path} n'existe pas.")
            return {
                "revenue": {"2022": 100, "2023": 120, "2024": 150},
                "net_income": {"2022": 10, "2023": 15, "2024": 20},
                "gross_margin": {"2022": 30, "2023": 35, "2024": 40}
            }
        
        # Charger les données depuis le fichier JSON
        with open(file_path, "r") as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        # Retourner des données par défaut en cas d'erreur
        return {
            "revenue": {"2022": 100, "2023": 120, "2024": 150},
            "net_income": {"2022": 10, "2023": 15, "2024": 20},
            "gross_margin": {"2022": 30, "2023": 35, "2024": 40}
        }

# Fonction pour obtenir les indicateurs clés
def get_key_indicators(company):
    """Récupère les indicateurs clés pour une entreprise."""
    metrics = load_financial_data(company)
    
    # Extraire les années disponibles
    years = []
    if "revenue" in metrics:
        years = list(metrics["revenue"].keys())
    
    # Si aucune année n'est disponible, utiliser des valeurs par défaut
    if not years:
        years = ["2022", "2023", "2024"]
    
    # Trier les années
    years.sort()
    
    # Année la plus récente
    latest_year = years[-1] if years else "2024"
    
    # Calculer les indicateurs
    indicators = {}
    
    # Revenu
    if "revenue" in metrics:
        indicators["revenue"] = metrics["revenue"].get(latest_year, 0)
        
        # Croissance du revenu
        if len(years) > 1:
            previous_year = years[-2]
            current_revenue = metrics["revenue"].get(latest_year, 0)
            previous_revenue = metrics["revenue"].get(previous_year, 0)
            
            if previous_revenue > 0:
                revenue_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
                indicators["revenue_growth"] = round(revenue_growth, 2)
            else:
                indicators["revenue_growth"] = 0
        else:
            indicators["revenue_growth"] = 0
    else:
        indicators["revenue"] = 0
        indicators["revenue_growth"] = 0
    
    # Marge nette
    if "net_income" in metrics and "revenue" in metrics:
        net_income = metrics["net_income"].get(latest_year, 0)
        revenue = metrics["revenue"].get(latest_year, 0)
        
        if revenue > 0:
            net_margin = (net_income / revenue) * 100
            indicators["net_margin"] = round(net_margin, 2)
        else:
            indicators["net_margin"] = 0
    else:
        indicators["net_margin"] = 0
    
    # Marge brute
    if "gross_margin" in metrics:
        indicators["gross_margin"] = metrics["gross_margin"].get(latest_year, 0)
    else:
        indicators["gross_margin"] = 0
    
    return indicators

# Page d'accueil
@app.route('/')
def index():
    # Récupérer l'entreprise sélectionnée depuis les paramètres de requête
    company = request.args.get('company', 'tesla').lower()
    
    # Charger les données financières
    metrics = load_financial_data(company)
    
    # Obtenir les indicateurs clés
    indicators = get_key_indicators(company)
    
    # Créer le contenu HTML
    content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analyse Financière</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                min-height: 100vh;
            }
            
            .sidebar {
                width: 250px;
                background-color: #f8f9fa;
                padding: 20px;
                border-right: 1px solid #dee2e6;
            }
            
            .main-content {
                flex: 1;
                padding: 20px;
            }
            
            .card {
                margin-bottom: 20px;
            }
            
            .indicator {
                text-align: center;
                padding: 15px;
                border-radius: 5px;
                background-color: #f8f9fa;
                margin-bottom: 15px;
            }
            
            .indicator h3 {
                margin: 0;
                font-size: 24px;
                color: #0d6efd;
            }
            
            .indicator p {
                margin: 5px 0 0;
                font-size: 14px;
                color: #6c757d;
            }
            
            .chart-container {
                height: 300px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3 class="mb-4">Business Intelligence</h3>
            
            <div class="mb-4">
                <label for="company" class="form-label">Sélectionner une entreprise:</label>
                <form action="/" method="get">
                    <select name="company" id="company" class="form-select mb-2" onchange="this.form.submit()">
                        <option value="tesla" {{ 'selected' if company == 'tesla' else '' }}>Tesla</option>
                        <option value="apple" {{ 'selected' if company == 'apple' else '' }}>Apple</option>
                        <option value="microsoft" {{ 'selected' if company == 'microsoft' else '' }}>Microsoft</option>
                    </select>
                </form>
            </div>
            
            <div class="list-group mb-4">
                <a href="/" class="list-group-item list-group-item-action active">Tableau de bord</a>
                <a href="/metrics?company={{ company }}" class="list-group-item list-group-item-action">Métriques financières</a>
                <a href="/ratios?company={{ company }}" class="list-group-item list-group-item-action">Ratios financiers</a>
                <a href="/sec" class="list-group-item list-group-item-action">Recherche SEC</a>
            </div>
        </div>
        
        <div class="main-content">
            <h1 class="mb-4">Tableau de bord financier - {{ company.capitalize() }}</h1>
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="indicator">
                        <h3>${{ '{:,.0f}'.format(indicators['revenue']) }}M</h3>
                        <p>Revenu ({{ '{:+.2f}'.format(indicators['revenue_growth']) }}%)</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="indicator">
                        <h3>{{ '{:.2f}'.format(indicators['net_margin']) }}%</h3>
                        <p>Marge nette</p>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="indicator">
                        <h3>{{ '{:.2f}'.format(indicators['gross_margin']) }}%</h3>
                        <p>Marge brute</p>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title">Revenus par année</h5>
                        </div>
                        <div class="card-body">
                            <p class="text-center">Pour voir les graphiques interactifs, veuillez utiliser l'application SEC standalone.</p>
                            <p class="text-center">
                                <a href="/sec" class="btn btn-primary">Accéder à la recherche SEC</a>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Remplacer les variables dans le template
    return render_template_string(content, company=company)

# Route pour la recherche SEC
@app.route('/sec')
def sec_search():
    return redirect('http://127.0.0.1:5003')

# Route pour les métriques financières
@app.route('/metrics')
def metrics():
    # Récupérer l'entreprise sélectionnée depuis les paramètres de requête
    company = request.args.get('company', 'tesla').lower()
    
    # Charger les données financières
    metrics_data = load_financial_data(company)
    
    # Créer le contenu HTML
    content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Métriques Financières</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                min-height: 100vh;
            }
            
            .sidebar {
                width: 250px;
                background-color: #f8f9fa;
                padding: 20px;
                border-right: 1px solid #dee2e6;
            }
            
            .main-content {
                flex: 1;
                padding: 20px;
            }
            
            .card {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3 class="mb-4">Business Intelligence</h3>
            
            <div class="mb-4">
                <label for="company" class="form-label">Sélectionner une entreprise:</label>
                <form action="/metrics" method="get">
                    <select name="company" id="company" class="form-select mb-2" onchange="this.form.submit()">
                        <option value="tesla" {{ 'selected' if company == 'tesla' else '' }}>Tesla</option>
                        <option value="apple" {{ 'selected' if company == 'apple' else '' }}>Apple</option>
                        <option value="microsoft" {{ 'selected' if company == 'microsoft' else '' }}>Microsoft</option>
                    </select>
                </form>
            </div>
            
            <div class="list-group mb-4">
                <a href="/" class="list-group-item list-group-item-action">Tableau de bord</a>
                <a href="/metrics?company={{ company }}" class="list-group-item list-group-item-action active">Métriques financières</a>
                <a href="/ratios?company={{ company }}" class="list-group-item list-group-item-action">Ratios financiers</a>
                <a href="/sec" class="list-group-item list-group-item-action">Recherche SEC</a>
            </div>
        </div>
        
        <div class="main-content">
            <h1 class="mb-4">Métriques Financières - {{ company.capitalize() }}</h1>
            
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title">Métriques par année</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Métrique</th>
                                    {% for year in metrics_data.get('revenue', {}).keys()|sort %}
                                    <th>{{ year }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for metric, values in metrics_data.items() %}
                                <tr>
                                    <td>{{ metric }}</td>
                                    {% for year in metrics_data.get('revenue', {}).keys()|sort %}
                                    <td>{{ values.get(year, 'N/A') }}</td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Remplacer les variables dans le template
    return render_template_string(content, company=company, metrics_data=metrics_data)

# Route pour les ratios financiers
@app.route('/ratios')
def ratios():
    # Récupérer l'entreprise sélectionnée depuis les paramètres de requête
    company = request.args.get('company', 'tesla').lower()
    
    # Charger les données financières
    try:
        # Chemin vers le fichier de données
        file_path = f"data/results/{company}/ratios.json"
        
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            print(f"Le fichier {file_path} n'existe pas.")
            ratios_data = {
                "net_margin": {"2022": 10, "2023": 12, "2024": 15},
                "gross_margin": {"2022": 30, "2023": 32, "2024": 35},
                "debt_to_assets": {"2022": 0.4, "2023": 0.38, "2024": 0.35}
            }
        else:
            # Charger les données depuis le fichier JSON
            with open(file_path, "r") as f:
                ratios_data = json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        # Retourner des données par défaut en cas d'erreur
        ratios_data = {
            "net_margin": {"2022": 10, "2023": 12, "2024": 15},
            "gross_margin": {"2022": 30, "2023": 32, "2024": 35},
            "debt_to_assets": {"2022": 0.4, "2023": 0.38, "2024": 0.35}
        }
    
    # Créer le contenu HTML
    content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ratios Financiers</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                min-height: 100vh;
            }
            
            .sidebar {
                width: 250px;
                background-color: #f8f9fa;
                padding: 20px;
                border-right: 1px solid #dee2e6;
            }
            
            .main-content {
                flex: 1;
                padding: 20px;
            }
            
            .card {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h3 class="mb-4">Business Intelligence</h3>
            
            <div class="mb-4">
                <label for="company" class="form-label">Sélectionner une entreprise:</label>
                <form action="/ratios" method="get">
                    <select name="company" id="company" class="form-select mb-2" onchange="this.form.submit()">
                        <option value="tesla" {{ 'selected' if company == 'tesla' else '' }}>Tesla</option>
                        <option value="apple" {{ 'selected' if company == 'apple' else '' }}>Apple</option>
                        <option value="microsoft" {{ 'selected' if company == 'microsoft' else '' }}>Microsoft</option>
                    </select>
                </form>
            </div>
            
            <div class="list-group mb-4">
                <a href="/" class="list-group-item list-group-item-action">Tableau de bord</a>
                <a href="/metrics?company={{ company }}" class="list-group-item list-group-item-action">Métriques financières</a>
                <a href="/ratios?company={{ company }}" class="list-group-item list-group-item-action active">Ratios financiers</a>
                <a href="/sec" class="list-group-item list-group-item-action">Recherche SEC</a>
            </div>
        </div>
        
        <div class="main-content">
            <h1 class="mb-4">Ratios Financiers - {{ company.capitalize() }}</h1>
            
            <div class="card">
                <div class="card-header">
                    <h5 class="card-title">Ratios par année</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Ratio</th>
                                    {% for year in ratios_data.get('net_margin', {}).keys()|sort %}
                                    <th>{{ year }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for ratio, values in ratios_data.items() %}
                                <tr>
                                    <td>{{ ratio }}</td>
                                    {% for year in ratios_data.get('net_margin', {}).keys()|sort %}
                                    <td>{{ values.get(year, 'N/A') }}</td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Remplacer les variables dans le template
    return render_template_string(content, company=company, ratios_data=ratios_data)

if __name__ == '__main__':
    # Vérifier si le port est déjà utilisé
    import socket
    
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    # Essayer différents ports
    port = 5002
    while is_port_in_use(port) and port < 5010:
        port += 1
    
    print(f"Démarrage de l'application sur le port {port}")
    app.run(debug=True, port=port) 