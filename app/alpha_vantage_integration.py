import os
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time
import json

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("La clé API Alpha Vantage n'est pas définie dans le fichier .env")

# URL de base pour l'API Alpha Vantage
BASE_URL = "https://www.alphavantage.co/query"

# Limites de l'API Alpha Vantage (5 appels par minute, 500 par jour)
MAX_CALLS_PER_MINUTE = 5
CALLS_COUNTER = 0
LAST_CALL_TIME = None

def manage_api_rate_limit():
    """Gère les limites de taux de l'API Alpha Vantage."""
    global CALLS_COUNTER, LAST_CALL_TIME
    
    current_time = datetime.now()
    
    # Initialiser le compteur si c'est le premier appel
    if LAST_CALL_TIME is None:
        LAST_CALL_TIME = current_time
        CALLS_COUNTER = 1
        return
    
    # Réinitialiser le compteur si une minute s'est écoulée
    if (current_time - LAST_CALL_TIME) > timedelta(minutes=1):
        CALLS_COUNTER = 1
        LAST_CALL_TIME = current_time
    else:
        CALLS_COUNTER += 1
        
        # Si nous avons atteint la limite, attendre jusqu'à la prochaine minute
        if CALLS_COUNTER > MAX_CALLS_PER_MINUTE:
            wait_time = 60 - (current_time - LAST_CALL_TIME).seconds
            print(f"Limite d'API atteinte. Attente de {wait_time} secondes...")
            time.sleep(wait_time)
            CALLS_COUNTER = 1
            LAST_CALL_TIME = datetime.now()

