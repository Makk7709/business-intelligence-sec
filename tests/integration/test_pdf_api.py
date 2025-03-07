"""
Tests d'intégration pour les routes API de traitement des PDF.
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from io import BytesIO

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.config import UPLOADS_DIR, DATA_DIR


class TestPDFAPI(unittest.TestCase):
    """
    Tests d'intégration pour les routes API de traitement des PDF.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        # Créer des répertoires temporaires
        self.temp_uploads_dir = tempfile.mkdtemp()
        self.temp_extracted_dir = tempfile.mkdtemp()
        
        # Patcher les répertoires pour utiliser les répertoires temporaires
        self.patcher_uploads = patch('app.routes.api.UPLOADS_DIR', self.temp_uploads_dir)
        self.mock_uploads_dir = self.patcher_uploads.start()
        
        self.patcher_data = patch('app.routes.api.DATA_DIR', self.temp_extracted_dir)
        self.mock_data_dir = self.patcher_data.start()
        
        # Patcher le processeur PDF
        self.patcher_pdf = patch('app.routes.api.pdf_processor')
        self.mock_pdf_processor = self.patcher_pdf.start()
        
        # Configurer le mock du processeur PDF
        self.mock_pdf_processor.process_pdf.return_value = (
            os.path.join(self.temp_extracted_dir, 'test_extracted.txt'),
            os.path.join(self.temp_extracted_dir, 'test_financial_data.json')
        )
        
        # Créer le fichier de données financières
        os.makedirs(os.path.dirname(self.mock_pdf_processor.process_pdf.return_value[1]), exist_ok=True)
        with open(self.mock_pdf_processor.process_pdf.return_value[1], 'w') as f:
            json.dump({
                'revenue': 100,
                'gross_margin': 40,
                'net_income': 20
            }, f)
        
        # Créer l'application Flask en mode test
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        
        # Créer un fichier PDF de test
        self.test_pdf_content = b'%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\ntrailer\n<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF'
    
    def tearDown(self):
        """
        Nettoyage après chaque test.
        """
        # Arrêter les patchers
        self.patcher_uploads.stop()
        self.patcher_data.stop()
        self.patcher_pdf.stop()
        
        # Supprimer les répertoires temporaires
        shutil.rmtree(self.temp_uploads_dir)
        shutil.rmtree(self.temp_extracted_dir)
    
    def test_process_pdf(self):
        """
        Teste le traitement d'un fichier PDF.
        """
        # Créer un fichier PDF de test
        data = {
            'file': (BytesIO(self.test_pdf_content), 'test.pdf')
        }
        
        # Envoyer une requête POST pour traiter le fichier PDF
        response = self.client.post(
            '/api/pdf/process',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('text_file', data)
        self.assertIn('data_file', data)
        self.assertIn('financial_data', data)
        self.assertEqual(data['financial_data']['revenue'], 100)
        self.assertEqual(data['financial_data']['gross_margin'], 40)
        self.assertEqual(data['financial_data']['net_income'], 20)
        
        # Vérifier que le processeur PDF a été appelé avec le bon argument
        self.mock_pdf_processor.process_pdf.assert_called_once()
        args, _ = self.mock_pdf_processor.process_pdf.call_args
        self.assertTrue(args[0].endswith('test.pdf'))
    
    def test_process_pdf_no_file(self):
        """
        Teste le traitement sans fichier PDF.
        """
        # Envoyer une requête POST sans fichier
        response = self.client.post('/api/pdf/process')
        
        # Vérifier que la requête a échoué
        self.assertEqual(response.status_code, 400)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_process_pdf_empty_filename(self):
        """
        Teste le traitement avec un nom de fichier vide.
        """
        # Créer un fichier PDF de test avec un nom vide
        data = {
            'file': (BytesIO(self.test_pdf_content), '')
        }
        
        # Envoyer une requête POST pour traiter le fichier PDF
        response = self.client.post(
            '/api/pdf/process',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Vérifier que la requête a échoué
        self.assertEqual(response.status_code, 400)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_process_pdf_invalid_extension(self):
        """
        Teste le traitement avec un fichier non PDF.
        """
        # Créer un fichier non PDF
        data = {
            'file': (BytesIO(b'Not a PDF file'), 'test.txt')
        }
        
        # Envoyer une requête POST pour traiter le fichier
        response = self.client.post(
            '/api/pdf/process',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Vérifier que la requête a échoué
        self.assertEqual(response.status_code, 400)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_process_pdf_too_large(self):
        """
        Teste le traitement avec un fichier trop volumineux.
        """
        # Patcher la taille maximale des fichiers
        with patch('app.routes.api.MAX_UPLOAD_SIZE', 10):  # 10 octets
            # Créer un fichier PDF de test plus grand que la taille maximale
            data = {
                'file': (BytesIO(self.test_pdf_content), 'test.pdf')
            }
            
            # Envoyer une requête POST pour traiter le fichier PDF
            response = self.client.post(
                '/api/pdf/process',
                data=data,
                content_type='multipart/form-data'
            )
            
            # Vérifier que la requête a échoué
            self.assertEqual(response.status_code, 400)
            
            # Vérifier que la réponse contient les informations attendues
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('message', data)
    
    def test_process_pdf_processing_error(self):
        """
        Teste le traitement avec une erreur de traitement.
        """
        # Configurer le mock du processeur PDF pour lever une exception
        self.mock_pdf_processor.process_pdf.side_effect = Exception("Erreur de traitement")
        
        # Créer un fichier PDF de test
        data = {
            'file': (BytesIO(self.test_pdf_content), 'test.pdf')
        }
        
        # Envoyer une requête POST pour traiter le fichier PDF
        response = self.client.post(
            '/api/pdf/process',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Vérifier que la requête a échoué
        self.assertEqual(response.status_code, 500)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)


if __name__ == '__main__':
    unittest.main() 