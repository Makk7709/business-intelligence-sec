import os
import numpy as np
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Vérifier la clé API Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    print("ATTENTION: La clé API Alpha Vantage n'est pas définie dans les variables d'environnement.")
    print("Définissez la variable d'environnement ALPHA_VANTAGE_API_KEY ou créez un fichier .env")

# Créer l'application Flask
app = Flask(__name__)

# Template HTML simplifié
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recherche Vectorielle Financière Simplifiée</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
            flex: 1;
            min-width: 300px;
        }
        form {
            margin-bottom: 20px;
        }
        input, select, button {
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        .result {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Recherche Vectorielle Financière Simplifiée</h1>
    
    <div class="container">
        <div class="card">
            <h2>Rechercher des titres similaires</h2>
            <form id="searchForm">
                <div>
                    <label for="symbol">Symbole boursier:</label>
                    <input type="text" id="symbol" name="symbol" placeholder="ex: AAPL" required>
                </div>
                <div>
                    <label for="searchType">Type de recherche:</label>
                    <select id="searchType" name="searchType">
                        <option value="time_series">Séries temporelles</option>
                        <option value="overview">Aperçu de l'entreprise</option>
                    </select>
                </div>
                <button type="submit">Rechercher</button>
            </form>
            <div class="result" id="searchResult"></div>
        </div>
        
        <div class="card">
            <h2>Indexer un nouveau titre</h2>
            <form id="indexForm">
                <div>
                    <label for="indexSymbol">Symbole boursier:</label>
                    <input type="text" id="indexSymbol" name="indexSymbol" placeholder="ex: MSFT" required>
                </div>
                <button type="submit">Indexer</button>
            </form>
            <div class="result" id="indexResult"></div>
        </div>
    </div>
    
    <script>
        // Fonction pour rechercher des titres similaires
        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const symbol = document.getElementById('symbol').value;
            const searchType = document.getElementById('searchType').value;
            
            document.getElementById('searchResult').innerHTML = '<p>Recherche en cours...</p>';
            
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
                document.getElementById('searchResult').innerHTML = `
                    <h3>Résultats:</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            } catch (error) {
                document.getElementById('searchResult').innerHTML = `
                    <h3>Erreur:</h3>
                    <pre>${error.message}</pre>
                `;
            }
        });
        
        // Fonction pour indexer un nouveau titre
        document.getElementById('indexForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const symbol = document.getElementById('indexSymbol').value;
            
            document.getElementById('indexResult').innerHTML = '<p>Indexation en cours...</p>';
            
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
                document.getElementById('indexResult').innerHTML = `
                    <h3>Résultats:</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                `;
            } catch (error) {
                document.getElementById('indexResult').innerHTML = `
                    <h3>Erreur:</h3>
                    <pre>${error.message}</pre>
                `;
            }
        });
    </script>
</body>
</html>
"""

def normalize_vector(vector):
    """Normalise un vecteur pour qu'il ait une norme unitaire."""
    # Convertir en tableau numpy si ce n'est pas déjà le cas
    if not isinstance(vector, np.ndarray):
        vector = np.array(vector, dtype=np.float32)
    
    # Calculer la norme
    norm = np.linalg.norm(vector)
    
    # Normaliser le vecteur
    if norm > 0:
        vector = vector / norm
    else:
        print('Warning: Zero vector detected, cannot normalize')
    
    return vector

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
    app.run(debug=True, port=5050) 