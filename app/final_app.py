from flask import Flask, render_template_string, request, redirect, url_for
import json
import os
import socket

app = Flask(__name__)

# Fonction pour charger les données financières
def load_financial_data(company):
    """Charge les données financières à partir d'un fichier JSON."""
    try:
        # Chemin vers le fichier de données
        file_path = f"data/results/{company}/metrics.json"
        
        # Vérifier si le fichier existe
        if not os.path.exists(file_path):
            print(f"Le fichier {file_path} n'existe pas.")
            # Retourner des données par défaut
            return {
                "revenue": {"2022": 81462, "2023": 94000, "2024": 96702},
                "net_income": {"2022": 12656, "2023": 11330, "2024": 10500},
                "gross_profit": {"2022": 20853, "2023": 21501, "2024": 22894},
                "total_assets": {"2022": 128142, "2023": 135000, "2024": 142000},
                "total_liabilities": {"2022": 54848, "2023": 58000, "2024": 62000}
            }
        
        # Charger les données depuis le fichier JSON
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        # Retourner des données par défaut en cas d'erreur
        return {
            "revenue": {"2022": 81462, "2023": 94000, "2024": 96702},
            "net_income": {"2022": 12656, "2023": 11330, "2024": 10500},
            "gross_profit": {"2022": 20853, "2023": 21501, "2024": 22894},
            "total_assets": {"2022": 128142, "2023": 135000, "2024": 142000},
            "total_liabilities": {"2022": 54848, "2023": 58000, "2024": 62000}
        }

# Fonction pour obtenir les indicateurs clés
def get_key_indicators(company):
    """Calcule les indicateurs clés à partir des données financières."""
    data = load_financial_data(company)
    
    # Années disponibles
    years = sorted(data.get("revenue", {}).keys())
    if not years:
        return {}
    
    latest_year = years[-1]
    previous_year = years[-2] if len(years) > 1 else latest_year
    
    # Calculer les indicateurs
    revenue = data.get("revenue", {}).get(latest_year, 0)
    revenue_prev = data.get("revenue", {}).get(previous_year, 0)
    revenue_growth = ((revenue - revenue_prev) / revenue_prev * 100) if revenue_prev else 0
    
    net_income = data.get("net_income", {}).get(latest_year, 0)
    net_margin = (net_income / revenue * 100) if revenue else 0
    
    gross_profit = data.get("gross_profit", {}).get(latest_year, 0)
    gross_margin = (gross_profit / revenue * 100) if revenue else 0
    
    total_assets = data.get("total_assets", {}).get(latest_year, 0)
    total_liabilities = data.get("total_liabilities", {}).get(latest_year, 0)
    debt_ratio = (total_liabilities / total_assets) if total_assets else 0
    
    return {
        "revenue": f"${revenue:,}",
        "revenue_growth": f"{revenue_growth:.1f}%",
        "net_margin": f"{net_margin:.1f}%",
        "gross_margin": f"{gross_margin:.1f}%",
        "debt_ratio": f"{debt_ratio:.2f}"
    }

