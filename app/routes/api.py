"""
Routes API pour l'application.
"""

from flask import Blueprint, jsonify, request, send_file, session
import os
import sys
import json
import time

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import (
    QUERY_FILE, RESPONSE_FILE, STATUS_FILE,
    OPENAI_API_KEY, PINECONE_API_KEY, ALLOWED_EXTENSIONS,
    MAX_UPLOAD_SIZE, UPLOADS_DIR, EXPORT_FORMATS,
    EXPORTS_DIR, DATA_DIR
)
from app.core.data_loader import (
    load_company_data, load_comparative_data, load_prediction_data
)
from app.core.ai_manager import ai_manager
from app.core.edgar_integration import edgar_integration
from app.core.alpha_vantage_integration import alpha_vantage_integration
from app.core.pdf_processor import pdf_processor
from app.core.export_manager import export_manager
from app.core.security_manager import security_manager

# Créer le blueprint pour les routes API
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """Route pour obtenir un token CSRF."""
    return jsonify({
        'token': security_manager.get_csrf_token()
    })

@api_bp.route('/ai-query', methods=['POST'])
@security_manager.limit_rate
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
    
    # Valider la requête
    if not security_manager.input_validator.validate_string(query, max_length=500):
        return jsonify({
            'response': "La requête est invalide ou trop longue.",
            'query': query
        }), 400
    
    # Nettoyer la requête
    query = security_manager.input_validator.sanitize_string(query)
    
    # Envoyer la requête au pont IA en utilisant AIManager
    response = ai_manager.send_query(query, query_type)
    
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
    # Valider le code de l'entreprise
    if not security_manager.input_validator.validate_string(company_code, pattern=r'^[a-zA-Z0-9]+$'):
        return jsonify({"error": "Invalid company code"}), 400
    
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
    # Valider le code de l'entreprise
    if not security_manager.input_validator.validate_string(company_code, pattern=r'^[a-zA-Z0-9]+$'):
        return jsonify({"error": "Invalid company code"}), 400
    
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
@security_manager.require_csrf_token
@security_manager.limit_rate
def load_document():
    """Route pour charger un document dans Pinecone."""
    # Valider le fichier
    error = security_manager.validate_file_upload(
        request.files.get('file'),
        ALLOWED_EXTENSIONS,
        MAX_UPLOAD_SIZE
    )
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    file = request.files['file']
    
    # Sauvegarder le fichier
    filename = os.path.join(UPLOADS_DIR, file.filename)
    file.save(filename)
    
    # Traiter le document (à implémenter)
    # TODO: Implémenter le traitement du document et l'indexation dans Pinecone
    
    return jsonify({
        'success': True,
        'message': f"Document '{file.filename}' chargé avec succès.",
        'filename': file.filename
    })

@api_bp.route('/edgar/download/<ticker>', methods=['POST'])
@security_manager.require_csrf_token
@security_manager.limit_rate
def download_edgar_filing(ticker):
    """
    Route pour télécharger un document financier depuis EDGAR.
    
    Args:
        ticker: Le symbole boursier de l'entreprise
    """
    # Valider le ticker
    if not security_manager.input_validator.validate_string(ticker, pattern=r'^[A-Z]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid ticker symbol"
        }), 400
    
    data = request.json or {}
    filing_type = data.get('filing_type', '10-K')
    count = data.get('count', 1)
    
    # Valider le type de document
    if not security_manager.input_validator.validate_string(filing_type, pattern=r'^[0-9A-Z\-]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid filing type"
        }), 400
    
    # Valider le nombre de documents
    if not security_manager.input_validator.validate_integer(count, min_value=1, max_value=10):
        return jsonify({
            'success': False,
            'message': "Invalid count (must be between 1 and 10)"
        }), 400
    
    try:
        # Télécharger le document
        filing_dir = edgar_integration.download_filing(ticker, filing_type, count)
        
        return jsonify({
            'success': True,
            'message': f"Document {filing_type} téléchargé avec succès pour {ticker}.",
            'filing_dir': filing_dir
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors du téléchargement du document: {str(e)}"
        }), 500

