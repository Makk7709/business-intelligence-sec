"""
Tests d'intégration pour les routes API d'exportation.
"""

import os
import sys
import unittest
import json
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.config import EXPORTS_DIR, DATA_DIR


class TestExportAPI(unittest.TestCase):
    """
    Tests d'intégration pour les routes API d'exportation.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        # Créer un répertoire temporaire pour les exports
        self.temp_dir = tempfile.mkdtemp()
        
        # Patcher le répertoire d'exports pour utiliser le répertoire temporaire
        self.patcher_exports = patch('app.routes.api.EXPORTS_DIR', self.temp_dir)
        self.mock_exports_dir = self.patcher_exports.start()
        
        # Patcher le répertoire de données pour utiliser le répertoire temporaire
        self.patcher_data = patch('app.routes.api.DATA_DIR', self.temp_dir)
        self.mock_data_dir = self.patcher_data.start()
        
        # Créer l'application Flask en mode test
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        
        # Données de test
        self.test_data = {
            "name": "Test Company",
            "ticker": "TEST",
            "metrics": {
                "revenue": {
                    "years": [2020, 2021, 2022],
                    "values": [100, 120, 150]
                },
                "net_income": {
                    "years": [2020, 2021, 2022],
                    "values": [10, 15, 20]
                }
            }
        }
    
    def tearDown(self):
        """
        Nettoyage après chaque test.
        """
        # Arrêter les patchers
        self.patcher_exports.stop()
        self.patcher_data.stop()
        
        # Supprimer le répertoire temporaire
        shutil.rmtree(self.temp_dir)
    
    def test_export_data_csv(self):
        """
        Teste l'exportation de données au format CSV.
        """
        # Envoyer une requête POST pour exporter les données au format CSV
        response = self.client.post(
            '/api/export/csv',
            json=self.test_data,
            query_string={'filename': 'test_export'}
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('filepath', data)
        self.assertTrue(data['filepath'].endswith('.csv'))
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(data['filepath']))
    
    def test_export_data_excel(self):
        """
        Teste l'exportation de données au format Excel.
        """
        # Envoyer une requête POST pour exporter les données au format Excel
        response = self.client.post(
            '/api/export/excel',
            json=self.test_data,
            query_string={'filename': 'test_export'}
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('filepath', data)
        self.assertTrue(data['filepath'].endswith('.xlsx'))
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(data['filepath']))
    
    def test_export_data_pdf(self):
        """
        Teste l'exportation de données au format PDF.
        """
        # Envoyer une requête POST pour exporter les données au format PDF
        response = self.client.post(
            '/api/export/pdf',
            json=self.test_data,
            query_string={'filename': 'test_export'}
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('filepath', data)
        self.assertTrue(data['filepath'].endswith('.pdf'))
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(data['filepath']))
    
    def test_export_data_json(self):
        """
        Teste l'exportation de données au format JSON.
        """
        # Envoyer une requête POST pour exporter les données au format JSON
        response = self.client.post(
            '/api/export/json',
            json=self.test_data,
            query_string={'filename': 'test_export'}
        )
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('filepath', data)
        self.assertTrue(data['filepath'].endswith('.json'))
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(data['filepath']))
        
        # Vérifier le contenu du fichier
        with open(data['filepath'], 'r') as f:
            content = json.load(f)
            self.assertEqual(content, self.test_data)
    
    def test_export_data_invalid_format(self):
        """
        Teste l'exportation de données avec un format invalide.
        """
        # Envoyer une requête POST pour exporter les données avec un format invalide
        response = self.client.post(
            '/api/export/invalid_format',
            json=self.test_data,
            query_string={'filename': 'test_export'}
        )
        
        # Vérifier que la requête a échoué
        self.assertEqual(response.status_code, 400)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_export_data_no_data(self):
        """
        Teste l'exportation sans données.
        """
        # Envoyer une requête POST pour exporter sans données
        response = self.client.post(
            '/api/export/csv',
            json=None,
            query_string={'filename': 'test_export'}
        )
        
        # Vérifier que la requête a échoué
        self.assertEqual(response.status_code, 400)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_export_company_data(self):
        """
        Teste l'exportation des données d'une entreprise.
        """
        # Patcher la fonction load_company_data pour retourner des données de test
        with patch('app.routes.api.load_company_data') as mock_load_company_data:
            # Configurer le mock pour retourner un objet avec les attributs nécessaires
            mock_company = MagicMock()
            mock_company.name = "Test Company"
            mock_company.ticker = "TEST"
            mock_company.metrics = {
                "revenue": MagicMock(get_years=lambda: [2020, 2021, 2022], get_values=lambda: [100, 120, 150]),
                "net_income": MagicMock(get_years=lambda: [2020, 2021, 2022], get_values=lambda: [10, 15, 20])
            }
            mock_load_company_data.return_value = mock_company
            
            # Envoyer une requête GET pour exporter les données d'une entreprise au format CSV
            response = self.client.get(
                '/api/export/company/test/csv',
                query_string={'filename': 'test_company_export'}
            )
            
            # Vérifier que la requête a réussi
            self.assertEqual(response.status_code, 200)
            
            # Vérifier que la réponse contient les informations attendues
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('filepath', data)
            self.assertTrue(data['filepath'].endswith('.csv'))
            
            # Vérifier que le fichier a été créé
            self.assertTrue(os.path.exists(data['filepath']))
    
    def test_export_comparative_data(self):
        """
        Teste l'exportation des données comparatives.
        """
        # Patcher la fonction load_comparative_data pour retourner des données de test
        with patch('app.routes.api.load_comparative_data') as mock_load_comparative_data:
            # Configurer le mock pour retourner un objet avec les attributs nécessaires
            mock_comparative = MagicMock()
            mock_comparative.years = [2020, 2021, 2022]
            mock_comparative.companies = ["AAPL", "MSFT"]
            mock_comparative.metrics = ["revenue", "net_income"]
            mock_comparative.get_metric_for_company = lambda company, metric: {
                2020: 100 if company == "AAPL" else 200,
                2021: 120 if company == "AAPL" else 220,
                2022: 150 if company == "AAPL" else 250
            }
            mock_load_comparative_data.return_value = mock_comparative
            
            # Envoyer une requête GET pour exporter les données comparatives au format CSV
            response = self.client.get(
                '/api/export/comparative/csv',
                query_string={'filename': 'test_comparative_export'}
            )
            
            # Vérifier que la requête a réussi
            self.assertEqual(response.status_code, 200)
            
            # Vérifier que la réponse contient les informations attendues
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('filepath', data)
            self.assertTrue(data['filepath'].endswith('.csv'))
            
            # Vérifier que le fichier a été créé
            self.assertTrue(os.path.exists(data['filepath']))
    
    def test_download_file(self):
        """
        Teste le téléchargement d'un fichier.
        """
        # Créer un fichier de test
        test_file_path = os.path.join(self.temp_dir, 'test_file.txt')
        with open(test_file_path, 'w') as f:
            f.write('Test file content')
        
        # Envoyer une requête GET pour télécharger le fichier
        response = self.client.get(f'/api/download/{test_file_path}')
        
        # Vérifier que la requête a réussi
        self.assertEqual(response.status_code, 200)
        
        # Vérifier que le contenu du fichier est correct
        self.assertEqual(response.data, b'Test file content')
    
    def test_download_file_not_found(self):
        """
        Teste le téléchargement d'un fichier inexistant.
        """
        # Envoyer une requête GET pour télécharger un fichier inexistant
        response = self.client.get('/api/download/nonexistent_file.txt')
        
        # Vérifier que la requête a échoué
        self.assertEqual(response.status_code, 404)
        
        # Vérifier que la réponse contient les informations attendues
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('message', data)
    
    def test_download_file_unauthorized(self):
        """
        Teste le téléchargement d'un fichier non autorisé.
        """
        # Créer un fichier de test en dehors des répertoires autorisés
        unauthorized_dir = tempfile.mkdtemp()
        test_file_path = os.path.join(unauthorized_dir, 'test_file.txt')
        with open(test_file_path, 'w') as f:
            f.write('Test file content')
        
        try:
            # Envoyer une requête GET pour télécharger le fichier
            response = self.client.get(f'/api/download/{test_file_path}')
            
            # Vérifier que la requête a échoué
            self.assertEqual(response.status_code, 403)
            
            # Vérifier que la réponse contient les informations attendues
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('message', data)
        finally:
            # Supprimer le répertoire temporaire
            shutil.rmtree(unauthorized_dir)


if __name__ == '__main__':
    unittest.main() 