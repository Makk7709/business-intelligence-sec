"""
Module pour gérer la sécurité de l'application.
Ce module fournit des fonctionnalités pour valider les entrées, protéger contre les attaques CSRF et XSS,
et limiter le taux de requêtes.
"""

import os
import sys
import logging
import re
import time
import hashlib
import secrets
import functools
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from flask import request, abort, session, jsonify

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import LOGS_DIR, CSRF_SECRET_KEY, SESSION_COOKIE_SECURE, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'security.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Classe pour limiter le taux de requêtes.
    """
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialise le limiteur de taux.
        
        Args:
            max_requests: Nombre maximum de requêtes autorisées dans la fenêtre de temps
            time_window: Fenêtre de temps en secondes
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Vérifie si le client est autorisé à effectuer une requête.
        
        Args:
            client_id: Identifiant du client (adresse IP, etc.)
            
        Returns:
            True si le client est autorisé, False sinon
        """
        current_time = time.time()
        
        # Nettoyer les anciennes requêtes
        self._clean_old_requests(current_time)
        
        # Vérifier si le client a déjà effectué des requêtes
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Vérifier si le client a dépassé la limite
        if len(self.requests[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False
        
        # Ajouter la requête
        self.requests[client_id].append(current_time)
        return True
    
    def _clean_old_requests(self, current_time: float):
        """
        Nettoie les anciennes requêtes.
        
        Args:
            current_time: Temps actuel
        """
        for client_id in list(self.requests.keys()):
            # Supprimer les requêtes plus anciennes que la fenêtre de temps
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if current_time - req_time < self.time_window
            ]
            
            # Supprimer le client s'il n'a plus de requêtes
            if not self.requests[client_id]:
                del self.requests[client_id]


class CSRFProtection:
    """
    Classe pour protéger contre les attaques CSRF.
    """
    
    def __init__(self, secret_key: str = None):
        """
        Initialise la protection CSRF.
        
        Args:
            secret_key: Clé secrète pour générer les tokens CSRF
        """
        self.secret_key = secret_key or CSRF_SECRET_KEY or secrets.token_hex(16)
    
    def generate_token(self, session_id: str) -> str:
        """
        Génère un token CSRF.
        
        Args:
            session_id: Identifiant de session
            
        Returns:
            Token CSRF
        """
        # Générer un token aléatoire
        token = secrets.token_hex(16)
        
        # Calculer la signature
        signature = self._generate_signature(token, session_id)
        
        # Retourner le token complet
        return f"{token}.{signature}"
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """
        Valide un token CSRF.
        
        Args:
            token: Token CSRF
            session_id: Identifiant de session
            
        Returns:
            True si le token est valide, False sinon
        """
        try:
            # Séparer le token et la signature
            token_part, signature_part = token.split('.')
            
            # Calculer la signature attendue
            expected_signature = self._generate_signature(token_part, session_id)
            
            # Vérifier la signature
            return signature_part == expected_signature
        except Exception as e:
            logger.error(f"Error validating CSRF token: {str(e)}")
            return False
    
    def _generate_signature(self, token: str, session_id: str) -> str:
        """
        Génère une signature pour un token CSRF.
        
        Args:
            token: Token CSRF
            session_id: Identifiant de session
            
        Returns:
            Signature
        """
        # Créer une signature en utilisant HMAC
        message = f"{token}{session_id}{self.secret_key}"
        return hashlib.sha256(message.encode()).hexdigest()


class InputValidator:
    """
    Classe pour valider les entrées utilisateur.
    """
    
    @staticmethod
    def validate_string(value: str, min_length: int = 0, max_length: int = 1000, pattern: str = None) -> bool:
        """
        Valide une chaîne de caractères.
        
        Args:
            value: Valeur à valider
            min_length: Longueur minimale
            max_length: Longueur maximale
            pattern: Expression régulière à vérifier
            
        Returns:
            True si la valeur est valide, False sinon
        """
        if not isinstance(value, str):
            return False
        
        if len(value) < min_length or len(value) > max_length:
            return False
        
        if pattern and not re.match(pattern, value):
            return False
        
        return True
    
    @staticmethod
    def validate_integer(value: Any, min_value: int = None, max_value: int = None) -> bool:
        """
        Valide un entier.
        
        Args:
            value: Valeur à valider
            min_value: Valeur minimale
            max_value: Valeur maximale
            
        Returns:
            True si la valeur est valide, False sinon
        """
        try:
            int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                return False
            
            if max_value is not None and int_value > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_float(value: Any, min_value: float = None, max_value: float = None) -> bool:
        """
        Valide un nombre à virgule flottante.
        
        Args:
            value: Valeur à valider
            min_value: Valeur minimale
            max_value: Valeur maximale
            
        Returns:
            True si la valeur est valide, False sinon
        """
        try:
            float_value = float(value)
            
            if min_value is not None and float_value < min_value:
                return False
            
            if max_value is not None and float_value > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_email(value: str) -> bool:
        """
        Valide une adresse e-mail.
        
        Args:
            value: Adresse e-mail à valider
            
        Returns:
            True si l'adresse e-mail est valide, False sinon
        """
        if not isinstance(value, str):
            return False
        
        # Expression régulière pour valider une adresse e-mail
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def validate_url(value: str) -> bool:
        """
        Valide une URL.
        
        Args:
            value: URL à valider
            
        Returns:
            True si l'URL est valide, False sinon
        """
        if not isinstance(value, str):
            return False
        
        # Expression régulière pour valider une URL
        pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Nettoie une chaîne de caractères pour éviter les attaques XSS.
        
        Args:
            value: Chaîne de caractères à nettoyer
            
        Returns:
            Chaîne de caractères nettoyée
        """
        if not isinstance(value, str):
            return ""
        
        # Remplacer les caractères spéciaux par leurs entités HTML
        value = value.replace('&', '&amp;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&#x27;')
        value = value.replace('/', '&#x2F;')
        
        return value


class SecurityManager:
    """
    Classe pour gérer la sécurité de l'application.
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de sécurité.
        """
        self.rate_limiter = RateLimiter()
        self.csrf_protection = CSRFProtection()
        self.input_validator = InputValidator()
    
    def require_csrf_token(self, f: Callable) -> Callable:
        """
        Décorateur pour exiger un token CSRF valide.
        
        Args:
            f: Fonction à décorer
            
        Returns:
            Fonction décorée
        """
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifier si la requête est une requête POST, PUT, DELETE ou PATCH
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                # Récupérer le token CSRF
                token = request.headers.get('X-CSRF-Token')
                
                # Vérifier si le token est présent
                if not token:
                    logger.warning("CSRF token missing")
                    abort(403, "CSRF token missing")
                
                # Vérifier si le token est valide
                if not self.csrf_protection.validate_token(token, session.get('id', '')):
                    logger.warning("Invalid CSRF token")
                    abort(403, "Invalid CSRF token")
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def limit_rate(self, f: Callable) -> Callable:
        """
        Décorateur pour limiter le taux de requêtes.
        
        Args:
            f: Fonction à décorer
            
        Returns:
            Fonction décorée
        """
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Récupérer l'adresse IP du client
            client_id = request.remote_addr
            
            # Vérifier si le client est autorisé
            if not self.rate_limiter.is_allowed(client_id):
                logger.warning(f"Rate limit exceeded for client {client_id}")
                return jsonify({
                    'success': False,
                    'message': "Rate limit exceeded. Please try again later."
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def validate_file_upload(self, file, allowed_extensions: List[str], max_size: int) -> Union[str, None]:
        """
        Valide un fichier téléchargé.
        
        Args:
            file: Fichier à valider
            allowed_extensions: Extensions autorisées
            max_size: Taille maximale en octets
            
        Returns:
            Message d'erreur si le fichier est invalide, None sinon
        """
        # Vérifier si le fichier existe
        if not file:
            return "No file provided"
        
        # Vérifier si le fichier a un nom
        if file.filename == '':
            return "No file selected"
        
        # Vérifier l'extension du fichier
        ext = os.path.splitext(file.filename)[1].lower()[1:]
        if ext not in allowed_extensions:
            return f"File type not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
        
        # Vérifier la taille du fichier
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return f"File too large. Maximum size: {max_size / (1024 * 1024):.1f} MB"
        
        return None
    
    def validate_path(self, path: str, allowed_dirs: List[str]) -> bool:
        """
        Valide un chemin de fichier.
        
        Args:
            path: Chemin à valider
            allowed_dirs: Répertoires autorisés
            
        Returns:
            True si le chemin est valide, False sinon
        """
        # Vérifier si le chemin est absolu
        abs_path = os.path.abspath(path)
        
        # Vérifier si le chemin est dans un répertoire autorisé
        return any(os.path.abspath(d) in abs_path for d in allowed_dirs)
    
    def get_csrf_token(self) -> str:
        """
        Récupère un token CSRF.
        
        Returns:
            Token CSRF
        """
        # Vérifier si la session a un identifiant
        if 'id' not in session:
            session['id'] = secrets.token_hex(16)
        
        # Générer un token CSRF
        return self.csrf_protection.generate_token(session['id'])


# Créer une instance du gestionnaire de sécurité
security_manager = SecurityManager() 