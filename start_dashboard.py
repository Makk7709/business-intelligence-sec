#!/usr/bin/env python3
"""
Script de démarrage simplifié pour le dashboard financier.
Ce script lance l'application sur le port 5115 et ouvre automatiquement le navigateur.
"""

import os
import sys
import time
import signal
import socket
import webbrowser
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
PORT = 5115
URL = f"http://127.0.0.1:{PORT}"
SCRIPT_PATH = os.path.join("app", "run_direct.py")

def is_port_in_use(port):
    """Vérifie si le port est déjà utilisé."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_process_on_port(port):
    """Tue le processus qui utilise le port spécifié."""
    try:
        if sys.platform.startswith('win'):
            cmd = f"FOR /F \"tokens=5\" %P IN ('netstat -ano | findstr :{port}') DO taskkill /F /PID %P"
            os.system(cmd)
        else:
            cmd = f"lsof -i :{port} -t | xargs kill -9"
            os.system(cmd)
        time.sleep(1)  # Attendre que le processus soit terminé
        return True
    except Exception as e:
        print(f"Erreur lors de la tentative de libération du port {port}: {e}")
        return False

def check_openai_api_key():
    """Vérifie si la clé API OpenAI est configurée."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("\n" + "!" * 80)
        print("AVERTISSEMENT: Clé API OpenAI non trouvée.")
        print("L'assistant IA utilisera des réponses prédéfinies au lieu de l'API OpenAI.")
        print("Pour utiliser l'API OpenAI, créez un fichier .env à la racine du projet avec:")
        print("OPENAI_API_KEY=votre_clé_api_ici")
        print("!" * 80 + "\n")
        return False
    else:
        print("\n" + "*" * 80)
        print("INFO: Clé API OpenAI trouvée.")
        print("L'assistant IA utilisera l'API OpenAI pour générer des réponses personnalisées.")
        print("*" * 80 + "\n")
        return True

def main():
    """Fonction principale qui lance l'application."""
    # Vérifier si le script existe
    if not os.path.exists(SCRIPT_PATH):
        print(f"Erreur: Le fichier {SCRIPT_PATH} n'existe pas.")
        print("Veuillez vous assurer que vous êtes dans le répertoire racine du projet.")
        return 1

    # Vérifier si la clé API OpenAI est configurée
    check_openai_api_key()

    # Vérifier si le port est déjà utilisé
    if is_port_in_use(PORT):
        print(f"Le port {PORT} est déjà utilisé. Tentative de libération...")
        if not kill_process_on_port(PORT):
            print(f"Impossible de libérer le port {PORT}. Veuillez fermer l'application qui l'utilise.")
            return 1
        print(f"Port {PORT} libéré avec succès.")

    # Lancer l'application
    print("=" * 80)
    print(f"Démarrage du dashboard financier sur le port {PORT}")
    print("=" * 80)
    
    try:
        # Lancer le script en arrière-plan
        if sys.platform.startswith('win'):
            process = subprocess.Popen([sys.executable, SCRIPT_PATH], 
                                      creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            process = subprocess.Popen([sys.executable, SCRIPT_PATH],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
        
        # Attendre que le serveur démarre
        print("Démarrage du serveur en cours...")
        time.sleep(2)
        
        # Vérifier si le serveur a démarré correctement
        if is_port_in_use(PORT):
            print(f"Serveur démarré avec succès sur le port {PORT}")
            print(f"Ouverture du navigateur à l'adresse: {URL}")
            webbrowser.open(URL)
            print("\nPour arrêter le serveur, appuyez sur Ctrl+C dans cette fenêtre.")
            
            # Garder le script en cours d'exécution
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nArrêt du serveur...")
                process.terminate()
                time.sleep(1)
                if is_port_in_use(PORT):
                    kill_process_on_port(PORT)
                print("Serveur arrêté.")
        else:
            print("Erreur: Le serveur n'a pas démarré correctement.")
            return 1
            
    except Exception as e:
        print(f"Erreur lors du lancement de l'application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 