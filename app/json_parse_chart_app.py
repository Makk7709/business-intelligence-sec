from flask import Flask, render_template_string, request
import json
import os
import socket

app = Flask(__name__)

def find_available_port(start_port=5000, max_attempts=100):
    """Trouve un port disponible en commençant par start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return start_port  # Retourne le port de départ si aucun port n'est disponible

@app.route('/')
def index():
    # Données statiques pour le graphique
    years = ["2022", "2023", "2024"]
    revenue_data = [1000, 1500, 2000]
    net_income_data = [200, 300, 400]
    
    # HTML avec Chart.js intégré
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Graphique Simple avec JSON.parse</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="text-center mb-4">Graphique de Test avec JSON.parse</h1>
            
            <div class="row">
                <div class="col-md-8 offset-md-2">
                    <div class="card">
                        <div class="card-header">
                            Revenus et Bénéfices
                        </div>
                        <div class="card-body">
                            <canvas id="revenueChart" width="400" height="200"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Données pour le graphique avec JSON.parse
            const years = JSON.parse('{{ years|tojson }}');
            const revenueData = JSON.parse('{{ revenue_data|tojson }}');
            const netIncomeData = JSON.parse('{{ net_income_data|tojson }}');
            
            // Création du graphique
            const ctx = document.getElementById('revenueChart').getContext('2d');
            const revenueChart = new Chart(ctx, {
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
                            label: 'Bénéfice Net',
                            data: netIncomeData,
                            backgroundColor: 'rgba(75, 192, 192, 0.5)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value + ' €';
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
    
    return render_template_string(html_content, 
                                 years=years,
                                 revenue_data=revenue_data,
                                 net_income_data=net_income_data)

if __name__ == '__main__':
    port = find_available_port(5020)
    print(f"Démarrage de l'application sur le port {port}")
    app.run(debug=True, port=port) 