@api_bp.route('/edgar/process/<ticker>', methods=['POST'])
@security_manager.require_csrf_token
@security_manager.limit_rate
def process_edgar_filing(ticker):
    """
    Route pour traiter les documents financiers d'une entreprise.
    
    Args:
        ticker: Le symbole boursier de l'entreprise
    """
    # Valider le ticker
    if not security_manager.input_validator.validate_string(ticker, pattern=r'^[A-Z]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid ticker symbol"
        }), 400
    
    data = request.json or {}
    filing_type = data.get('filing_type', '10-K')
    
    # Valider le type de document
    if not security_manager.input_validator.validate_string(filing_type, pattern=r'^[0-9A-Z\-]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid filing type"
        }), 400
    
    try:
        # Traiter les documents
        text_file, data_file = edgar_integration.process_company(ticker, filing_type)
        
        return jsonify({
            'success': True,
            'message': f"Documents financiers traités avec succès pour {ticker}.",
            'text_file': text_file,
            'data_file': data_file
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors du traitement des documents: {str(e)}"
        }), 500

@api_bp.route('/alpha-vantage/time-series/<ticker>', methods=['GET'])
@security_manager.limit_rate
def get_time_series(ticker):
    """
    Route pour obtenir les données de série temporelle pour une entreprise.
    
    Args:
        ticker: Le symbole boursier de l'entreprise
    """
    # Valider le ticker
    if not security_manager.input_validator.validate_string(ticker, pattern=r'^[A-Z]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid ticker symbol"
        }), 400
    
    outputsize = request.args.get('outputsize', 'compact')
    
    # Valider la taille de sortie
    if outputsize not in ['compact', 'full']:
        return jsonify({
            'success': False,
            'message': "Invalid outputsize (must be 'compact' or 'full')"
        }), 400
    
    try:
        # Récupérer les données de série temporelle
        df = alpha_vantage_integration.get_time_series_daily(ticker, outputsize)
        
        # Convertir le DataFrame en dictionnaire
        data = {
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'open': df['open'].tolist(),
            'high': df['high'].tolist(),
            'low': df['low'].tolist(),
            'close': df['close'].tolist(),
            'volume': df['volume'].tolist()
        }
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'data': data
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de la récupération des données de série temporelle: {str(e)}"
        }), 500

@api_bp.route('/alpha-vantage/company-overview/<ticker>', methods=['GET'])
@security_manager.limit_rate
def get_company_overview(ticker):
    """
    Route pour obtenir les informations générales sur une entreprise.
    
    Args:
        ticker: Le symbole boursier de l'entreprise
    """
    # Valider le ticker
    if not security_manager.input_validator.validate_string(ticker, pattern=r'^[A-Z]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid ticker symbol"
        }), 400
    
    try:
        # Récupérer les informations sur l'entreprise
        overview = alpha_vantage_integration.get_company_overview(ticker)
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'data': overview
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de la récupération des informations sur l'entreprise: {str(e)}"
        }), 500

@api_bp.route('/alpha-vantage/financial-data/<ticker>', methods=['GET'])
@security_manager.limit_rate
def get_financial_data(ticker):
    """
    Route pour obtenir les données financières d'une entreprise.
    
    Args:
        ticker: Le symbole boursier de l'entreprise
    """
    # Valider le ticker
    if not security_manager.input_validator.validate_string(ticker, pattern=r'^[A-Z]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid ticker symbol"
        }), 400
    
    try:
        # Récupérer les données financières
        financial_data = alpha_vantage_integration.get_financial_data(ticker)
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'data': financial_data
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de la récupération des données financières: {str(e)}"
        }), 500

