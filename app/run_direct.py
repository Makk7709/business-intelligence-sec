"""
Script simplifié pour lancer directement le dashboard complet avec l'assistant IA.
"""

import os
import sys
import logging
import json
from flask import Flask, send_file, render_template_string, jsonify, request
from dotenv import load_dotenv
import openai

# Charger les variables d'environnement
load_dotenv()

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

# Configurer l'API OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("Clé API OpenAI non trouvée. L'assistant IA utilisera des réponses prédéfinies.")
else:
    openai.api_key = openai_api_key
    logger.info("API OpenAI configurée avec succès.")

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
    
    # Réponses prédéfinies pour l'assistant IA (utilisées si l'API OpenAI n'est pas disponible)
    responses = {
        'revenus': "Les revenus d'Apple ont atteint 390,036 millions de dollars en 2024, soit une augmentation de 3.7% par rapport à 2023.",
        'marges': "La marge brute d'Apple était de 43.8% en 2024, tandis que celle de Microsoft était de 70.0%. Microsoft a une marge brute significativement plus élevée.",
        'prévisions': "Selon nos prédictions, les revenus d'Apple devraient atteindre environ 405,637 millions de dollars en 2025 et 421,863 millions de dollars en 2026.",
        'perspectives': "Les perspectives financières pour Apple sont positives, avec une croissance prévue des revenus et une stabilisation des marges brutes autour de 44%."
    }
    
    # Utiliser l'API OpenAI si disponible
    if openai_api_key:
        try:
            logger.info(f"Envoi de la requête à OpenAI: {query}")
            
            # Contexte financier pour l'assistant
            financial_context = """
            Données financières d'Apple:
            - Revenus: 390,036 millions de dollars en 2024, 375,970 millions en 2023, 368,234 millions en 2022
            - Marge brute: 43.8% en 2024, 43.2% en 2023, 46.4% en 2022
            - Bénéfice net: 97,150 millions de dollars en 2024, 94,320 millions en 2023, 99,803 millions en 2022
            
            Données financières de Microsoft:
            - Revenus: 225,340 millions de dollars en 2024, 205,357 millions en 2023, 188,852 millions en 2022
            - Marge brute: 70.0% en 2024, 69.0% en 2023, 66.8% en 2022
            - Bénéfice net: 72,361 millions de dollars en 2024, 72,361 millions en 2023, 67,430 millions en 2022
            
            Prédictions pour Apple:
            - Revenus: environ 405,637 millions de dollars en 2025, 421,863 millions en 2026
            - Marge brute: environ 44.1% en 2025, 44.3% en 2026
            
            Prédictions pour Microsoft:
            - Revenus: environ 245,621 millions de dollars en 2025, 267,726 millions en 2026
            - Marge brute: environ 70.5% en 2025, 71.0% en 2026
            """
            
            # Appel à l'API OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Tu es un assistant financier spécialisé dans l'analyse des données d'Apple et Microsoft. Réponds de manière concise et précise aux questions sur les données financières. Voici les données dont tu disposes: {financial_context}"},
                    {"role": "user", "content": query}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            # Extraire la réponse
            ai_response = response.choices[0].message.content
            logger.info(f"Réponse d'OpenAI reçue: {ai_response[:50]}...")
            
            return jsonify({
                'response': ai_response,
                'query': query
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
            logger.info("Utilisation des réponses prédéfinies comme fallback.")
    
    # Utiliser les réponses prédéfinies si l'API OpenAI n'est pas disponible ou en cas d'erreur
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
    # Données comparatives pour Apple et Microsoft
    data = {
        'years': ['2022', '2023', '2024'],
        'companies': ['Apple', 'Microsoft'],
        'revenue': {
            'Apple': [368234, 375970, 390036],
            'Microsoft': [188852, 205357, 225340]
        },
        'grossMargin': {
            'Apple': [46.4, 43.2, 43.8],
            'Microsoft': [66.8, 69.0, 70.0]
        },
        'netIncome': {
            'Apple': [99803, 94320, 97150],
            'Microsoft': [67430, 72361, 72361]
        }
    }
    return jsonify(data)

def main():
    """Fonction principale qui lance l'application."""
    # Vérifier si le fichier HTML statique existe
    if not os.path.exists(STATIC_HTML):
        logger.error(f"Erreur: Le fichier {STATIC_HTML} n'existe pas.")
        return 1
    
    # Lancer l'application
    logger.info("=" * 80)
    logger.info(f"Démarrage du dashboard financier complet sur le port {PORT}")
    logger.info("=" * 80)
    
    try:
        logger.info(f"Lancement de l'application sur le port {PORT}...")
        logger.info(f"Accédez à l'application à l'adresse: http://127.0.0.1:{PORT}")
        app.run(host='127.0.0.1', port=PORT)
        return 0
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 