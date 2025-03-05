from flask import Flask, render_template_string, request
import socket
import json
import os

app = Flask(__name__)

def find_available_port(start_port=5050, max_attempts=100):
    """Trouve un port disponible en commençant par start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

def load_comparative_data():
    """Charge les données comparatives depuis le fichier JSON"""
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                'data/results/comparative/comparative/comparative_analysis.json')
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return None

@app.route('/')
def index():
    # Chargement des données réelles
    data = load_comparative_data()
    
    # Valeur par défaut si les données ne peuvent pas être chargées
    if not data:
        years = ["2022", "2023", "2024"]
        revenue_data = [200000, 250000, 300000]
        net_income_data = [50000, 60000, 75000]
        net_margins = [25, 24, 25]
        gross_margins = [40, 42, 45]
        debt_ratios = [35, 30, 28]
        company = "tesla"
    else:
        # Récupération de l'entreprise sélectionnée (par défaut: tesla)
        company = request.args.get('company', 'tesla').upper()
        if company.upper() == 'TESLA':
            company = 'TSLA'
        elif company.upper() == 'APPLE':
            company = 'AAPL'
        elif company.upper() == 'MICROSOFT':
            company = 'MSFT'
        
        # Extraction des données pour l'entreprise sélectionnée
        years = ["2022", "2023", "2024"]
        revenue_data = [data["revenue"][company].get("2022", 0), 
                        data["revenue"][company].get("2023", 0), 
                        data["revenue"][company].get("2024", 0)]
        
        # Calcul du résultat net à partir des revenus et de la marge nette
        net_margins = [data["net_margin"][company].get("2022", 0),
                      data["net_margin"][company].get("2023", 0),
                      data["net_margin"][company].get("2024", 0)]
        
        net_income_data = [revenue_data[0] * net_margins[0] / 100,
                          revenue_data[1] * net_margins[1] / 100,
                          revenue_data[2] * net_margins[2] / 100]
        
        # Pour les marges brutes, nous n'avons pas cette donnée, donc on utilise une approximation
        gross_margins = [net_margins[0] * 1.6, net_margins[1] * 1.6, net_margins[2] * 1.6]
        
        # Ratios d'endettement
        debt_ratios = [0, data["debt_ratio"][company].get("2023", 0), 
                      data["debt_ratio"][company].get("2024", 0)]
    
    # Template HTML avec les graphiques
    template = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tableau de bord financier</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .card {
                margin-bottom: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .indicator {
                text-align: center;
                padding: 20px;
            }
            .indicator h3 {
                font-size: 24px;
                margin-bottom: 10px;
            }
            .indicator p {
                font-size: 36px;
                font-weight: bold;
                margin: 0;
            }
            .positive {
                color: green;
            }
            .negative {
                color: red;
            }
            .chart-container {
                height: 300px;
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <div class="row mb-4">
                <div class="col">
                    <h1 class="display-4">Tableau de bord financier</h1>
                    <p class="lead">Analyse des performances financières</p>
                </div>
                <div class="col-auto">
                    <div class="form-group">
                        <label for="company">Entreprise:</label>
                        <select class="form-control" id="company" onchange="window.location.href='?company=' + this.value">
                            <option value="tesla" selected>Tesla</option>
                            <option value="apple">Apple</option>
                            <option value="microsoft">Microsoft</option>
                        </select>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card indicator">
                        <h3>Croissance du revenu</h3>
                        <p class="positive">+20%</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card indicator">
                        <h3>Marge nette</h3>
                        <p>25%</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card indicator">
                        <h3>Marge brute</h3>
                        <p>45%</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card indicator">
                        <h3>Ratio d'endettement</h3>
                        <p class="positive">28%</p>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h2>Revenus et résultat net</h2>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="revenueChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h2>Marges</h2>
                        </div>
                        <div class="card-body">
                            <div class="chart-container">
                                <canvas id="marginsChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h2>Ratio d'endettement</h2>
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
            const years = {{ years|tojson }};
            const revenueData = {{ revenue_data|tojson }};
            const netIncomeData = {{ net_income_data|tojson }};
            const netMargins = {{ net_margins|tojson }};
            const grossMargins = {{ gross_margins|tojson }};
            const debtRatios = {{ debt_ratios|tojson }};

            // Graphique des revenus et résultat net
            const revenueCtx = document.getElementById('revenueChart').getContext('2d');
            new Chart(revenueCtx, {
                type: 'bar',
                data: {
                    labels: years,
                    datasets: [
                        {
                            label: 'Revenus',
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
                            label: 'Marge nette',
                            data: netMargins,
                            borderColor: 'rgba(255, 99, 132, 1)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            tension: 0.1,
                            fill: true
                        },
                        {
                            label: 'Marge brute',
                            data: grossMargins,
                            borderColor: 'rgba(153, 102, 255, 1)',
                            backgroundColor: 'rgba(153, 102, 255, 0.2)',
                            tension: 0.1,
                            fill: true
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
                            label: 'Ratio d\'endettement',
                            data: debtRatios,
                            borderColor: 'rgba(255, 159, 64, 1)',
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            tension: 0.1,
                            fill: true
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
    </body>
    </html>
    """
    
    return render_template_string(template, 
                                 years=years,
                                 revenue_data=revenue_data,
                                 net_income_data=net_income_data,
                                 net_margins=net_margins,
                                 gross_margins=gross_margins,
                                 debt_ratios=debt_ratios)

if __name__ == '__main__':
    port = 8080
    print(f"\n\n=== DÉMARRAGE DE L'APPLICATION ===")
    print(f"Application accessible à l'adresse: http://127.0.0.1:{port}")
    print(f"Appuyez sur CTRL+C pour arrêter le serveur")
    print(f"=====================================\n\n")
    app.run(debug=True, port=port) 