@api_bp.route('/alpha-vantage/key-metrics/<ticker>', methods=['GET'])
@security_manager.limit_rate
def get_key_metrics(ticker):
    """
    Route pour obtenir les métriques clés d'une entreprise.
    
    Args:
        ticker: Le symbole boursier de l'entreprise
    """
    # Valider le ticker
    if not security_manager.input_validator.validate_string(ticker, pattern=r'^[A-Z]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid ticker symbol"
        }), 400
    
    try:
        # Extraire les métriques clés
        metrics = alpha_vantage_integration.extract_key_metrics(ticker)
        
        # Convertir les métriques en format adapté pour l'API
        formatted_metrics = {}
        for metric, years_data in metrics.items():
            formatted_metrics[metric] = {
                'years': sorted(years_data.keys()),
                'values': [years_data[year] for year in sorted(years_data.keys())]
            }
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'metrics': formatted_metrics
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de l'extraction des métriques clés: {str(e)}"
        }), 500

@api_bp.route('/pdf/process', methods=['POST'])
@security_manager.limit_rate
def process_pdf():
    """Route pour traiter un fichier PDF."""
    # Valider le fichier
    error = security_manager.validate_file_upload(
        request.files.get('file'),
        ['pdf'],
        MAX_UPLOAD_SIZE
    )
    
    if error:
        return jsonify({
            'success': False,
            'message': error
        }), 400
    
    file = request.files['file']
    
    # Sauvegarder le fichier
    filename = os.path.join(UPLOADS_DIR, file.filename)
    file.save(filename)
    
    try:
        # Traiter le fichier PDF
        text_file, data_file = pdf_processor.process_pdf(filename)
        
        # Lire les données financières extraites
        with open(data_file, 'r') as f:
            financial_data = json.load(f)
        
        return jsonify({
            'success': True,
            'message': f"Document '{file.filename}' traité avec succès.",
            'text_file': text_file,
            'data_file': data_file,
            'financial_data': financial_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors du traitement du document: {str(e)}"
        }), 500

@api_bp.route('/export/<format>', methods=['POST'])
@security_manager.limit_rate
def export_data(format):
    """
    Route pour exporter des données dans différents formats.
    
    Args:
        format: Le format d'exportation (csv, excel, pdf, json)
    """
    # Vérifier si le format est pris en charge
    if format.lower() not in EXPORT_FORMATS:
        return jsonify({
            'success': False,
            'message': f"Format d'exportation non pris en charge. Formats pris en charge: {', '.join(EXPORT_FORMATS)}"
        }), 400
    
    # Récupérer les données à exporter
    data = request.json
    if not data:
        return jsonify({
            'success': False,
            'message': "Aucune donnée à exporter."
        }), 400
    
    # Récupérer le nom du fichier
    filename = request.args.get('filename')
    
    # Valider le nom du fichier
    if filename and not security_manager.input_validator.validate_string(filename, pattern=r'^[a-zA-Z0-9_\-\.]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid filename"
        }), 400
    
    try:
        # Exporter les données
        filepath = export_manager.export_data(data, format, filename)
        
        # Retourner le chemin vers le fichier exporté
        return jsonify({
            'success': True,
            'message': f"Données exportées avec succès au format {format}.",
            'filepath': filepath
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de l'exportation des données: {str(e)}"
        }), 500

