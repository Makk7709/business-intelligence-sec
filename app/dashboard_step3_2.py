from flask import Flask, render_template_string, request, jsonify
import json
import random
from datetime import datetime, timedelta

# Créer l'application Flask
app = Flask(__name__)

# Générer des données aléatoires pour le graphique
def generate_chart_data():
    # Générer des dates pour les 30 derniers jours
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
    
    # Générer des valeurs aléatoires pour AAPL
    aapl_data = [random.uniform(170, 190) for _ in range(31)]
    
    # Générer des valeurs aléatoires pour MSFT
    msft_data = [random.uniform(350, 380) for _ in range(31)]
    
    # Générer des valeurs aléatoires pour GOOGL
    googl_data = [random.uniform(130, 150) for _ in range(31)]
    
    return {
        "dates": dates,
        "datasets": [
            {
                "label": "AAPL",
                "data": aapl_data,
                "borderColor": "#e74c3c",
                "backgroundColor": "rgba(231, 76, 60, 0.1)"
            },
            {
                "label": "MSFT",
                "data": msft_data,
                "borderColor": "#3498db",
                "backgroundColor": "rgba(52, 152, 219, 0.1)"
            },
            {
                "label": "GOOGL",
                "data": googl_data,
                "borderColor": "#2ecc71",
                "backgroundColor": "rgba(46, 204, 113, 0.1)"
            }
        ]
    }

