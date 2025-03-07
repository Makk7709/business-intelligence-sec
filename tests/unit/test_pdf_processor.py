"""
Tests unitaires pour le module pdf_processor.py.
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

from app.core.pdf_processor import PDFProcessor


class TestPDFProcessor(unittest.TestCase):
    """
    Tests unitaires pour la classe PDFProcessor.
    """
    
    def setUp(self):
        """
        Configuration avant chaque test.
        """
        # Créer un répertoire temporaire pour les fichiers extraits
        self.temp_dir = tempfile.mkdtemp()
        
        # Créer une instance de PDFProcessor
        self.pdf_processor = PDFProcessor()
        
        # Patcher le répertoire d'extraction pour utiliser le répertoire temporaire
        patcher = patch.object(self.pdf_processor, 'extracted_dir', self.temp_dir)
        self.mock_extracted_dir = patcher.start()
        self.addCleanup(patcher.stop)
        
        # Créer un fichier PDF de test
        self.test_pdf_path = os.path.join(self.temp_dir, 'test.pdf')
        with open(self.test_pdf_path, 'w') as f:
            f.write('Dummy PDF content')
    
    def tearDown(self):
        """
        Nettoyage après chaque test.
        """
        # Supprimer le répertoire temporaire
        shutil.rmtree(self.temp_dir)
    
    @patch('app.core.pdf_processor.extract_text')
    def test_extract_text_from_pdf(self, mock_extract_text):
        """
        Teste l'extraction de texte à partir d'un PDF.
        """
        # Configurer le mock pour retourner un texte de test
        mock_extract_text.return_value = "Test revenue: $100 million\nGross margin: 40%\nNet income: $20 million"
        
        # Extraire le texte
        text = self.pdf_processor.extract_text_from_pdf(self.test_pdf_path)
        
        # Vérifier que la fonction extract_text a été appelée avec le bon argument
        mock_extract_text.assert_called_once_with(self.test_pdf_path)
        
        # Vérifier que le texte extrait est correct
        self.assertEqual(text, "Test revenue: $100 million\nGross margin: 40%\nNet income: $20 million")
    
    def test_extract_financial_data(self):
        """
        Teste l'extraction de données financières à partir du texte.
        """
        # Texte de test
        text = "Test revenue: $100 million\nGross margin: 40%\nNet income: $20 million"
        
        # Extraire les données financières
        financial_data = self.pdf_processor.extract_financial_data(text)
        
        # Vérifier que les données extraites sont correctes
        self.assertEqual(financial_data['revenue'], 100)
        self.assertEqual(financial_data['gross_margin'], 40)
        self.assertEqual(financial_data['net_income'], 20)
    
    def test_save_extracted_text(self):
        """
        Teste la sauvegarde du texte extrait.
        """
        # Texte de test
        text = "Test revenue: $100 million\nGross margin: 40%\nNet income: $20 million"
        
        # Sauvegarder le texte
        filepath = self.pdf_processor.save_extracted_text(text, self.test_pdf_path)
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .txt
        self.assertTrue(filepath.endswith('.txt'))
        
        # Vérifier le contenu du fichier
        with open(filepath, 'r') as f:
            content = f.read()
            self.assertEqual(content, text)
    
    def test_save_financial_data(self):
        """
        Teste la sauvegarde des données financières.
        """
        # Données financières de test
        financial_data = {
            'revenue': 100,
            'gross_margin': 40,
            'net_income': 20
        }
        
        # Sauvegarder les données
        filepath = self.pdf_processor.save_financial_data(financial_data, self.test_pdf_path)
        
        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(filepath))
        
        # Vérifier que le fichier a l'extension .json
        self.assertTrue(filepath.endswith('.json'))
        
        # Vérifier le contenu du fichier
        with open(filepath, 'r') as f:
            content = json.load(f)
            self.assertEqual(content, financial_data)
    
    @patch('app.core.pdf_processor.PDFProcessor.extract_text_from_pdf')
    @patch('app.core.pdf_processor.PDFProcessor.extract_financial_data')
    @patch('app.core.pdf_processor.PDFProcessor.save_extracted_text')
    @patch('app.core.pdf_processor.PDFProcessor.save_financial_data')
    def test_process_pdf(self, mock_save_financial_data, mock_save_extracted_text, mock_extract_financial_data, mock_extract_text_from_pdf):
        """
        Teste le traitement complet d'un PDF.
        """
        # Configurer les mocks
        mock_extract_text_from_pdf.return_value = "Test revenue: $100 million\nGross margin: 40%\nNet income: $20 million"
        mock_extract_financial_data.return_value = {
            'revenue': 100,
            'gross_margin': 40,
            'net_income': 20
        }
        mock_save_extracted_text.return_value = os.path.join(self.temp_dir, 'test_extracted.txt')
        mock_save_financial_data.return_value = os.path.join(self.temp_dir, 'test_financial_data.json')
        
        # Traiter le PDF
        text_filepath, json_filepath = self.pdf_processor.process_pdf(self.test_pdf_path)
        
        # Vérifier que les fonctions ont été appelées avec les bons arguments
        mock_extract_text_from_pdf.assert_called_once_with(self.test_pdf_path)
        mock_extract_financial_data.assert_called_once_with(mock_extract_text_from_pdf.return_value)
        mock_save_extracted_text.assert_called_once_with(mock_extract_text_from_pdf.return_value, self.test_pdf_path)
        mock_save_financial_data.assert_called_once_with(mock_extract_financial_data.return_value, self.test_pdf_path)
        
        # Vérifier que les chemins de fichiers retournés sont corrects
        self.assertEqual(text_filepath, mock_save_extracted_text.return_value)
        self.assertEqual(json_filepath, mock_save_financial_data.return_value)


if __name__ == '__main__':
    unittest.main() 