#!/usr/bin/env python3
"""
Script pour lancer l'application.
"""

import os
import sys
import argparse
import logging
import subprocess
import time
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Ajouter le répertoire courant au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Répertoires
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, 'app')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
VENV_DIR = os.path.join(BASE_DIR, '.venv')
VENV_PYTHON = os.path.join(VENV_DIR, 'bin', 'python')

# Créer les répertoires s'ils n'existent pas
for directory in [DATA_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)


def parse_args():
    """
    Parse les arguments de la ligne de commande.
    
    Returns:
        Arguments parsés
    """
    parser = argparse.ArgumentParser(description='Lancer l\'application Business Intelligence SEC')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    parser.add_argument('--host', default='127.0.0.1', help='Hôte sur lequel lancer l\'application')
    parser.add_argument('--port', type=int, default=5115, help='Port sur lequel lancer l\'application')
    parser.add_argument('--no-browser', action='store_true', help='Ne pas ouvrir le navigateur automatiquement')
    parser.add_argument('--profile', action='store_true', help='Activer le profilage des performances')
    parser.add_argument('--test', action='store_true', help='Exécuter les tests')
    return parser.parse_args()


def create_venv():
    """
    Crée un environnement virtuel Python s'il n'existe pas déjà.
    """
    if not os.path.exists(VENV_DIR):
        logger.info("Création de l'environnement virtuel...")
        subprocess.run([sys.executable, '-m', 'venv', VENV_DIR], check=True)
        logger.info("Environnement virtuel créé avec succès.")
    else:
        logger.info("L'environnement virtuel existe déjà.")


def install_dependencies():
    """
    Installe les dépendances Python.
    """
    logger.info("Installation des dépendances...")
    
    # Installer les dépendances principales
    try:
        subprocess.run([VENV_PYTHON, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        logger.info("Dépendances installées avec succès.")
    except subprocess.CalledProcessError:
        logger.warning("Erreur lors de l'installation des dépendances principales.")
        logger.info("Tentative d'installation des dépendances essentielles...")
        
        # Installer les dépendances essentielles
        try:
            subprocess.run([VENV_PYTHON, '-m', 'pip', 'install', 'flask', 'python-dotenv'], check=True)
            logger.info("Dépendances essentielles installées avec succès.")
        except subprocess.CalledProcessError:
            logger.error("Erreur lors de l'installation des dépendances essentielles.")
            sys.exit(1)


def create_env_file():
    """
    Crée un fichier .env s'il n'existe pas déjà.
    """
    if not os.path.exists('.env'):
        logger.info("Création du fichier .env...")
        with open('.env', 'w') as f:
            f.write("# Configuration de l'application\n")
            f.write("DEBUG=False\n")
            f.write("FLASK_HOST=127.0.0.1\n")
            f.write("FLASK_PORT=5115\n")
            f.write("\n")
            f.write("# Clés API\n")
            f.write("OPENAI_API_KEY=\n")
            f.write("PINECONE_API_KEY=\n")
            f.write("PINECONE_ENV=gcp-starter\n")
            f.write("ALPHA_VANTAGE_API_KEY=\n")
            f.write("EDGAR_USER_AGENT=your-email@example.com\n")
            f.write("\n")
            f.write("# Sécurité\n")
            f.write(f"SECRET_KEY={os.urandom(24).hex()}\n")
            f.write("CSRF_SECRET_KEY={os.urandom(24).hex()}\n")
        logger.info("Fichier .env créé avec succès.")
    else:
        logger.info("Le fichier .env existe déjà.")


def run_tests(verbose=False):
    """
    Exécute les tests unitaires et d'intégration.
    
    Args:
        verbose: Afficher les détails des tests
    
    Returns:
        True si tous les tests ont réussi, False sinon
    """
    logger.info("Exécution des tests...")
    
    try:
        cmd = [VENV_PYTHON, 'tests/run_tests.py']
        if verbose:
            cmd.append('--verbose')
        
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            logger.info("Tous les tests ont réussi.")
            return True
        else:
            logger.error("Certains tests ont échoué.")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution des tests: {str(e)}")
        return False


def run_app(host='127.0.0.1', port=5115, debug=False, open_browser=True, profile=False):
    """
    Lance l'application Flask.
    
    Args:
        host: Hôte sur lequel lancer l'application
        port: Port sur lequel lancer l'application
        debug: Activer le mode debug
        open_browser: Ouvrir le navigateur automatiquement
        profile: Activer le profilage des performances
    """
    logger.info(f"Lancement de l'application sur {host}:{port} (debug={debug}, profile={profile})...")
    
    # Construire la commande
    cmd = [VENV_PYTHON, 'app/run_direct.py', '--host', host, '--port', str(port)]
    
    if debug:
        cmd.append('--debug')
    
    if not open_browser:
        cmd.append('--no-browser')
    
    if profile:
        cmd.append('--profile')
    
    # Lancer l'application
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        logger.info("Application arrêtée par l'utilisateur.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du lancement de l'application: {str(e)}")
        sys.exit(1)


def main():
    """
    Fonction principale.
    """
    # Parser les arguments
    args = parse_args()
    
    # Créer l'environnement virtuel
    create_venv()
    
    # Installer les dépendances
    install_dependencies()
    
    # Créer le fichier .env
    create_env_file()
    
    # Exécuter les tests si demandé
    if args.test:
        success = run_tests(verbose=args.debug)
        if not success:
            logger.warning("Les tests ont échoué. L'application peut ne pas fonctionner correctement.")
    
    # Lancer l'application
    run_app(
        host=args.host,
        port=args.port,
        debug=args.debug,
        open_browser=not args.no_browser,
        profile=args.profile
    )


if __name__ == '__main__':
    main() 