# Template HTML intégré
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Dashboard financier pour l'analyse des données boursières">
    <title>Finance Dashboard</title>
    
    <!-- Chargement des CSS depuis CDN pour éviter les fichiers locaux lourds -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    
    <!-- CSS personnalisé minimal -->
    <style>
        /* Variables CSS pour la cohérence des couleurs */
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --background-color: #f8f9fa;
            --card-background: #ffffff;
            --text-color: #333333;
            --text-light: #6c757d;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            padding-bottom: 2rem;
        }
        
        .navbar-brand {
            font-weight: 600;
        }
        
        .card {
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            border: none;
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            background-color: var(--primary-color);
            color: white;
            border-radius: 0.5rem 0.5rem 0 0 !important;
            padding: 0.75rem 1.25rem;
        }
        
        .btn-primary {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }
        
        .btn-primary:hover {
            background-color: #2980b9;
            border-color: #2980b9;
        }
        
        .dashboard-card {
            text-align: center;
            padding: 1.5rem;
        }
        
        .dashboard-card .icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .dashboard-card .value {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .dashboard-card .label {
            font-size: 1rem;
            color: var(--text-light);
        }
        
        .positive {
            color: var(--success-color);
        }
        
        .negative {
            color: var(--danger-color);
        }
        
        .neutral {
            color: var(--secondary-color);
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
        }
        
        /* Styles spécifiques pour mobile */
        @media (max-width: 767.98px) {
            .container {
                padding-left: 10px;
                padding-right: 10px;
            }
            
            h1 {
                font-size: 1.75rem;
            }
            
            .card-body {
                padding: 1rem;
            }
            
            .dashboard-card .icon {
                font-size: 2rem;
            }
            
            .dashboard-card .value {
                font-size: 1.5rem;
            }
            
            .chart-container {
                height: 250px;
            }
        }
    </style>
</head>
<body>
    <!-- Barre de navigation responsive -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="#">Finance Dashboard</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="#">Accueil</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#dashboard">Tableau de bord</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#charts">Graphiques</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#compare">Comparaison</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#search">Recherche</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#index">Indexation</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Contenu principal -->
    <div class="container">
        <!-- En-tête -->
        <div class="row mb-4">
            <div class="col-12">
                <h1 class="text-center">Analyse Financière Vectorielle</h1>
                <p class="text-center text-muted">Recherchez et indexez des données financières avec la puissance des vecteurs</p>
            </div>
        </div>
        
        <!-- Tableau de bord avec indicateurs clés -->
        <div class="row mb-4" id="dashboard">
            <div class="col-12">
                <h2 class="h4 mb-3">Tableau de bord</h2>
            </div>
            
            <div class="col-md-3 col-sm-6">
                <div class="card dashboard-card">
                    <div class="icon positive">
                        <i class="bi bi-graph-up"></i>
                    </div>
                    <div class="value positive">+12.5%</div>
                    <div class="label">Performance du marché</div>
                </div>
            </div>
            
            <div class="col-md-3 col-sm-6">
                <div class="card dashboard-card">
                    <div class="icon neutral">
                        <i class="bi bi-search"></i>
                    </div>
                    <div class="value">1,245</div>
                    <div class="label">Titres indexés</div>
                </div>
            </div>
            
            <div class="col-md-3 col-sm-6">
                <div class="card dashboard-card">
                    <div class="icon negative">
                        <i class="bi bi-activity"></i>
                    </div>
                    <div class="value negative">-3.2%</div>
                    <div class="label">Volatilité</div>
                </div>
            </div>
            
            <div class="col-md-3 col-sm-6">
                <div class="card dashboard-card">
                    <div class="icon neutral">
                        <i class="bi bi-clock"></i>
                    </div>
                    <div class="value">24h</div>
                    <div class="label">Dernière mise à jour</div>
                </div>
            </div>
        </div>
        
        <!-- Section des graphiques -->
        <div class="row mb-4" id="charts">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h2 class="card-title h5 mb-0">Évolution des cours</h2>
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-sm btn-outline-light" onclick="updateChartPeriod('1m')">1M</button>
                            <button type="button" class="btn btn-sm btn-outline-light" onclick="updateChartPeriod('3m')">3M</button>
                            <button type="button" class="btn btn-sm btn-outline-light" onclick="updateChartPeriod('1y')">1A</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="stockChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Section de comparaison -->
        <div class="row mb-4" id="compare">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title h5 mb-0">Comparaison de titres</h2>
                    </div>
                    <div class="card-body">
                        <p>Section de comparaison en cours de développement...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Section de recherche -->
        <div class="row mb-4" id="search">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title h5 mb-0">Rechercher des titres similaires</h2>
                    </div>
                    <div class="card-body">
                        <form id="searchForm">
                            <div class="mb-3">
                                <label for="symbol" class="form-label">Symbole boursier</label>
                                <input type="text" class="form-control" id="symbol" placeholder="ex: AAPL" required>
                                <div class="form-text">Entrez le symbole d'une action cotée en bourse</div>
                            </div>
                            <div class="mb-3">
                                <label for="searchType" class="form-label">Type de recherche</label>
                                <select class="form-select" id="searchType">
                                    <option value="time_series">Séries temporelles</option>
                                    <option value="overview">Aperçu de l'entreprise</option>
                                </select>
                            </div>
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-search me-1"></i> Rechercher
                            </button>
                        </form>
                        <div class="mt-4" id="searchResult"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Section d'indexation -->
        <div class="row" id="index">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title h5 mb-0">Indexer un nouveau titre</h2>
                    </div>
                    <div class="card-body">
                        <form id="indexForm">
                            <div class="mb-3">
                                <label for="indexSymbol" class="form-label">Symbole boursier</label>
                                <input type="text" class="form-control" id="indexSymbol" placeholder="ex: MSFT" required>
                                <div class="form-text">Entrez le symbole d'une action à indexer</div>
                            </div>
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-plus-circle me-1"></i> Indexer
                            </button>
                        </form>
                        <div class="mt-4" id="indexResult"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-white mt-5 py-3">
        <div class="container text-center">
            <p class="mb-0">© 2024 Finance Dashboard. Tous droits réservés.</p>
        </div>
    </footer>

    <!-- Scripts JS depuis CDN -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <!-- Script personnalisé -->
    <script>
        // Données du graphique
        const chartData = {{ chart_data|safe }};
        let stockChart;
        
        // Attendre que le DOM soit chargé
        document.addEventListener('DOMContentLoaded', function() {
            // Initialiser le graphique
            initChart();
            
            // Gestionnaire pour le formulaire de recherche
            document.getElementById('searchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const symbol = document.getElementById('symbol').value;
                const searchType = document.getElementById('searchType').value;
                
                const resultDiv = document.getElementById('searchResult');
                resultDiv.innerHTML = '<div class="alert alert-info"><i class="bi bi-hourglass-split me-2"></i>Recherche en cours...</div>';
                
                try {
                    const response = await fetch('/api/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            symbol: symbol,
                            search_type: searchType
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Afficher les résultats de manière plus élégante
                    let resultsHtml = `
                        <div class="alert alert-success"><i class="bi bi-check-circle me-2"></i>Recherche réussie pour ${symbol}</div>
                        <h3 class="h5 mt-3">Résultats similaires</h3>
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>Symbole</th>
                                        <th>Nom</th>
                                        <th>Secteur</th>
                                        <th>Similarité</th>
                                    </tr>
                                </thead>
                                <tbody>
                    `;
                    
                    data.results.forEach(stock => {
                        resultsHtml += `
                            <tr>
                                <td><strong>${stock.symbol}</strong></td>
                                <td>${stock.name}</td>
                                <td>${stock.sector}</td>
                                <td>${(stock.similarity * 100).toFixed(1)}%</td>
                            </tr>
                        `;
                    });
                    
                    resultsHtml += `
                                </tbody>
                            </table>
                        </div>
                    `;
                    
                    resultDiv.innerHTML = resultsHtml;
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle me-2"></i><strong>Erreur:</strong> ${error.message}
                        </div>
                    `;
                }
            });
            
            // Gestionnaire pour le formulaire d'indexation
            document.getElementById('indexForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const symbol = document.getElementById('indexSymbol').value;
                
                const resultDiv = document.getElementById('indexResult');
                resultDiv.innerHTML = '<div class="alert alert-info"><i class="bi bi-hourglass-split me-2"></i>Indexation en cours...</div>';
                
                try {
                    const response = await fetch('/api/index', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            symbol: symbol
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Afficher les résultats de manière plus élégante
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <i class="bi bi-check-circle me-2"></i><strong>Succès!</strong> ${data.message}
                        </div>
                        <div class="card mt-3">
                            <div class="card-header bg-light">
                                <h3 class="h5 mb-0">Détails de l'indexation</h3>
                            </div>
                            <div class="card-body">
                                <ul class="list-group">
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Symbole
                                        <span class="badge bg-primary rounded-pill">${data.symbol}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Taille du vecteur (séries temporelles)
                                        <span class="badge bg-secondary rounded-pill">${data.details.time_series_vector_size}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Taille du vecteur (aperçu)
                                        <span class="badge bg-secondary rounded-pill">${data.details.overview_vector_size}</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Normalisé
                                        <span class="badge bg-success rounded-pill">Oui</span>
                                    </li>
                                    <li class="list-group-item d-flex justify-content-between align-items-center">
                                        Horodatage
                                        <span class="badge bg-info rounded-pill">${new Date(data.details.timestamp).toLocaleString()}</span>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="bi bi-exclamation-triangle me-2"></i><strong>Erreur:</strong> ${error.message}
                        </div>
                    `;
                }
            });
        });
        
        // Initialiser le graphique
        function initChart() {
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            stockChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.dates,
                    datasets: chartData.datasets.map(dataset => ({
                        label: dataset.label,
                        data: dataset.data,
                        borderColor: dataset.borderColor,
                        backgroundColor: dataset.backgroundColor,
                        borderWidth: 2,
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        tension: 0.3,
                        fill: true
                    }))
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': $' + context.raw.toFixed(2);
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            }
                        },
                        y: {
                            beginAtZero: false,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            },
                            ticks: {
                                callback: function(value) {
                                    return '$' + value;
                                }
                            }
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    },
                    animations: {
                        tension: {
                            duration: 1000,
                            easing: 'linear'
                        }
                    }
                }
            });
        }
        
        // Mettre à jour la période du graphique (simulation)
        function updateChartPeriod(period) {
            // Simuler un chargement
            document.getElementById('stockChart').style.opacity = 0.5;
            
            // Simuler une requête API
            setTimeout(() => {
                // Générer de nouvelles données aléatoires
                const newData = chartData.datasets.map(dataset => {
                    const baseValue = dataset.label === 'AAPL' ? 180 : (dataset.label === 'MSFT' ? 365 : 140);
                    return dataset.data.map(() => baseValue + (Math.random() * 20 - 10));
                });
                
                // Mettre à jour les données du graphique
                for (let i = 0; i < chartData.datasets.length; i++) {
                    stockChart.data.datasets[i].data = newData[i];
                }
                
                // Mettre à jour les dates en fonction de la période
                let newDates;
                if (period === '1m') {
                    newDates = chartData.dates.slice(-30);
                } else if (period === '3m') {
                    newDates = chartData.dates.slice(-90);
                } else {
                    // Simuler des dates pour 1 an
                    const endDate = new Date();
                    const startDate = new Date();
                    startDate.setFullYear(endDate.getFullYear() - 1);
                    newDates = [];
                    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 7)) {
                        newDates.push(d.toISOString().split('T')[0]);
                    }
                }
                
                stockChart.data.labels = newDates;
                stockChart.update();
                
                // Restaurer l'opacité
                document.getElementById('stockChart').style.opacity = 1;
            }, 500);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Page d'accueil de l'application."""
    # Générer des données pour le graphique
    chart_data = generate_chart_data()
    
    # Rendre le template avec les données du graphique
    return render_template_string(HTML_TEMPLATE, chart_data=json.dumps(chart_data))

@app.route('/api/search', methods=['POST'])
def api_search():
    """API pour rechercher des titres similaires (simulée)."""
    try:
        # Récupérer les paramètres de la requête
        data = request.json
        symbol = data.get('symbol')
        search_type = data.get('search_type', 'time_series')
        
        if not symbol:
            return jsonify({"error": "Le symbole boursier est requis"}), 400
        
        # Simuler une recherche
        similar_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "similarity": 0.95, "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "similarity": 0.82, "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "similarity": 0.78, "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "similarity": 0.71, "sector": "Consumer Cyclical"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "similarity": 0.68, "sector": "Communication Services"}
        ]
        
        return jsonify({
            "query": {
                "symbol": symbol,
                "search_type": search_type
            },
            "results": similar_stocks,
            "status": "success",
            "message": "Recherche simulée réussie"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/index', methods=['POST'])
def api_index():
    """API pour indexer un nouveau titre (simulée)."""
    try:
        # Récupérer les paramètres de la requête
        data = request.json
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({"error": "Le symbole boursier est requis"}), 400
        
        # Simuler une indexation
        return jsonify({
            "symbol": symbol,
            "status": "success",
            "message": "Indexation simulée réussie",
            "details": {
                "time_series_vector_size": 128,
                "overview_vector_size": 128,
                "normalized": True,
                "timestamp": "2024-03-06T12:00:00Z"
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Démarrer l'application Flask
    print("Démarrage de l'application sur le port 5050...")
    print("Accédez à l'application à l'adresse: http://127.0.0.1:5050")
    app.run(debug=True, port=5050) 