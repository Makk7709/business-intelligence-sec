"""
Tests unitaires pour le module security_manager.py.
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
import time
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.security_manager import SecurityManager, RateLimiter, CSRFProtection, InputValidator


class TestRateLimiter(unittest.TestCase):
    """
    Tests unitaires pour la classe RateLimiter.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        self.rate_limiter = RateLimiter(max_requests=5, time_window=10)
    
    def test_is_allowed(self):
        """
        Teste la méthode is_allowed.
        """
        # Vérifier que le client est autorisé pour les 5 premières requêtes
        for i in range(5):
            self.assertTrue(self.rate_limiter.is_allowed('client1'))
        
        # Vérifier que le client n'est plus autorisé après 5 requêtes
        self.assertFalse(self.rate_limiter.is_allowed('client1'))
        
        # Vérifier qu'un autre client est autorisé
        self.assertTrue(self.rate_limiter.is_allowed('client2'))
    
    def test_clean_old_requests(self):
        """
        Teste la méthode _clean_old_requests.
        """
        # Ajouter des requêtes
        for i in range(3):
            self.rate_limiter.is_allowed('client1')
        
        # Vérifier que le client a 3 requêtes
        self.assertEqual(len(self.rate_limiter.requests['client1']), 3)
        
        # Nettoyer les anciennes requêtes avec un temps actuel très éloigné
        self.rate_limiter._clean_old_requests(time.time() + 20)
        
        # Vérifier que le client n'a plus de requêtes
        self.assertNotIn('client1', self.rate_limiter.requests)