# Route principale
@app.route('/')
def index():
    # Récupérer l'entreprise sélectionnée depuis les paramètres de requête
    company = request.args.get('company', 'tesla').lower()
    
    # Obtenir les indicateurs clés
    indicators = get_key_indicators(company)
    
    # Charger les données pour les graphiques
    data = load_financial_data(company)
    
    # Préparer les données pour les graphiques JavaScript
    years = sorted(data.get("revenue", {}).keys())
    revenue_data = [data.get("revenue", {}).get(year, 0) for year in years]
    net_income_data = [data.get("net_income", {}).get(year, 0) for year in years]
    
    # Calculer les marges pour chaque année
    net_margins = []
    gross_margins = []
    for year in years:
        revenue = data.get("revenue", {}).get(year, 0)
        if revenue > 0:
            net_income = data.get("net_income", {}).get(year, 0)
            gross_profit = data.get("gross_profit", {}).get(year, 0)
            net_margins.append((net_income / revenue) * 100)
            gross_margins.append((gross_profit / revenue) * 100)
        else:
            net_margins.append(0)
            gross_margins.append(0)
    
    # Calculer les ratios d'endettement
    debt_ratios = []
    for year in years:
        assets = data.get("total_assets", {}).get(year, 0)
        if assets > 0:
            liabilities = data.get("total_liabilities", {}).get(year, 0)
            debt_ratios.append((liabilities / assets) * 100)
        else:
            debt_ratios.append(0)
    
    # Créer le contenu HTML avec les graphiques
    content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Financier</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            
            .chart-container {
                height: 300px;
                margin-bottom: 30px;
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
                <a href="/?company={{ company }}" class="list-group-item list-group-item-action active">Tableau de bord</a>
                <a href="/metrics?company={{ company }}" class="list-group-item list-group-item-action">Métriques financières</a>
                <a href="/ratios?company={{ company }}" class="list-group-item list-group-item-action">Ratios financiers</a>
                <a href="/sec" class="list-group-item list-group-item-action">Recherche SEC</a>
            </div>
        </div>
        
        <div class="main-content">
            <h1 class="mb-4">Tableau de Bord Financier - {{ company.capitalize() }}</h1>
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Chiffre d'affaires</h5>
                            <p class="card-text display-6">{{ indicators.get('revenue', 'N/A') }}</p>
                            <p class="card-text text-muted">Croissance: {{ indicators.get('revenue_growth', 'N/A') }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Marge nette</h5>
                            <p class="card-text display-6">{{ indicators.get('net_margin', 'N/A') }}</p>
                            <p class="card-text text-muted">Marge brute: {{ indicators.get('gross_margin', 'N/A') }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Ratio d'endettement</h5>
                            <p class="card-text display-6">{{ indicators.get('debt_ratio', 'N/A') }}</p>
                            <p class="card-text text-muted">Dette / Actifs totaux</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title">Évolution du chiffre d'affaires</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="revenueChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title">Marges</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="marginsChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title">Ratio d'endettement</h5>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="debtChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Données pour les graphiques
            const years = JSON.parse('{{ years|tojson }}');
            const revenueData = JSON.parse('{{ revenue_data|tojson }}');
            const netIncomeData = JSON.parse('{{ net_income_data|tojson }}');
            const netMargins = JSON.parse('{{ net_margins|tojson }}');
            const grossMargins = JSON.parse('{{ gross_margins|tojson }}');
            const debtRatios = JSON.parse('{{ debt_ratios|tojson }}');
            
            // Graphique du chiffre d'affaires
            const revenueCtx = document.getElementById('revenueChart').getContext('2d');
            new Chart(revenueCtx, {
                type: 'bar',
                data: {
                    labels: years,
                    datasets: [
                        {
                            label: 'Chiffre d\'affaires',
                            data: revenueData,
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Résultat net',
                            data: netIncomeData,
                            backgroundColor: 'rgba(75, 192, 192, 0.5)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
            
            // Graphique des marges
            const marginsCtx = document.getElementById('marginsChart').getContext('2d');
            new Chart(marginsCtx, {
                type: 'line',
                data: {
                    labels: years,
                    datasets: [
                        {
                            label: 'Marge nette (%)',
                            data: netMargins,
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 2,
                            tension: 0.1
                        },
                        {
                            label: 'Marge brute (%)',
                            data: grossMargins,
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            borderColor: 'rgba(153, 102, 255, 1)',
                            borderWidth: 2,
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
            
            // Graphique du ratio d'endettement
            const debtCtx = document.getElementById('debtChart').getContext('2d');
            new Chart(debtCtx, {
                type: 'line',
                data: {
                    labels: years,
                    datasets: [
                        {
                            label: 'Ratio d\'endettement (%)',
                            data: debtRatios,
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgba(255, 159, 64, 1)',
                            borderWidth: 2,
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        </script>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Remplacer les variables dans le template
    return render_template_string(
        content, 
        company=company, 
        indicators=indicators,
        years=years,
        revenue_data=revenue_data,
        net_income_data=net_income_data,
        net_margins=net_margins,
        gross_margins=gross_margins,
        debt_ratios=debt_ratios
    )

# Route pour la redirection vers l'application SEC
@app.route('/sec')
def sec_search():
    return redirect('http://127.0.0.1:5004')

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
                <a href="/?company={{ company }}" class="list-group-item list-group-item-action">Tableau de bord</a>
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
                <a href="/?company={{ company }}" class="list-group-item list-group-item-action">Tableau de bord</a>
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
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    # Essayer différents ports
    port = 5002
    while is_port_in_use(port) and port < 5010:
        port += 1
    
    print(f"Démarrage de l'application sur le port {port}")
    app.run(debug=True, port=port)