import os
import sys
import numpy as np
import pinecone
import requests
from dotenv import load_dotenv
import time
import json
import uuid

# Charger les variables d'environnement
load_dotenv()

# Configuration de Pinecone
PINECONE_API_KEY = "pcsk_2ufD2c_AoNVgZYP28gYsABGSdkHM2kFyviRzfTqogKVw8ac8F2g6ZyY1GwW8sYvrdJQCZM"
PINECONE_ENVIRONMENT = "gcp-starter"
INDEX_NAME = "financial-data"
DIMENSION = 128  # Dimension des vecteurs pour les données financières

# Configuration d'Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

def normalize_vector(vector):
    """
    Normalise un vecteur pour qu'il ait une norme unitaire.
    
    Args:
        vector (np.ndarray): Le vecteur à normaliser
        
    Returns:
        np.ndarray: Le vecteur normalisé
    """
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

def initialize_pinecone():
    """
    Initialise la connexion à Pinecone et crée l'index s'il n'existe pas.
    
    Returns:
        pinecone.Index: L'index Pinecone
    """
    print(f"Initialisation de Pinecone avec la clé API: {PINECONE_API_KEY[:5]}...")
    
    # Initialiser Pinecone
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
    
    # Vérifier si l'index existe, sinon le créer
    if INDEX_NAME not in pinecone.list_indexes():
        print(f"Création de l'index '{INDEX_NAME}'...")
        pinecone.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine"
        )
        # Attendre que l'index soit prêt
        print("Attente de la création de l'index...")
        time.sleep(10)
    
    # Se connecter à l'index
    index = pinecone.Index(INDEX_NAME)
    print(f"Connecté à l'index '{INDEX_NAME}'")
    
    return index