@api_bp.route('/export/company/<company_code>/<format>', methods=['GET'])
@security_manager.limit_rate
def export_company_data(company_code, format):
    """
    Route pour exporter les données d'une entreprise dans différents formats.
    
    Args:
        company_code: Le code de l'entreprise
        format: Le format d'exportation (csv, excel, pdf, json)
    """
    # Valider le code de l'entreprise
    if not security_manager.input_validator.validate_string(company_code, pattern=r'^[a-zA-Z0-9]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid company code"
        }), 400
    
    # Vérifier si le format est pris en charge
    if format.lower() not in EXPORT_FORMATS:
        return jsonify({
            'success': False,
            'message': f"Format d'exportation non pris en charge. Formats pris en charge: {', '.join(EXPORT_FORMATS)}"
        }), 400
    
    # Charger les données de l'entreprise
    financials = load_company_data(company_code)
    
    if not financials:
        return jsonify({
            'success': False,
            'message': f"Données non trouvées pour l'entreprise {company_code}"
        }), 404
    
    # Convertir en format adapté pour l'exportation
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
    
    # Récupérer le nom du fichier
    filename = request.args.get('filename', f"{company_code}_financials")
    
    # Valider le nom du fichier
    if filename and not security_manager.input_validator.validate_string(filename, pattern=r'^[a-zA-Z0-9_\-\.]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid filename"
        }), 400
    
    try:
        # Exporter les données
        filepath = export_manager.export_data(data, format, filename)
        
        # Si le format est 'json', 'csv' ou 'excel', retourner le chemin vers le fichier
        if format.lower() in ['json', 'csv', 'excel']:
            return jsonify({
                'success': True,
                'message': f"Données exportées avec succès au format {format}.",
                'filepath': filepath
            })
        
        # Si le format est 'pdf', retourner le fichier directement
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de l'exportation des données: {str(e)}"
        }), 500

@api_bp.route('/export/comparative/<format>', methods=['GET'])
@security_manager.limit_rate
def export_comparative_data(format):
    """
    Route pour exporter les données comparatives dans différents formats.
    
    Args:
        format: Le format d'exportation (csv, excel, pdf, json)
    """
    # Vérifier si le format est pris en charge
    if format.lower() not in EXPORT_FORMATS:
        return jsonify({
            'success': False,
            'message': f"Format d'exportation non pris en charge. Formats pris en charge: {', '.join(EXPORT_FORMATS)}"
        }), 400
    
    # Charger les données comparatives
    comparative = load_comparative_data()
    
    # Convertir en format adapté pour l'exportation
    data = {
        "name": "Analyse comparative",
        "years": comparative.years,
        "companies": comparative.companies,
        "metrics": {}
    }
    
    # Ajouter les données pour chaque métrique
    for metric in comparative.metrics:
        data["metrics"][metric] = {}
        for company in comparative.companies:
            company_data = comparative.get_metric_for_company(company, metric)
            years = sorted(company_data.keys())
            values = [company_data.get(year, 0) for year in years]
            
            data["metrics"][f"{metric}_{company}"] = {
                "years": years,
                "values": values
            }
    
    # Récupérer le nom du fichier
    filename = request.args.get('filename', "comparative_analysis")
    
    # Valider le nom du fichier
    if filename and not security_manager.input_validator.validate_string(filename, pattern=r'^[a-zA-Z0-9_\-\.]+$'):
        return jsonify({
            'success': False,
            'message': "Invalid filename"
        }), 400
    
    try:
        # Exporter les données
        filepath = export_manager.export_data(data, format, filename)
        
        # Si le format est 'json', 'csv' ou 'excel', retourner le chemin vers le fichier
        if format.lower() in ['json', 'csv', 'excel']:
            return jsonify({
                'success': True,
                'message': f"Données exportées avec succès au format {format}.",
                'filepath': filepath
            })
        
        # Si le format est 'pdf', retourner le fichier directement
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Erreur lors de l'exportation des données: {str(e)}"
        }), 500

@api_bp.route('/download/<path:filepath>', methods=['GET'])
def download_file(filepath):
    """
    Route pour télécharger un fichier.
    
    Args:
        filepath: Le chemin vers le fichier à télécharger
    """
    # Vérifier si le fichier existe
    if not os.path.exists(filepath):
        return jsonify({
            'success': False,
            'message': f"Le fichier {filepath} n'existe pas."
        }), 404
    
    # Vérifier si le fichier est dans un répertoire autorisé
    allowed_dirs = [EXPORTS_DIR, DATA_DIR]
    if not security_manager.validate_path(filepath, allowed_dirs):
        return jsonify({
            'success': False,
            'message': f"Accès non autorisé au fichier {filepath}."
        }), 403
    
    # Télécharger le fichier
    return send_file(filepath, as_attachment=True) 