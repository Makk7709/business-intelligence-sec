import os
import numpy as np
from flask import Flask, request, jsonify, render_template
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

def find_available_port(start_port=5050, max_attempts=100):
    """Trouve un port disponible pour l'application."""
    import socket
    port = start_port
    for _ in range(max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    raise RuntimeError(f"Impossible de trouver un port disponible après {max_attempts} tentatives")

if __name__ == "__main__":
    # Trouver un port disponible
    port = find_available_port()
    
    # Démarrer l'application Flask
    print(f"Démarrage de l'application sur le port {port}...")
    print(f"Accédez à l'application à l'adresse: http://127.0.0.1:{port}")
    app.run(debug=True, port=port) 