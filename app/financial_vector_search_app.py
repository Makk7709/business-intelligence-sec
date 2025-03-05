import os
import sys
import numpy as np
import json
import traceback
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv

# Importer notre module d'intégration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.alpha_vantage_pinecone_normalized import (
    initialize_pinecone, get_stock_time_series, get_company_overview,
    vectorize_time_series, vectorize_company_overview, normalize_vector,
    search_similar_stocks, index_stock_data
)

# Charger les variables d'environnement
load_dotenv()

# Vérifier la clé API Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    print("ATTENTION: La clé API Alpha Vantage n'est pas définie dans les variables d'environnement.")
    print("Définissez la variable d'environnement ALPHA_VANTAGE_API_KEY ou créez un fichier .env")

# Créer l'application Flask
app = Flask(__name__)

# Variables globales
pinecone_index = None
pinecone_initialized = False

# Template HTML simplifié
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recherche Vectorielle Financière</title>
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
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #3498db;
        }
        .error {
            color: #e74c3c;
            border-left: 4px solid #e74c3c;
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background-color: #f1f1f1;
            border: none;
            cursor: pointer;
            margin-right: 5px;
            border-radius: 4px 4px 0 0;
        }
        .tab.active {
            background-color: #3498db;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <h1>Recherche Vectorielle Financière avec Normalisation</h1>
    
    <div class="tabs">
        <button class="tab active" onclick="openTab(event, 'search-tab')">Recherche</button>
        <button class="tab" onclick="openTab(event, 'index-tab')">Indexation</button>
        <button class="tab" onclick="openTab(event, 'about-tab')">À propos</button>
    </div>
    
    <div id="search-tab" class="tab-content active">
        <div class="container">
            <h2>Recherche de titres similaires</h2>
            <div class="form-group">
                <label for="symbol">Symbole boursier:</label>
                <input type="text" id="symbol" name="symbol" placeholder="Ex: AAPL" required>
            </div>
            <div class="form-group">
                <label for="search-type">Type de recherche:</label>
                <select id="search-type" name="search-type">
                    <option value="time_series">Séries temporelles</option>
                    <option value="overview">Aperçu de l'entreprise</option>
                </select>
            </div>
            <button onclick="searchSimilarStocks()">Rechercher</button>
            <div id="search-results" class="result" style="display: none;"></div>
        </div>
    </div>
    
    <div id="index-tab" class="tab-content">
        <div class="container">
            <h2>Indexation d'un nouveau titre</h2>
            <div class="form-group">
                <label for="index-symbol">Symbole boursier:</label>
                <input type="text" id="index-symbol" name="index-symbol" placeholder="Ex: MSFT" required>
            </div>
            <button onclick="indexStock()">Indexer</button>
            <div id="index-results" class="result" style="display: none;"></div>
        </div>
    </div>
    
    <div id="about-tab" class="tab-content">
        <div class="container">
            <h2>À propos de cette application</h2>
            <p>Cette application démontre l'intégration de la normalisation des vecteurs avec Alpha Vantage et Pinecone pour la recherche vectorielle de données financières.</p>
            <h3>Fonctionnalités:</h3>
            <ul>
                <li>Normalisation des vecteurs pour améliorer la qualité des recherches</li>
                <li>Indexation des données financières dans Pinecone</li>
                <li>Recherche de titres similaires basée sur les séries temporelles ou les informations d'entreprise</li>
            </ul>
            <h3>Technologies utilisées:</h3>
            <ul>
                <li>Flask pour le backend</li>
                <li>Alpha Vantage pour les données financières</li>
                <li>Pinecone pour la recherche vectorielle</li>
                <li>NumPy pour le traitement des vecteurs</li>
            </ul>
        </div>
    </div>
    
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].className = tabcontent[i].className.replace(" active", "");
            }
            tablinks = document.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).className += " active";
            evt.currentTarget.className += " active";
        }
        
        function searchSimilarStocks() {
            const symbol = document.getElementById('symbol').value;
            if (!symbol) {
                alert('Veuillez entrer un symbole boursier');
                return;
            }
            
            const searchType = document.getElementById('search-type').value;
            
            document.getElementById('search-results').style.display = 'none';
            
            fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: symbol,
                    search_type: searchType
                }),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('search-results').style.display = 'block';
                
                if (data.error) {
                    document.getElementById('search-results').innerHTML = `<p class="error">${data.error}</p>`;
                    return;
                }
                
                let resultsHtml = `<h3>Résultats pour ${symbol}:</h3>`;
                resultsHtml += `<p>Status: ${data.status}</p>`;
                
                document.getElementById('search-results').innerHTML = resultsHtml;
            })
            .catch(error => {
                document.getElementById('search-results').style.display = 'block';
                document.getElementById('search-results').innerHTML = `<p class="error">Erreur: ${error.message}</p>`;
            });
        }
        
        function indexStock() {
            const symbol = document.getElementById('index-symbol').value;
            if (!symbol) {
                alert('Veuillez entrer un symbole boursier');
                return;
            }
            
            document.getElementById('index-results').style.display = 'none';
            
            fetch('/api/index', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: symbol
                }),
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('index-results').style.display = 'block';
                
                if (data.error) {
                    document.getElementById('index-results').innerHTML = `<p class="error">${data.error}</p>`;
                    return;
                }
                
                let resultsHtml = `<h3>Indexation pour ${symbol}:</h3>`;
                resultsHtml += `<p>Status: ${data.status}</p>`;
                
                document.getElementById('index-results').innerHTML = resultsHtml;
            })
            .catch(error => {
                document.getElementById('index-results').style.display = 'block';
                document.getElementById('index-results').innerHTML = `<p class="error">Erreur: ${error.message}</p>`;
            });
        }
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
        normalized_vector = vector / norm
    else:
        print('Warning: Zero vector detected, cannot normalize')
        normalized_vector = vector
    
    return normalized_vector

