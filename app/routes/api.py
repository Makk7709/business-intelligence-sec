"""
Routes API pour l'application.
"""

from flask import Blueprint, jsonify, request
import os
import sys
import json
import time

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import (
    QUERY_FILE, RESPONSE_FILE, STATUS_FILE,
    OPENAI_API_KEY, PINECONE_API_KEY
)
from app.core.data_loader import (
    load_company_data, load_comparative_data, load_prediction_data
)

# Créer le blueprint pour les routes API
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/ai-query', methods=['POST'])
def ai_query():
    """Route pour traiter les requêtes de l'assistant IA."""
    data = request.json
    query = data.get('query', '')
    query_type = data.get('type', 'openai')  # Par défaut, utiliser OpenAI
    
    # Vérifier si la requête est vide
    if not query.strip():
        return jsonify({
            'response': "Je n'ai pas compris votre question. Pourriez-vous reformuler ?",
            'query': query
        })
    
    # Envoyer la requête au pont IA
    response = send_query_to_ai_bridge(query, query_type)
    
    return jsonify(response)

@api_bp.route('/comparative-data', methods=['GET'])
def get_comparative_data():
    """Route pour obtenir les données comparatives."""
    # Charger les données comparatives
    comparative = load_comparative_data()
    
    # Convertir en format adapté pour l'API
    data = {
        "years": comparative.years,
        "companies": comparative.companies,
        "metrics": {}
    }
    
    # Ajouter les données pour chaque métrique
    for metric in comparative.metrics:
        data["metrics"][metric] = {}
        for company in comparative.companies:
            company_data = comparative.get_metric_for_company(company, metric)
            data["metrics"][metric][company] = [company_data.get(year, 0) for year in comparative.years]
    
    return jsonify(data)

@api_bp.route('/company/<company_code>', methods=['GET'])
def get_company_data(company_code):
    """Route pour obtenir les données d'une entreprise."""
    # Charger les données de l'entreprise
    financials = load_company_data(company_code)
    
    if not financials:
        return jsonify({"error": f"Données non trouvées pour l'entreprise {company_code}"}), 404
    
    # Convertir en format adapté pour l'API
    data = {
        "name": financials.name,
        "ticker": financials.ticker,
        "metrics": {}
    }
    
    # Ajouter les données pour chaque métrique
    for metric_name, series in financials.metrics.items():
        data["metrics"][metric_name] = {
            "years": series.get_years(),
            "values": series.get_values()
        }
    
    return jsonify(data)

@api_bp.route('/predictions/<company_code>', methods=['GET'])
def get_predictions(company_code):
    """Route pour obtenir les prédictions pour une entreprise."""
    # Mapper les codes d'entreprise aux noms
    company_map = {
        'aapl': 'Apple',
        'msft': 'Microsoft',
        'tsla': 'Tesla',
        'amzn': 'Amazon',
        'googl': 'Google'
    }
    
    company_name = company_map.get(company_code)
    if not company_name:
        return jsonify({"error": f"Entreprise inconnue: {company_code}"}), 404
    
    # Charger les prédictions
    all_predictions = load_prediction_data()
    company_predictions = all_predictions.get(company_name, {})
    
    if not company_predictions:
        return jsonify({"error": f"Prédictions non trouvées pour l'entreprise {company_name}"}), 404
    
    # Convertir en format adapté pour l'API
    data = {
        "company": company_name,
        "metrics": {}
    }
    
    # Ajouter les données pour chaque métrique
    for metric_name, series in company_predictions.items():
        data["metrics"][metric_name] = {
            "years": series.get_years(),
            "values": series.get_values(),
            "details": {
                str(year): {
                    "value": pred.value,
                    "confidence": pred.confidence,
                    "growth_rate": pred.growth_rate
                }
                for year, pred in series.predictions.items()
            }
        }
    
    return jsonify(data)

@api_bp.route('/load-document', methods=['POST'])
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

def send_query_to_ai_bridge(query, query_type='openai'):
    """Envoie une requête au pont IA."""
    try:
        # Vérifier si le pont IA est en cours d'exécution
        if not os.path.exists(STATUS_FILE):
            return {
                "response": "Le pont IA n'est pas en cours d'exécution. Veuillez démarrer le pont IA.",
                "query": query,
                "source": "error"
            }
        
        # Lire le statut du pont IA
        try:
            with open(STATUS_FILE, 'r') as f:
                status = json.load(f)
            
            if status.get('status') != 'ready':
                return {
                    "response": f"Le pont IA n'est pas prêt: {status.get('message', 'Statut inconnu')}",
                    "query": query,
                    "source": "error"
                }
        except Exception as e:
            return {
                "response": f"Erreur lors de la lecture du statut du pont IA: {str(e)}",
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
        
        # Attendre la réponse
        for _ in range(30):  # Attendre jusqu'à 30 secondes
            if os.path.exists(RESPONSE_FILE):
                try:
                    with open(RESPONSE_FILE, 'r') as f:
                        response = json.load(f)
                    
                    # Supprimer le fichier de réponse
                    os.remove(RESPONSE_FILE)
                    
                    return response
                except Exception as e:
                    return {
                        "response": f"Erreur lors de la lecture de la réponse du pont IA: {str(e)}",
                        "query": query,
                        "source": "error"
                    }
            
            time.sleep(1)
        
        return {
            "response": "Aucune réponse reçue du pont IA dans le délai imparti. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }
        
    except Exception as e:
        return {
            "response": f"Erreur lors de l'envoi de la requête au pont IA: {str(e)}",
            "query": query,
            "source": "error"
        } 