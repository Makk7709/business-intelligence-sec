from flask import Flask, render_template, request, jsonify

# Créer l'application Flask
app = Flask(__name__)

@app.route('/')
def index():
    """Page d'accueil de l'application."""
    return render_template('responsive_dashboard.html')

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