def get_stock_time_series(symbol, interval="daily", outputsize="compact"):
    """
    Récupère les données de séries temporelles pour un symbole boursier.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
        interval (str): L'intervalle de temps ('daily', 'weekly', 'monthly')
        outputsize (str): La taille de sortie ('compact' = 100 derniers points, 'full' = 20+ ans)
    
    Returns:
        pandas.DataFrame: DataFrame contenant les données de séries temporelles
    """
    manage_api_rate_limit()
    
    function_name = f"TIME_SERIES_{interval.upper()}"
    
    params = {
        "function": function_name,
        "symbol": symbol,
        "outputsize": outputsize,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    # Extraire les données de séries temporelles
    time_series_key = f"Time Series ({interval.capitalize()})"
    if time_series_key not in data:
        time_series_key = next((k for k in data.keys() if "Time Series" in k), None)
        if not time_series_key:
            raise ValueError(f"Données de séries temporelles non trouvées dans la réponse: {data.keys()}")
    
    # Convertir en DataFrame
    df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
    
    # Renommer les colonnes pour supprimer les préfixes
    df.columns = [col.split(". ")[1] if ". " in col else col for col in df.columns]
    
    # Convertir les colonnes en nombres
    for col in df.columns:
        df[col] = pd.to_numeric(df[col])
    
    # Ajouter une colonne de date et trier
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    
    return df

def get_company_overview(symbol):
    """
    Récupère les informations générales sur une entreprise.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
    
    Returns:
        dict: Dictionnaire contenant les informations sur l'entreprise
    """
    manage_api_rate_limit()
    
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if not data or "Error Message" in data:
        raise ValueError(f"Erreur API: {data.get('Error Message', 'Aucune donnée retournée')}")
    
    return data

def get_income_statement(symbol):
    """
    Récupère les états financiers (compte de résultat) d'une entreprise.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
    
    Returns:
        dict: Dictionnaire contenant les données du compte de résultat
    """
    manage_api_rate_limit()
    
    params = {
        "function": "INCOME_STATEMENT",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    return data

def get_balance_sheet(symbol):
    """
    Récupère le bilan financier d'une entreprise.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
    
    Returns:
        dict: Dictionnaire contenant les données du bilan
    """
    manage_api_rate_limit()
    
    params = {
        "function": "BALANCE_SHEET",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    return data

def get_cash_flow(symbol):
    """
    Récupère le tableau des flux de trésorerie d'une entreprise.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
    
    Returns:
        dict: Dictionnaire contenant les données des flux de trésorerie
    """
    manage_api_rate_limit()
    
    params = {
        "function": "CASH_FLOW",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    return data

def get_earnings(symbol):
    """
    Récupère les données de bénéfices trimestriels et annuels d'une entreprise.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
    
    Returns:
        dict: Dictionnaire contenant les données de bénéfices
    """
    manage_api_rate_limit()
    
    params = {
        "function": "EARNINGS",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    return data

def search_company(keywords):
    """
    Recherche des entreprises par mots-clés.
    
    Args:
        keywords (str): Mots-clés pour la recherche
    
    Returns:
        list: Liste des entreprises correspondantes
    """
    manage_api_rate_limit()
    
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": keywords,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    return data.get("bestMatches", [])

def get_news_sentiment(symbol=None, topics=None):
    """
    Récupère les actualités et le sentiment pour un symbole ou un sujet.
    
    Args:
        symbol (str, optional): Le symbole boursier (ex: AAPL, MSFT)
        topics (str, optional): Sujets d'actualité (ex: technology, finance)
    
    Returns:
        dict: Dictionnaire contenant les actualités et les sentiments
    """
    manage_api_rate_limit()
    
    params = {
        "function": "NEWS_SENTIMENT",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    if symbol:
        params["tickers"] = symbol
    
    if topics:
        params["topics"] = topics
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    return data

def get_sector_performance():
    """
    Récupère les performances des secteurs du marché.
    
    Returns:
        dict: Dictionnaire contenant les performances des secteurs
    """
    manage_api_rate_limit()
    
    params = {
        "function": "SECTOR",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    # Vérifier les erreurs
    if "Error Message" in data:
        raise ValueError(f"Erreur API: {data['Error Message']}")
    
    return data

# Fonction pour convertir les données financières en vecteurs
def financial_data_to_vector(data, vector_size=1536):
    """
    Convertit les données financières en un vecteur normalisé.
    
    Args:
        data (dict/DataFrame): Données financières à vectoriser
        vector_size (int): Taille du vecteur de sortie
    
    Returns:
        numpy.ndarray: Vecteur normalisé
    """
    # Convertir les données en une représentation plate
    if isinstance(data, pd.DataFrame):
        # Pour les séries temporelles, utiliser les valeurs numériques
        flat_data = data.values.flatten()
    elif isinstance(data, dict):
        # Pour les données structurées, extraire les valeurs numériques
        flat_data = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                flat_data.append(value)
            elif isinstance(value, str):
                try:
                    # Essayer de convertir les chaînes en nombres
                    flat_data.append(float(value))
                except (ValueError, TypeError):
                    # Ignorer les valeurs non numériques
                    pass
    else:
        raise ValueError("Type de données non pris en charge")
    
    # S'assurer que nous avons des données
    if not flat_data:
        raise ValueError("Aucune donnée numérique trouvée pour la vectorisation")
    
    # Convertir en tableau numpy
    vector = np.array(flat_data, dtype=np.float32)
    
    # Redimensionner le vecteur à la taille souhaitée
    if len(vector) < vector_size:
        # Padding avec des zéros si trop petit
        vector = np.pad(vector, (0, vector_size - len(vector)), 'constant')
    elif len(vector) > vector_size:
        # Tronquer si trop grand
        vector = vector[:vector_size]
    
    # Normaliser le vecteur
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    
    return vector

# Exemple d'utilisation
if __name__ == "__main__":
    try:
        # Exemple de récupération de données pour Apple
        symbol = "AAPL"
        
        # Récupérer les données de séries temporelles
        time_series = get_stock_time_series(symbol, interval="daily", outputsize="compact")
        print(f"Données de séries temporelles pour {symbol}:")
        print(time_series.head())
        
        # Récupérer les informations sur l'entreprise
        overview = get_company_overview(symbol)
        print(f"\nInformations sur {symbol}:")
        for key, value in list(overview.items())[:5]:  # Afficher les 5 premières informations
            print(f"{key}: {value}")
        
        # Vectoriser les données
        vector = financial_data_to_vector(time_series)
        print(f"\nVecteur normalisé (premiers éléments):")
        print(vector[:10])
        print(f"Norme du vecteur: {np.linalg.norm(vector)}")
        
    except Exception as e:
        print(f"Erreur: {e}") 