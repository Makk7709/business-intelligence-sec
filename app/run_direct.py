"""
Script simplifié pour lancer directement le dashboard complet avec l'assistant IA.
"""

import os
import sys
import logging
from flask import Flask, send_file, render_template_string, jsonify, request

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Port pour l'application
PORT = 5115

# Chemin vers le fichier HTML statique
STATIC_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_static.html')

# Créer l'application Flask
app = Flask(__name__, static_folder='app/static')

@app.route('/')
def index():
    """Route principale qui sert le fichier HTML statique."""
    return send_file(STATIC_HTML)

@app.route('/api/ai-query', methods=['POST'])
def ai_query():
    """Route pour l'assistant IA."""
    data = request.json
    query = data.get('query', '')
    
    # Réponses prédéfinies pour l'assistant IA
    responses = {
        'revenus': "Les revenus d'Apple ont atteint 390,036 millions de dollars en 2024, soit une augmentation de 3.7% par rapport à 2023.",
        'marges': "La marge brute d'Apple était de 43.8% en 2024, tandis que celle de Microsoft était de 70.0%. Microsoft a une marge brute significativement plus élevée.",
        'prévisions': "Selon nos prédictions, les revenus d'Apple devraient atteindre environ 405,637 millions de dollars en 2025 et 421,863 millions de dollars en 2026.",
        'perspectives': "Les perspectives financières pour Apple sont positives, avec une croissance prévue des revenus et une stabilisation des marges brutes autour de 44%."
    }
    
    # Déterminer la réponse appropriée
    response = "Je ne peux pas répondre à cette question pour le moment. Pourriez-vous reformuler ou poser une autre question?"
    
    if 'revenus' in query.lower() or 'revenue' in query.lower():
        response = responses['revenus']
    elif 'marge' in query.lower() or 'margin' in query.lower():
        response = responses['marges']
    elif 'prévision' in query.lower() or 'prediction' in query.lower():
        response = responses['prévisions']
    elif 'perspective' in query.lower() or 'outlook' in query.lower():
        response = responses['perspectives']
    
    return jsonify({
        'response': response,
        'query': query
    })

@app.route('/api/comparative-data', methods=['GET'])
def get_comparative_data():
    """Route pour les données comparatives."""
    data = {
        'years': ['2022', '2023', '2024'],
        'companies': ['Apple', 'Microsoft'],
        'revenue': {
            'Apple': [368234, 375970, 390036],
            'Microsoft': [188852, 205357, 225340]
        },
        'netIncome': {
            'Apple': [99803, 94320, 97150],
            'Microsoft': [67430, 72361, 72361]
        },
        'grossMargin': {
            'Apple': [46.4, 43.2, 43.8],
            'Microsoft': [66.8, 69.0, 70.0]
        }
    }
    return jsonify(data)

def main():
    """Fonction principale."""
    logger.info("=" * 80)
    logger.info(f"Démarrage du dashboard financier complet sur le port {PORT}")
    logger.info("=" * 80)
    
    # Vérifier si le fichier HTML statique existe
    if not os.path.exists(STATIC_HTML):
        logger.error(f"Erreur: Le fichier {STATIC_HTML} n'existe pas.")
        return 1
    
    # Lancer l'application
    logger.info(f"Lancement de l'application sur le port {PORT}...")
    logger.info(f"Accédez à l'application à l'adresse: http://127.0.0.1:{PORT}")
    
    app.run(host='127.0.0.1', port=PORT, debug=False)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 