"""
Script simplifié pour lancer directement le dashboard complet avec l'assistant IA.
"""

import os
import sys
import logging
import json
import subprocess
import time
from flask import Flask, send_file, render_template_string, jsonify, request
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialiser l'application Flask
app = Flask(__name__)

# Répertoire pour les fichiers de communication avec le pont IA
COMM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comm')
os.makedirs(COMM_DIR, exist_ok=True)

# Fichiers de communication
QUERY_FILE = os.path.join(COMM_DIR, 'query.json')
RESPONSE_FILE = os.path.join(COMM_DIR, 'response.json')
STATUS_FILE = os.path.join(COMM_DIR, 'status.json')

# Chemin vers le fichier HTML statique
STATIC_HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_static.html')

# Processus du pont IA
ai_bridge_process = None

def start_ai_bridge():
    """Démarre le processus du pont IA."""
    global ai_bridge_process
    
    # Chemin vers le script du pont IA
    ai_bridge_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai_bridge.py')
    
    # Vérifier si le fichier existe
    if not os.path.exists(ai_bridge_path):
        logger.error(f"Le fichier du pont IA n'existe pas: {ai_bridge_path}")
        return False
    
    try:
        # Démarrer le processus du pont IA
        ai_bridge_process = subprocess.Popen([sys.executable, ai_bridge_path], 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)
        
        logger.info(f"Processus du pont IA démarré avec PID: {ai_bridge_process.pid}")
        
        # Attendre que le pont IA soit prêt
        for _ in range(10):  # Attendre jusqu'à 10 secondes
            if os.path.exists(STATUS_FILE):
                try:
                    with open(STATUS_FILE, 'r') as f:
                        status = json.load(f)
                    if status.get('status') == 'ready':
                        logger.info("Le pont IA est prêt.")
                        return True
                except Exception as e:
                    logger.warning(f"Erreur lors de la lecture du statut du pont IA: {str(e)}")
            
            time.sleep(1)
        
        logger.warning("Le pont IA n'est pas devenu prêt dans le délai imparti.")
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du pont IA: {str(e)}")
        return False

def stop_ai_bridge():
    """Arrête le processus du pont IA."""
    global ai_bridge_process
    
    if ai_bridge_process:
        try:
            ai_bridge_process.terminate()
            ai_bridge_process.wait(timeout=5)
            logger.info("Processus du pont IA arrêté.")
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du pont IA: {str(e)}")
            try:
                ai_bridge_process.kill()
                logger.info("Processus du pont IA tué.")
            except Exception as e2:
                logger.error(f"Impossible de tuer le processus du pont IA: {str(e2)}")

def send_query_to_ai_bridge(query, query_type='openai'):
    """Envoie une requête au pont IA."""
    try:
        # Vérifier si le pont IA est en cours d'exécution
        if not ai_bridge_process or ai_bridge_process.poll() is not None:
            logger.warning("Le pont IA n'est pas en cours d'exécution. Tentative de redémarrage...")
            if not start_ai_bridge():
                return {
                    "response": "Impossible de démarrer le pont IA. Veuillez réessayer plus tard.",
                    "query": query,
                    "source": "error"
                }
        
        # Écrire la requête dans le fichier de communication
        with open(QUERY_FILE, 'w') as f:
            json.dump({
                'query': query,
                'type': query_type,
                'timestamp': time.time()
            }, f)
        
        logger.info(f"Requête envoyée au pont IA: {query[:50]}...")
        
        # Attendre la réponse
        for _ in range(30):  # Attendre jusqu'à 30 secondes
            if os.path.exists(RESPONSE_FILE):
                try:
                    with open(RESPONSE_FILE, 'r') as f:
                        response = json.load(f)
                    
                    # Supprimer le fichier de réponse
                    os.remove(RESPONSE_FILE)
                    
                    logger.info(f"Réponse reçue du pont IA: {response.get('response', '')[:50]}...")
                    return response
                except Exception as e:
                    logger.warning(f"Erreur lors de la lecture de la réponse du pont IA: {str(e)}")
            
            time.sleep(1)
        
        logger.warning("Aucune réponse reçue du pont IA dans le délai imparti.")
        return {
            "response": "Aucune réponse reçue du pont IA dans le délai imparti. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la requête au pont IA: {str(e)}")
        return {
            "response": f"Erreur lors de l'envoi de la requête au pont IA: {str(e)}",
            "query": query,
            "source": "error"
        }

@app.route('/')
def index():
    """Route principale pour servir le dashboard."""
    return send_file(STATIC_HTML_PATH)

@app.route('/api/ai-query', methods=['POST'])
def ai_query():
    """Route pour traiter les requêtes de l'assistant IA."""
    data = request.json
    query = data.get('query', '')
    query_type = data.get('type', 'openai')  # Par défaut, utiliser OpenAI
    
    logger.info(f"Requête reçue: {query[:50]}... (type: {query_type})")
    
    # Vérifier si la requête est vide
    if not query.strip():
        return jsonify({
            'response': "Je n'ai pas compris votre question. Pourriez-vous reformuler ?",
            'query': query
        })
    
    # Envoyer la requête au pont IA
    response = send_query_to_ai_bridge(query, query_type)
    
    return jsonify(response)

@app.route('/api/comparative-data', methods=['GET'])
def get_comparative_data():
    """Route pour obtenir les données comparatives."""
    # Données comparatives pour Apple et Microsoft
    comparative_data = {
        "years": [2022, 2023, 2024],
        "companies": ["Apple", "Microsoft"],
        "revenue": {
            "Apple": [368234, 375970, 390036],
            "Microsoft": [188852, 205357, 225340]
        },
        "gross_margin": {
            "Apple": [46.4, 43.2, 43.8],
            "Microsoft": [66.8, 69.0, 70.0]
        },
        "net_income": {
            "Apple": [99803, 94320, 97150],
            "Microsoft": [67430, 72361, 72361]
        },
        "growth_rate": {
            "Apple": [7.8, 2.1, 3.7],
            "Microsoft": [18.0, 8.7, 9.7]
        }
    }
    
    return jsonify(comparative_data)

@app.route('/api/load-document', methods=['POST'])
def load_document():
    """Route pour charger un document dans Pinecone."""
    data = request.json
    document_text = data.get('text', '')
    document_title = data.get('title', 'Document sans titre')
    
    if not document_text.strip():
        return jsonify({
            'success': False,
            'message': "Le document est vide."
        })
    
    # Envoyer une requête spéciale au pont IA pour charger le document dans Pinecone
    # Cette fonctionnalité n'est pas implémentée dans cette version
    
    return jsonify({
        'success': True,
        'message': f"Document '{document_title}' chargé avec succès (simulation)."
    })

def main():
    """Fonction principale pour démarrer l'application."""
    try:
        # Démarrer le pont IA
        if start_ai_bridge():
            logger.info("Pont IA démarré avec succès.")
        else:
            logger.warning("Impossible de démarrer le pont IA. L'assistant IA utilisera des réponses prédéfinies.")
        
        # Démarrer l'application Flask
        app.run(host='127.0.0.1', port=5115, debug=False)
    except KeyboardInterrupt:
        logger.info("Arrêt de l'application...")
    finally:
        # Arrêter le pont IA
        stop_ai_bridge()

if __name__ == "__main__":
    main() 