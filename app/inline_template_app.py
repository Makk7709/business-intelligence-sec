from flask import Flask, render_template_string, request, jsonify

# Créer l'application Flask
app = Flask(__name__)

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
    
    <!-- CSS personnalisé minimal -->
    <style>
        /* Variables CSS pour la cohérence des couleurs */
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
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
                            <button type="submit" class="btn btn-primary">Rechercher</button>
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
                            <button type="submit" class="btn btn-primary">Indexer</button>
                        </form>
                        <div class="mt-4" id="indexResult"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts JS depuis CDN -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
    
    <!-- Script personnalisé minimal -->
    <script>
        // Attendre que le DOM soit chargé
        document.addEventListener('DOMContentLoaded', function() {
            // Gestionnaire pour le formulaire de recherche
            document.getElementById('searchForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const symbol = document.getElementById('symbol').value;
                const searchType = document.getElementById('searchType').value;
                
                const resultDiv = document.getElementById('searchResult');
                resultDiv.innerHTML = '<div class="alert alert-info">Recherche en cours...</div>';
                
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
                        <div class="alert alert-success">Recherche réussie pour ${symbol}</div>
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
                            <strong>Erreur:</strong> ${error.message}
                        </div>
                    `;
                }
            });
            
            // Gestionnaire pour le formulaire d'indexation
            document.getElementById('indexForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const symbol = document.getElementById('indexSymbol').value;
                
                const resultDiv = document.getElementById('indexResult');
                resultDiv.innerHTML = '<div class="alert alert-info">Indexation en cours...</div>';
                
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
                            <strong>Succès!</strong> ${data.message}
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
                            <strong>Erreur:</strong> ${error.message}
                        </div>
                    `;
                }
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Page d'accueil de l'application."""
    return render_template_string(HTML_TEMPLATE)

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