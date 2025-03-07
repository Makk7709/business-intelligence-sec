"""
Configuration centralisée pour l'application.
Ce fichier contient toutes les constantes et paramètres de configuration.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Chemins des répertoires
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, 'app')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
STATIC_DIR = os.path.join(APP_DIR, 'static')
TEMPLATES_DIR = os.path.join(APP_DIR, 'templates')
COMM_DIR = os.path.join(APP_DIR, 'comm')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
EXPORTS_DIR = os.path.join(DATA_DIR, 'exports')

# Créer les répertoires s'ils n'existent pas
for directory in [DATA_DIR, LOGS_DIR, COMM_DIR, UPLOADS_DIR, EXPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuration de l'application Flask
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5115
FLASK_DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Chemins des fichiers
STATIC_HTML_PATH = os.path.join(APP_DIR, 'ui', 'dashboard_static.html')
LOG_FILE = os.path.join(LOGS_DIR, 'app.log')
AI_BRIDGE_LOG_FILE = os.path.join(LOGS_DIR, 'ai_bridge.log')

# Fichiers de communication
QUERY_FILE = os.path.join(COMM_DIR, 'query.json')
RESPONSE_FILE = os.path.join(COMM_DIR, 'response.json')
STATUS_FILE = os.path.join(COMM_DIR, 'status.json')

# Configuration des API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV', 'gcp-starter')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'financial-docs')

# Configuration de l'IA
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '150'))

# Configuration LangChain
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
LANGCHAIN_ENDPOINT = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'financial-analysis')

# Configuration Alpha Vantage
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
ALPHA_VANTAGE_RATE_LIMIT = 5  # Requêtes par minute pour la version gratuite

# Configuration EDGAR
EDGAR_USER_AGENT = os.getenv("EDGAR_USER_AGENT", "financial-dashboard@example.com")
EDGAR_RATE_LIMIT = 10  # Requêtes par seconde selon les directives de la SEC

# Configuration des exportations
EXPORT_FORMATS = ['csv', 'pdf', 'excel', 'json']
PDF_TEMPLATE_PATH = os.path.join(APP_DIR, 'templates', 'pdf_report_template.html')
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'csv', 'xls', 'xlsx'}

# Données financières
FINANCIAL_CONTEXT = """
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

# Configuration des chemins
RESULTS_DIR = os.path.join(DATA_DIR, "results")
PREDICTIONS_DIR = os.path.join(DATA_DIR, "predictions")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")

# Configuration des entreprises
COMPANIES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com, Inc.",
    "META": "Meta Platforms, Inc."
}

# Configuration des métriques
METRICS = {
    "revenue": "Revenus",
    "net_income": "Bénéfice net",
    "gross_margin": "Marge brute",
    "operating_income": "Résultat d'exploitation",
    "eps": "Bénéfice par action",
    "pe_ratio": "Ratio cours/bénéfice",
    "dividend_yield": "Rendement du dividende",
    "debt_to_equity": "Ratio d'endettement",
    "roe": "Rentabilité des capitaux propres",
    "roa": "Rentabilité des actifs"
}

# Configuration des années
YEARS = ["2020", "2021", "2022", "2023", "2024"]

# Configuration des prédictions
PREDICTION_YEARS_AHEAD = 3
PREDICTION_CONFIDENCE_THRESHOLD = 0.7

# Configuration de sécurité
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_ENABLED = True
CSRF_SECRET_KEY = os.getenv('CSRF_SECRET_KEY', os.urandom(24).hex())

# Configuration des timeouts
API_TIMEOUT = 30  # secondes
LONG_OPERATION_TIMEOUT = 300  # secondes 