def get_stock_time_series(symbol, function="TIME_SERIES_DAILY", outputsize="compact"):
    """
    Récupère les données de séries temporelles pour un symbole boursier.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL)
        function (str): Le type de série temporelle à récupérer
        outputsize (str): La taille de sortie (compact ou full)
        
    Returns:
        dict: Les données de séries temporelles
    """
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError("La clé API Alpha Vantage n'est pas définie")
    
    params = {
        "function": function,
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
    data = response.json()
    
    # Vérifier si la réponse contient une erreur
    if "Error Message" in data:
        raise ValueError(f"Erreur Alpha Vantage: {data['Error Message']}")
    
    return data

def get_company_overview(symbol):
    """
    Récupère les informations générales sur une entreprise.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL)
        
    Returns:
        dict: Les informations sur l'entreprise
    """
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError("La clé API Alpha Vantage n'est pas définie")
    
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
    data = response.json()
    
    # Vérifier si la réponse contient une erreur
    if "Error Message" in data:
        raise ValueError(f"Erreur Alpha Vantage: {data['Error Message']}")
    
    return data

def vectorize_time_series(time_series_data):
    """
    Convertit les données de séries temporelles en un vecteur.
    
    Args:
        time_series_data (dict): Les données de séries temporelles
        
    Returns:
        np.ndarray: Le vecteur représentant les données
    """
    # Extraire les données de séries temporelles
    time_series_key = next((k for k in time_series_data.keys() if "Time Series" in k), None)
    if not time_series_key:
        raise ValueError("Format de données de séries temporelles non reconnu")
    
    time_series = time_series_data[time_series_key]
    
    # Extraire les valeurs de clôture pour les 30 derniers jours
    close_values = []
    for date in sorted(time_series.keys(), reverse=True)[:30]:
        close_values.append(float(time_series[date]["4. close"]))
    
    # Compléter avec des zéros si nécessaire pour atteindre DIMENSION
    vector = np.zeros(DIMENSION)
    vector[:min(len(close_values), DIMENSION)] = close_values[:min(len(close_values), DIMENSION)]
    
    return vector

def vectorize_company_overview(overview_data):
    """
    Convertit les informations d'une entreprise en un vecteur.
    
    Args:
        overview_data (dict): Les informations sur l'entreprise
        
    Returns:
        np.ndarray: Le vecteur représentant les données
    """
    # Extraire les valeurs numériques des informations de l'entreprise
    numeric_fields = [
        "MarketCapitalization", "EBITDA", "PERatio", "PEGRatio", "BookValue",
        "DividendPerShare", "DividendYield", "EPS", "RevenuePerShareTTM",
        "ProfitMargin", "OperatingMarginTTM", "ReturnOnAssetsTTM",
        "ReturnOnEquityTTM", "RevenueTTM", "GrossProfitTTM", "DilutedEPSTTM",
        "QuarterlyEarningsGrowthYOY", "QuarterlyRevenueGrowthYOY", "AnalystTargetPrice",
        "TrailingPE", "ForwardPE", "PriceToSalesRatioTTM", "PriceToBookRatio",
        "EVToRevenue", "EVToEBITDA", "Beta", "52WeekHigh", "52WeekLow",
        "50DayMovingAverage", "200DayMovingAverage", "SharesOutstanding",
        "SharesFloat", "SharesShort", "SharesShortPriorMonth", "ShortRatio",
        "ShortPercentOutstanding", "ShortPercentFloat", "PercentInsiders",
        "PercentInstitutions", "ForwardAnnualDividendRate", "ForwardAnnualDividendYield",
        "PayoutRatio", "DividendDate", "ExDividendDate", "LastSplitFactor"
    ]
    
    # Créer un vecteur à partir des valeurs numériques
    vector = np.zeros(DIMENSION)
    idx = 0
    
    for field in numeric_fields:
        if field in overview_data and idx < DIMENSION:
            try:
                value = float(overview_data[field])
                vector[idx] = value
                idx += 1
            except (ValueError, TypeError):
                # Ignorer les valeurs non numériques
                pass
    
    return vector

def index_stock_data(symbol, index=None):
    """
    Récupère et indexe les données d'un titre boursier dans Pinecone.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL)
        index (pinecone.Index, optional): L'index Pinecone
        
    Returns:
        dict: Résultat de l'opération d'indexation
    """
    if index is None:
        index = initialize_pinecone()
    
    try:
        # Récupérer les données de séries temporelles
        time_series_data = get_stock_time_series(symbol)
        
        # Récupérer les informations sur l'entreprise
        overview_data = get_company_overview(symbol)
        
        # Vectoriser les données
        time_series_vector = vectorize_time_series(time_series_data)
        overview_vector = vectorize_company_overview(overview_data)
        
        # Normaliser les vecteurs
        normalized_ts_vector = normalize_vector(time_series_vector)
        normalized_ov_vector = normalize_vector(overview_vector)
        
        # Préparer les métadonnées
        ts_metadata = {
            "symbol": symbol,
            "type": "time_series",
            "name": overview_data.get("Name", ""),
            "sector": overview_data.get("Sector", ""),
            "industry": overview_data.get("Industry", ""),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        ov_metadata = {
            "symbol": symbol,
            "type": "overview",
            "name": overview_data.get("Name", ""),
            "sector": overview_data.get("Sector", ""),
            "industry": overview_data.get("Industry", ""),
            "market_cap": overview_data.get("MarketCapitalization", ""),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Générer des IDs uniques
        ts_id = f"{symbol}_ts_{uuid.uuid4()}"
        ov_id = f"{symbol}_ov_{uuid.uuid4()}"
        
        # Insérer les vecteurs dans Pinecone
        vectors = [
            (ts_id, normalized_ts_vector.tolist(), ts_metadata),
            (ov_id, normalized_ov_vector.tolist(), ov_metadata)
        ]
        
        upsert_response = index.upsert(vectors=vectors)
        
        return {
            "symbol": symbol,
            "time_series_id": ts_id,
            "overview_id": ov_id,
            "upsert_response": upsert_response
        }
        
    except Exception as e:
        print(f"Erreur lors de l'indexation des données pour {symbol}: {str(e)}")
        return {"error": str(e)}

def search_similar_stocks(query_vector, index=None, top_k=5):
    """
    Recherche des titres boursiers similaires à partir d'un vecteur de requête.
    
    Args:
        query_vector (np.ndarray): Le vecteur de requête
        index (pinecone.Index, optional): L'index Pinecone
        top_k (int): Nombre de résultats à retourner
        
    Returns:
        dict: Résultats de la recherche
    """
    if index is None:
        index = initialize_pinecone()
    
    # Normaliser le vecteur de requête
    normalized_query = normalize_vector(query_vector)
    
    # Effectuer la recherche
    query_response = index.query(
        vector=normalized_query.tolist(),
        top_k=top_k,
        include_metadata=True
    )
    
    return query_response

def test_alpha_vantage_pinecone_integration():
    """
    Teste l'intégration d'Alpha Vantage et Pinecone avec normalisation.
    """
    print("=== TEST DE L'INTÉGRATION ALPHA VANTAGE ET PINECONE AVEC NORMALISATION ===")
    
    try:
        # Vérifier la clé API Alpha Vantage
        if not ALPHA_VANTAGE_API_KEY:
            print("Erreur: La clé API Alpha Vantage n'est pas définie")
            return
        
        print(f"Clé API Alpha Vantage trouvée: {ALPHA_VANTAGE_API_KEY[:5]}...")
        
        # Initialiser Pinecone
        index = initialize_pinecone()
        
        # Liste des symboles à indexer
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        
        # Indexer les données pour chaque symbole
        for symbol in symbols:
            print(f"\nIndexation des données pour {symbol}...")
            result = index_stock_data(symbol, index)
            print(f"Résultat: {result}")
            
            # Attendre pour éviter de dépasser les limites de l'API
            print("Attente de 15 secondes pour éviter les limites de l'API...")
            time.sleep(15)
        
        # Récupérer les données pour un symbole de test
        print("\nRécupération des données pour AAPL...")
        time_series_data = get_stock_time_series("AAPL")
        
        # Vectoriser et normaliser les données
        print("Vectorisation et normalisation des données...")
        vector = vectorize_time_series(time_series_data)
        normalized_vector = normalize_vector(vector)
        
        print(f"Norme du vecteur original: {np.linalg.norm(vector):.6f}")
        print(f"Norme du vecteur normalisé: {np.linalg.norm(normalized_vector):.6f}")
        
        # Rechercher des titres similaires
        print("\nRecherche de titres similaires...")
        search_results = search_similar_stocks(vector, index)
        
        # Afficher les résultats
        print("\nRésultats de la recherche:")
        for i, match in enumerate(search_results['matches']):
            print(f"Match {i+1}:")
            print(f"  ID: {match['id']}")
            print(f"  Score: {match['score']:.6f}")
            print(f"  Symbole: {match['metadata'].get('symbol', 'N/A')}")
            print(f"  Nom: {match['metadata'].get('name', 'N/A')}")
            print(f"  Type: {match['metadata'].get('type', 'N/A')}")
        
        print("\nTest terminé avec succès!")
        
    except Exception as e:
        print(f"Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpha_vantage_pinecone_integration() 