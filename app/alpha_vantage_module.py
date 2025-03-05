import os
import requests
import numpy as np
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("La clé API Alpha Vantage n'est pas définie dans le fichier .env")

# URL de base pour l'API Alpha Vantage
BASE_URL = "https://www.alphavantage.co/query"

def get_stock_time_series(symbol, interval="daily", outputsize="compact"):
    """
    Récupère les données de séries temporelles pour un symbole boursier.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
        interval (str): L'intervalle de temps ('daily', 'weekly', 'monthly')
        outputsize (str): La taille de sortie ('compact' = 100 derniers points, 'full' = 20+ ans)
    
    Returns:
        dict: Dictionnaire contenant les données de séries temporelles
    """
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
    
    return data

def get_company_overview(symbol):
    """
    Récupère les informations générales sur une entreprise.
    
    Args:
        symbol (str): Le symbole boursier (ex: AAPL, MSFT)
    
    Returns:
        dict: Dictionnaire contenant les informations sur l'entreprise
    """
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

def normalize_vector(vector):
    """
    Normalise un vecteur pour qu'il ait une norme unitaire.
    
    Args:
        vector (list/numpy.ndarray): Le vecteur à normaliser
    
    Returns:
        numpy.ndarray: Le vecteur normalisé
    """
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