def safe_initialize_pinecone():
    """Initialise Pinecone de manière sécurisée."""
    try:
        import pinecone
        
        # Configuration de Pinecone
        PINECONE_API_KEY = "pcsk_2ufD2c_AoNVgZYP28gYsABGSdkHM2kFyviRzfTqogKVw8ac8F2g6ZyY1GwW8sYvrdJQCZM"
        PINECONE_ENVIRONMENT = "gcp-starter"
        INDEX_NAME = "financial-data"
        
        # Initialiser Pinecone
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        
        # Vérifier si l'index existe
        if INDEX_NAME in pinecone.list_indexes():
            # Se connecter à l'index
            index = pinecone.Index(INDEX_NAME)
            return index, True
        else:
            return None, False
    except Exception as e:
        print(f"Erreur lors de l'initialisation de Pinecone: {str(e)}")
        traceback.print_exc()
        return None, False

@app.route('/')
def index():
    """Page d'accueil de l'application."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search', methods=['POST'])
def api_search():
    """API pour rechercher des titres similaires."""
    try:
        # Récupérer les paramètres de la requête
        data = request.json
        symbol = data.get('symbol')
        search_type = data.get('search_type', 'time_series')
        
        if not symbol:
            return jsonify({"error": "Le symbole boursier est requis"}), 400
        
        # Initialiser Pinecone si nécessaire
        global pinecone_index, pinecone_initialized
        if not pinecone_initialized:
            pinecone_index, pinecone_initialized = safe_initialize_pinecone()
        
        if not pinecone_initialized:
            return jsonify({
                "status": "Pinecone non initialisé",
                "message": "L'index Pinecone n'est pas disponible. Vérifiez votre configuration."
            })
        
        # Simuler une recherche pour éviter les problèmes de segmentation
        return jsonify({
            "symbol": symbol,
            "search_type": search_type,
            "status": "Recherche simulée réussie",
            "message": "Cette version de l'application simule la recherche pour éviter les problèmes de segmentation."
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/index', methods=['POST'])
def api_index():
    """API pour indexer un nouveau titre."""
    try:
        # Récupérer les paramètres de la requête
        data = request.json
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({"error": "Le symbole boursier est requis"}), 400
        
        # Initialiser Pinecone si nécessaire
        global pinecone_index, pinecone_initialized
        if not pinecone_initialized:
            pinecone_index, pinecone_initialized = safe_initialize_pinecone()
        
        if not pinecone_initialized:
            return jsonify({
                "status": "Pinecone non initialisé",
                "message": "L'index Pinecone n'est pas disponible. Vérifiez votre configuration."
            })
        
        # Simuler une indexation pour éviter les problèmes de segmentation
        return jsonify({
            "symbol": symbol,
            "status": "Indexation simulée réussie",
            "message": "Cette version de l'application simule l'indexation pour éviter les problèmes de segmentation."
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Tenter d'initialiser Pinecone au démarrage
    pinecone_index, pinecone_initialized = safe_initialize_pinecone()
    if pinecone_initialized:
        print("Pinecone initialisé avec succès!")
    else:
        print("Avertissement: Pinecone n'a pas pu être initialisé. L'application fonctionnera en mode limité.")
    
    # Démarrer l'application Flask
    print("Démarrage de l'application sur le port 5050...")
    app.run(debug=True, port=5050)

