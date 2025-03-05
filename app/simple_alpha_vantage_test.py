import os
import sys
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_API_KEY:
    print("Erreur: La clé API Alpha Vantage n'est pas définie dans le fichier .env")
    sys.exit(1)

print(f"Clé API Alpha Vantage trouvée: {ALPHA_VANTAGE_API_KEY[:5]}...")

# URL de base pour l'API Alpha Vantage
BASE_URL = "https://www.alphavantage.co/query"

def test_alpha_vantage_api():
    """Test simple de l'API Alpha Vantage."""
    print("=== TEST SIMPLE DE L'API ALPHA VANTAGE ===")
    
    # Symbole à tester
    symbol = "AAPL"
    
    # Test 1: Récupération des données de séries temporelles
    print("\n1. Test de récupération des données de séries temporelles:")
    
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        # Vérifier les erreurs
        if "Error Message" in data:
            print(f"Erreur API: {data['Error Message']}")
            return
        
        # Extraire les données de séries temporelles
        time_series_key = "Time Series (Daily)"
        if time_series_key not in data:
            print(f"Données de séries temporelles non trouvées dans la réponse: {data.keys()}")
            return
        
        # Afficher les premières données
        time_series = data[time_series_key]
        print(f"Nombre de jours récupérés: {len(time_series)}")
        
        # Afficher les 3 derniers jours
        dates = list(time_series.keys())
        for date in dates[:3]:
            print(f"  {date}: {time_series[date]}")
        
        print("\nTest réussi!")
        
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpha_vantage_api() 