class TestCSRFProtection(unittest.TestCase):
    """
    Tests unitaires pour la classe CSRFProtection.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        self.csrf_protection = CSRFProtection(secret_key='test_secret_key')
    
    def test_generate_token(self):
        """
        Teste la méthode generate_token.
        """
        # Générer un token
        token = self.csrf_protection.generate_token('session1')
        
        # Vérifier que le token est une chaîne de caractères
        self.assertIsInstance(token, str)
        
        # Vérifier que le token contient un point (séparateur entre le token et la signature)
        self.assertIn('.', token)
    
    def test_validate_token(self):
        """
        Teste la méthode validate_token.
        """
        # Générer un token
        token = self.csrf_protection.generate_token('session1')
        
        # Vérifier que le token est valide pour la même session
        self.assertTrue(self.csrf_protection.validate_token(token, 'session1'))
        
        # Vérifier que le token n'est pas valide pour une autre session
        self.assertFalse(self.csrf_protection.validate_token(token, 'session2'))
        
        # Vérifier qu'un token invalide n'est pas valide
        self.assertFalse(self.csrf_protection.validate_token('invalid_token', 'session1'))
    
    def test_generate_signature(self):
        """
        Teste la méthode _generate_signature.
        """
        # Générer une signature
        signature = self.csrf_protection._generate_signature('token1', 'session1')
        
        # Vérifier que la signature est une chaîne de caractères
        self.assertIsInstance(signature, str)
        
        # Vérifier que la signature est la même pour les mêmes paramètres
        self.assertEqual(signature, self.csrf_protection._generate_signature('token1', 'session1'))
        
        # Vérifier que la signature est différente pour des paramètres différents
        self.assertNotEqual(signature, self.csrf_protection._generate_signature('token2', 'session1'))
        self.assertNotEqual(signature, self.csrf_protection._generate_signature('token1', 'session2'))


class TestInputValidator(unittest.TestCase):
    """
    Tests unitaires pour la classe InputValidator.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        self.input_validator = InputValidator()
    
    def test_validate_string(self):
        """
        Teste la méthode validate_string.
        """
        # Vérifier qu'une chaîne valide est validée
        self.assertTrue(self.input_validator.validate_string('test'))
        
        # Vérifier qu'une chaîne trop courte n'est pas validée
        self.assertFalse(self.input_validator.validate_string('', min_length=1))
        
        # Vérifier qu'une chaîne trop longue n'est pas validée
        self.assertFalse(self.input_validator.validate_string('test', max_length=3))
        
        # Vérifier qu'une chaîne qui ne correspond pas au pattern n'est pas validée
        self.assertFalse(self.input_validator.validate_string('test', pattern=r'^[0-9]+$'))
        
        # Vérifier qu'une chaîne qui correspond au pattern est validée
        self.assertTrue(self.input_validator.validate_string('123', pattern=r'^[0-9]+$'))
        
        # Vérifier qu'un non-string n'est pas validé
        self.assertFalse(self.input_validator.validate_string(123))
    
    def test_validate_integer(self):
        """
        Teste la méthode validate_integer.
        """
        # Vérifier qu'un entier valide est validé
        self.assertTrue(self.input_validator.validate_integer(123))
        
        # Vérifier qu'une chaîne représentant un entier est validée
        self.assertTrue(self.input_validator.validate_integer('123'))
        
        # Vérifier qu'un entier trop petit n'est pas validé
        self.assertFalse(self.input_validator.validate_integer(5, min_value=10))
        
        # Vérifier qu'un entier trop grand n'est pas validé
        self.assertFalse(self.input_validator.validate_integer(15, max_value=10))
        
        # Vérifier qu'une valeur non entière n'est pas validée
        self.assertFalse(self.input_validator.validate_integer('abc'))
    
    def test_validate_float(self):
        """
        Teste la méthode validate_float.
        """
        # Vérifier qu'un float valide est validé
        self.assertTrue(self.input_validator.validate_float(123.45))
        
        # Vérifier qu'une chaîne représentant un float est validée
        self.assertTrue(self.input_validator.validate_float('123.45'))
        
        # Vérifier qu'un float trop petit n'est pas validé
        self.assertFalse(self.input_validator.validate_float(5.5, min_value=10.0))
        
        # Vérifier qu'un float trop grand n'est pas validé
        self.assertFalse(self.input_validator.validate_float(15.5, max_value=10.0))
        
        # Vérifier qu'une valeur non float n'est pas validée
        self.assertFalse(self.input_validator.validate_float('abc'))
    
    def test_validate_email(self):
        """
        Teste la méthode validate_email.
        """
        # Vérifier qu'une adresse e-mail valide est validée
        self.assertTrue(self.input_validator.validate_email('test@example.com'))
        
        # Vérifier qu'une adresse e-mail invalide n'est pas validée
        self.assertFalse(self.input_validator.validate_email('test'))
        self.assertFalse(self.input_validator.validate_email('test@'))
        self.assertFalse(self.input_validator.validate_email('@example.com'))
        
        # Vérifier qu'un non-string n'est pas validé
        self.assertFalse(self.input_validator.validate_email(123))
    
    def test_validate_url(self):
        """
        Teste la méthode validate_url.
        """
        # Vérifier qu'une URL valide est validée
        self.assertTrue(self.input_validator.validate_url('http://example.com'))
        self.assertTrue(self.input_validator.validate_url('https://example.com'))
        
        # Vérifier qu'une URL invalide n'est pas validée
        self.assertFalse(self.input_validator.validate_url('example.com'))
        self.assertFalse(self.input_validator.validate_url('http://'))
        
        # Vérifier qu'un non-string n'est pas validé
        self.assertFalse(self.input_validator.validate_url(123))
    
    def test_sanitize_string(self):
        """
        Teste la méthode sanitize_string.
        """
        # Vérifier que les caractères spéciaux sont échappés
        self.assertEqual(self.input_validator.sanitize_string('<script>alert("XSS")</script>'),
                         '&lt;script&gt;alert(&quot;XSS&quot;)&lt;&#x2F;script&gt;')
        
        # Vérifier qu'un non-string est converti en chaîne vide
        self.assertEqual(self.input_validator.sanitize_string(123), '')


