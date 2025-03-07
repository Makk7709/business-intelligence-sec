"""
Module pour gérer le pont IA.
"""

import os
import sys
import subprocess
import time
import logging
import json
import signal
from typing import Optional, Dict, Any

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import (
    QUERY_FILE, RESPONSE_FILE, STATUS_FILE,
    AI_BRIDGE_LOG_FILE, LOGS_DIR
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=os.path.join(LOGS_DIR, 'ai_manager.log')
)
logger = logging.getLogger(__name__)

class AIManager:
    """Gestionnaire pour le pont IA."""
    
    def __init__(self):
        """Initialise le gestionnaire."""
        self.process = None
        self.bridge_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'ai_bridge.py'
        ))
    
    def start(self) -> bool:
        """
        Démarre le pont IA.
        
        Returns:
            bool: True si le démarrage a réussi, False sinon
        """
        # Vérifier si le pont IA est déjà en cours d'exécution
        if self.is_running():
            logger.info("Le pont IA est déjà en cours d'exécution.")
            return True
        
        # Vérifier si le fichier du pont IA existe
        if not os.path.exists(self.bridge_path):
            logger.error(f"Le fichier du pont IA n'existe pas: {self.bridge_path}")
            return False
        
        try:
            # Créer le répertoire de logs s'il n'existe pas
            os.makedirs(LOGS_DIR, exist_ok=True)
            
            # Démarrer le processus du pont IA
            self.process = subprocess.Popen(
                [sys.executable, self.bridge_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            logger.info(f"Processus du pont IA démarré avec PID: {self.process.pid}")
            
            # Attendre que le pont IA soit prêt
            for _ in range(10):  # Attendre jusqu'à 10 secondes
                if os.path.exists(STATUS_FILE):
                    try:
                        with open(STATUS_FILE, 'r') as f:
                            status = json.load(f)
                        if status.get('status') == 'ready':
                            logger.info("Le pont IA est prêt.")
                            return True
                    except Exception as e:
                        logger.warning(f"Erreur lors de la lecture du statut du pont IA: {str(e)}")
                
                time.sleep(1)
            
            logger.warning("Le pont IA n'est pas devenu prêt dans le délai imparti.")
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du pont IA: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        Arrête le pont IA.
        
        Returns:
            bool: True si l'arrêt a réussi, False sinon
        """
        if not self.process:
            logger.info("Aucun processus du pont IA à arrêter.")
            return True
        
        try:
            # Envoyer un signal SIGTERM au processus
            self.process.terminate()
            
            # Attendre que le processus se termine
            try:
                self.process.wait(timeout=5)
                logger.info("Processus du pont IA arrêté.")
                self.process = None
                return True
            except subprocess.TimeoutExpired:
                # Si le processus ne se termine pas, envoyer un signal SIGKILL
                logger.warning("Le processus du pont IA ne répond pas. Envoi d'un signal SIGKILL.")
                self.process.kill()
                self.process.wait(timeout=5)
                logger.info("Processus du pont IA tué.")
                self.process = None
                return True
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du pont IA: {str(e)}")
            return False
    
    def restart(self) -> bool:
        """
        Redémarre le pont IA.
        
        Returns:
            bool: True si le redémarrage a réussi, False sinon
        """
        self.stop()
        return self.start()
    
    def is_running(self) -> bool:
        """
        Vérifie si le pont IA est en cours d'exécution.
        
        Returns:
            bool: True si le pont IA est en cours d'exécution, False sinon
        """
        # Vérifier si le processus existe et est en cours d'exécution
        if self.process and self.process.poll() is None:
            return True
        
        # Vérifier si le fichier de statut existe
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r') as f:
                    status = json.load(f)
                
                # Vérifier si le statut est 'ready' ou 'processing'
                if status.get('status') in ['ready', 'processing']:
                    # Vérifier si le timestamp est récent (moins de 60 secondes)
                    if time.time() - status.get('timestamp', 0) < 60:
                        return True
            except Exception:
                pass
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtient le statut du pont IA.
        
        Returns:
            Dict[str, Any]: Le statut du pont IA
        """
        if not os.path.exists(STATUS_FILE):
            return {
                'status': 'stopped',
                'message': "Le pont IA n'est pas en cours d'exécution.",
                'timestamp': time.time()
            }
        
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Erreur lors de la lecture du statut du pont IA: {str(e)}",
                'timestamp': time.time()
            }
    
    def send_query(self, query: str, query_type: str = 'openai') -> Dict[str, Any]:
        """
        Envoie une requête au pont IA.
        
        Args:
            query: La requête à envoyer
            query_type: Le type de requête (openai, langchain, pinecone)
            
        Returns:
            Dict[str, Any]: La réponse du pont IA
        """
        # Vérifier si le pont IA est en cours d'exécution
        if not self.is_running():
            logger.warning("Le pont IA n'est pas en cours d'exécution. Tentative de démarrage...")
            if not self.start():
                return {
                    "response": "Impossible de démarrer le pont IA. Veuillez réessayer plus tard.",
                    "query": query,
                    "source": "error"
                }
        
        try:
            # Écrire la requête dans le fichier de communication
            with open(QUERY_FILE, 'w') as f:
                json.dump({
                    'query': query,
                    'type': query_type,
                    'timestamp': time.time()
                }, f)
            
            logger.info(f"Requête envoyée au pont IA: {query[:50]}...")
            
            # Attendre la réponse
            for _ in range(30):  # Attendre jusqu'à 30 secondes
                if os.path.exists(RESPONSE_FILE):
                    try:
                        with open(RESPONSE_FILE, 'r') as f:
                            response = json.load(f)
                        
                        # Supprimer le fichier de réponse
                        os.remove(RESPONSE_FILE)
                        
                        logger.info(f"Réponse reçue du pont IA: {response.get('response', '')[:50]}...")
                        return response
                    except Exception as e:
                        logger.warning(f"Erreur lors de la lecture de la réponse du pont IA: {str(e)}")
                
                time.sleep(1)
            
            logger.warning("Aucune réponse reçue du pont IA dans le délai imparti.")
            return {
                "response": "Aucune réponse reçue du pont IA dans le délai imparti. Veuillez réessayer plus tard.",
                "query": query,
                "source": "error"
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la requête au pont IA: {str(e)}")
            return {
                "response": f"Erreur lors de l'envoi de la requête au pont IA: {str(e)}",
                "query": query,
                "source": "error"
            }

# Instance singleton du gestionnaire
ai_manager = AIManager() 