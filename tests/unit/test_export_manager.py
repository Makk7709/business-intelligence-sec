"""
Tests unitaires pour le module export_manager.py.
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

from app.core.export_manager import ExportManager


class TestExportManager(unittest.TestCase):
    """
    Tests unitaires pour la classe ExportManager.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        # Créer un répertoire temporaire pour les exports
        self.temp_dir = tempfile.mkdtemp()
        
        # Créer une instance de ExportManager avec le répertoire temporaire
        self.export_manager = ExportManager()
        
        # Patcher le répertoire d'exports pour utiliser le répertoire temporaire
        patcher = patch('app.core.export_manager.EXPORTS_DIR', self.temp_dir)
        self.mock_exports_dir = patcher.start()
        self.addCleanup(patcher.stop)
        
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
        # Supprimer le répertoire temporaire
        shutil.rmtree(self.temp_dir)
    
    def test_export_to_csv(self):
        """
        Teste l'exportation au format CSV.
        """
        # Exporter les données au format CSV
        filepath = self.export_manager.export_to_csv(self.test_data, "test_export")
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .csv
        self.assertTrue(filepath.endswith('.csv'))
        
        # Vérifier le contenu du fichier
        with open(filepath, 'r') as f:
            content = f.read()
            
            # Vérifier que les en-têtes sont présents
            self.assertIn("Year", content)
            self.assertIn("revenue", content)
            self.assertIn("net_income", content)
            
            # Vérifier que les données sont présentes
            self.assertIn("2020", content)
            self.assertIn("100", content)
            self.assertIn("10", content)
    
    def test_export_to_excel(self):
        """
        Teste l'exportation au format Excel.
        """
        # Exporter les données au format Excel
        filepath = self.export_manager.export_to_excel(self.test_data, "test_export")
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .xlsx
        self.assertTrue(filepath.endswith('.xlsx'))
    
    def test_export_to_pdf(self):
        """
        Teste l'exportation au format PDF.
        """
        # Exporter les données au format PDF
        filepath = self.export_manager.export_to_pdf(self.test_data, "test_export")
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .pdf
        self.assertTrue(filepath.endswith('.pdf'))
    
    def test_export_data_csv(self):
        """
        Teste la méthode export_data avec le format CSV.
        """
        # Exporter les données au format CSV
        filepath = self.export_manager.export_data(self.test_data, "csv", "test_export")
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .csv
        self.assertTrue(filepath.endswith('.csv'))
    
    def test_export_data_excel(self):
        """
        Teste la méthode export_data avec le format Excel.
        """
        # Exporter les données au format Excel
        filepath = self.export_manager.export_data(self.test_data, "excel", "test_export")
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .xlsx
        self.assertTrue(filepath.endswith('.xlsx'))
    
    def test_export_data_pdf(self):
        """
        Teste la méthode export_data avec le format PDF.
        """
        # Exporter les données au format PDF
        filepath = self.export_manager.export_data(self.test_data, "pdf", "test_export")
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .pdf
        self.assertTrue(filepath.endswith('.pdf'))
    
    def test_export_data_json(self):
        """
        Teste la méthode export_data avec le format JSON.
        """
        # Exporter les données au format JSON
        filepath = self.export_manager.export_data(self.test_data, "json", "test_export")
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .json
        self.assertTrue(filepath.endswith('.json'))
        
        # Vérifier le contenu du fichier
        with open(filepath, 'r') as f:
            content = json.load(f)
            
            # Vérifier que les données sont correctes
            self.assertEqual(content["name"], self.test_data["name"])
            self.assertEqual(content["ticker"], self.test_data["ticker"])
            self.assertEqual(content["metrics"]["revenue"]["years"], self.test_data["metrics"]["revenue"]["years"])
            self.assertEqual(content["metrics"]["revenue"]["values"], self.test_data["metrics"]["revenue"]["values"])
    
    def test_export_data_invalid_format(self):
        """
        Teste la méthode export_data avec un format invalide.
        """
        # Vérifier qu'une exception est levée pour un format invalide
        with self.assertRaises(ValueError):
            self.export_manager.export_data(self.test_data, "invalid_format", "test_export")


if __name__ == '__main__':
    unittest.main() 