class TestSecurityManager(unittest.TestCase):
    """
    Tests unitaires pour la classe SecurityManager.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        self.security_manager = SecurityManager()
        
        # Créer un mock pour la requête Flask
        self.mock_request = MagicMock()
        self.mock_request.remote_addr = '127.0.0.1'
        self.mock_request.method = 'POST'
        self.mock_request.headers = {'X-CSRF-Token': 'valid_token'}
        
        # Créer un mock pour la session Flask
        self.mock_session = {'id': 'session1'}
    
    @patch('app.core.security_manager.request')
    @patch('app.core.security_manager.session')
    def test_require_csrf_token(self, mock_session, mock_request):
        """
        Teste le décorateur require_csrf_token.
        """
        # Configurer les mocks
        mock_request.method = 'POST'
        mock_request.headers = {'X-CSRF-Token': 'valid_token'}
        mock_session.get.return_value = 'session1'
        
        # Patcher la méthode validate_token
        with patch.object(self.security_manager.csrf_protection, 'validate_token', return_value=True):
            # Créer une fonction décorée
            @self.security_manager.require_csrf_token
            def test_function():
                return 'success'
            
            # Vérifier que la fonction est appelée
            self.assertEqual(test_function(), 'success')
    
    @patch('app.core.security_manager.request')
    def test_limit_rate(self, mock_request):
        """
        Teste le décorateur limit_rate.
        """
        # Configurer le mock
        mock_request.remote_addr = '127.0.0.1'
        
        # Patcher la méthode is_allowed
        with patch.object(self.security_manager.rate_limiter, 'is_allowed', return_value=True):
            # Créer une fonction décorée
            @self.security_manager.limit_rate
            def test_function():
                return 'success'
            
            # Vérifier que la fonction est appelée
            self.assertEqual(test_function(), 'success')
    
    def test_validate_file_upload(self):
        """
        Teste la méthode validate_file_upload.
        """
        # Créer un mock pour un fichier
        mock_file = MagicMock()
        mock_file.filename = 'test.pdf'
        mock_file.seek.return_value = None
        mock_file.tell.return_value = 1024  # 1 KB
        
        # Vérifier qu'un fichier valide est validé
        self.assertIsNone(self.security_manager.validate_file_upload(mock_file, ['pdf'], 2048))
        
        # Vérifier qu'un fichier avec une extension non autorisée n'est pas validé
        mock_file.filename = 'test.doc'
        self.assertIsNotNone(self.security_manager.validate_file_upload(mock_file, ['pdf'], 2048))
        
        # Vérifier qu'un fichier trop volumineux n'est pas validé
        mock_file.filename = 'test.pdf'
        mock_file.tell.return_value = 3072  # 3 KB
        self.assertIsNotNone(self.security_manager.validate_file_upload(mock_file, ['pdf'], 2048))
        
        # Vérifier qu'un fichier sans nom n'est pas validé
        mock_file.filename = ''
        self.assertIsNotNone(self.security_manager.validate_file_upload(mock_file, ['pdf'], 2048))
        
        # Vérifier qu'un fichier None n'est pas validé
        self.assertIsNotNone(self.security_manager.validate_file_upload(None, ['pdf'], 2048))
    
    def test_validate_path(self):
        """
        Teste la méthode validate_path.
        """
        # Créer des répertoires temporaires
        temp_dir1 = tempfile.mkdtemp()
        temp_dir2 = tempfile.mkdtemp()
        
        try:
            # Créer un fichier dans le premier répertoire
            file_path = os.path.join(temp_dir1, 'test.txt')
            with open(file_path, 'w') as f:
                f.write('test')
            
            # Vérifier qu'un chemin valide est validé
            self.assertTrue(self.security_manager.validate_path(file_path, [temp_dir1]))
            
            # Vérifier qu'un chemin dans un répertoire non autorisé n'est pas validé
            self.assertFalse(self.security_manager.validate_path(file_path, [temp_dir2]))
        finally:
            # Supprimer les répertoires temporaires
            shutil.rmtree(temp_dir1)
            shutil.rmtree(temp_dir2)
    
    @patch('app.core.security_manager.session')
    def test_get_csrf_token(self, mock_session):
        """
        Teste la méthode get_csrf_token.
        """
        # Configurer le mock
        mock_session.__contains__.return_value = True
        mock_session.__getitem__.return_value = 'session1'
        
        # Patcher la méthode generate_token
        with patch.object(self.security_manager.csrf_protection, 'generate_token', return_value='token1'):
            # Vérifier que la méthode retourne le token généré
            self.assertEqual(self.security_manager.get_csrf_token(), 'token1')


if __name__ == '__main__':
    unittest.main() 