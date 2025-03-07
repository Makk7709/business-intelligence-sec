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

# Ajouter le répertoire courant au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def is_port_in_use(port):
    """Vérifie si un port est déjà utilisé."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Tue le processus qui utilise un port spécifique."""
    if not is_port_in_use(port):
        return True
    
    try:
        if sys.platform.startswith('win'):
            cmd = f'netstat -ano | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True).decode()
            if output:
                pid = output.strip().split()[-1]
                subprocess.call(f'taskkill /F /PID {pid}', shell=True)
        else:
            cmd = f'lsof -i :{port} -t'
            pid = subprocess.check_output(cmd, shell=True).decode().strip()
            if pid:
                subprocess.call(f'kill -9 {pid}', shell=True)
        
        # Vérifier si le port est libéré
        time.sleep(1)
        return not is_port_in_use(port)
    except Exception as e:
        logger.error(f"Erreur lors de la tentative de libération du port {port}: {e}")
        return False

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Lance l\'application d\'analyse financière.')
    parser.add_argument('--port', type=int, default=5115, help='Port sur lequel lancer l\'application')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Hôte sur lequel lancer l\'application')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    parser.add_argument('--no-ai', action='store_true', help='Désactiver le pont IA')
    
    args = parser.parse_args()
    
    # Vérifier si le port est déjà utilisé
    if is_port_in_use(args.port):
        logger.warning(f"Le port {args.port} est déjà utilisé. Tentative de libération...")
        if not kill_process_on_port(args.port):
            logger.error(f"Impossible de libérer le port {args.port}. Veuillez choisir un autre port.")
            return 1
    
    # Définir les variables d'environnement
    os.environ['FLASK_HOST'] = args.host
    os.environ['FLASK_PORT'] = str(args.port)
    os.environ['FLASK_DEBUG'] = str(args.debug).lower()
    os.environ['DISABLE_AI'] = str(args.no_ai).lower()
    
    # Lancer l'application
    try:
        from app.app import main as app_main
        app_main()
        return 0
    except Exception as e:
        logger.error(f"Erreur lors du lancement de l'application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 