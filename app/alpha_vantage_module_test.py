import os
import sys
import numpy as np
from dotenv import load_dotenv

print("Démarrage du test du module Alpha Vantage...")

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    print("Erreur: La clé API Alpha Vantage n'est pas définie dans le fichier .env")
    sys.exit(1)

print(f"Clé API Alpha Vantage trouvée: {ALPHA_VANTAGE_API_KEY[:5]}...")

# Importer notre module d'intégration Alpha Vantage
try:
    # Créer le module s'il n'existe pas
    module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alpha_vantage_module.py')
    
    if not os.path.exists(module_path):
        print(f"Création du module Alpha Vantage: {module_path}")
        
        with open(module_path, 'w') as f:
            f.write('''import os
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
''')
        print("Module créé avec succès!")
    
    # Importer le module
    print("Importation du module alpha_vantage_module...")
    from app.alpha_vantage_module import get_stock_time_series, get_company_overview, normalize_vector
    print("Module importé avec succès!")
    
except Exception as e:
    print(f"Erreur lors de l'importation du module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def test_alpha_vantage_module():
    """Test du module Alpha Vantage."""
    print("=== TEST DU MODULE ALPHA VANTAGE ===")
    
    # Symbole à tester
    symbol = "AAPL"
    
    try:
        # Test 1: Récupération des données de séries temporelles
        print("\n1. Test de récupération des données de séries temporelles:")
        time_series_data = get_stock_time_series(symbol, interval="daily", outputsize="compact")
        
        # Extraire les données de séries temporelles
        time_series_key = "Time Series (Daily)"
        if time_series_key not in time_series_data:
            print(f"Données de séries temporelles non trouvées dans la réponse: {time_series_data.keys()}")
            return
        
        # Afficher les premières données
        time_series = time_series_data[time_series_key]
        print(f"Nombre de jours récupérés: {len(time_series)}")
        
        # Afficher les 3 derniers jours
        dates = list(time_series.keys())
        for date in dates[:3]:
            print(f"  {date}: {time_series[date]['4. close']}")
        
        # Test 2: Récupération des informations sur l'entreprise
        print("\n2. Test de récupération des informations sur l'entreprise:")
        overview = get_company_overview(symbol)
        important_fields = ["Symbol", "Name", "Sector", "Industry", "MarketCapitalization"]
        for field in important_fields:
            if field in overview:
                print(f"  {field}: {overview[field]}")
        
        # Test 3: Normalisation de vecteur
        print("\n3. Test de normalisation de vecteur:")
        # Créer un vecteur aléatoire
        vector = np.random.rand(10)
        print(f"Vecteur original: {vector}")
        print(f"Norme du vecteur original: {np.linalg.norm(vector)}")
        
        # Normaliser le vecteur
        normalized_vector = normalize_vector(vector)
        print(f"Vecteur normalisé: {normalized_vector}")
        print(f"Norme du vecteur normalisé: {np.linalg.norm(normalized_vector)}")
        
        print("\nTous les tests ont réussi!")
        
    except Exception as e:
        print(f"Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpha_vantage_module() 