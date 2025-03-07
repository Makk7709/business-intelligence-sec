"""
Module pour l'intégration avec l'API EDGAR de la SEC.
Ce module permet de télécharger et d'analyser les documents financiers 10-K et 10-Q.
"""

import os
import sys
import time
import logging
import re
import requests
from bs4 import BeautifulSoup
from sec_edgar_downloader import Downloader
from typing import Dict, List, Optional, Tuple, Union

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import (
    DATA_DIR, EDGAR_USER_AGENT, EDGAR_RATE_LIMIT,
    COMPANIES
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class EdgarIntegration:
    """Classe pour l'intégration avec l'API EDGAR de la SEC."""
    
    def __init__(self):
        """Initialise l'intégration avec EDGAR."""
        self.downloader = Downloader(user_agent=EDGAR_USER_AGENT)
        self.data_dir = os.path.join(DATA_DIR, "edgar")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Mapper les tickers aux CIK (Central Index Key)
        self.ticker_to_cik = {
            'AAPL': '0000320193',  # Apple
            'MSFT': '0000789019',  # Microsoft
            'GOOGL': '0001652044',  # Alphabet (Google)
            'AMZN': '0001018724',  # Amazon
            'META': '0001326801'   # Meta (Facebook)
        }
    
    def download_filing(self, ticker: str, filing_type: str = '10-K', count: int = 1) -> str:
        """
        Télécharge un document financier depuis EDGAR.
        
        Args:
            ticker: Le symbole boursier de l'entreprise
            filing_type: Le type de document (10-K, 10-Q, etc.)
            count: Le nombre de documents à télécharger
            
        Returns:
            str: Le chemin vers le répertoire contenant les documents téléchargés
        """
        ticker = ticker.upper()
        
        if ticker not in self.ticker_to_cik:
            logger.error(f"Ticker inconnu: {ticker}")
            raise ValueError(f"Ticker inconnu: {ticker}")
        
        logger.info(f"Téléchargement du document {filing_type} pour {ticker}")
        
        try:
            # Définir le répertoire de sortie
            self.downloader.set_output_dir(self.data_dir)
            
            # Télécharger le document
            self.downloader.get(filing_type, ticker, count)
            
            # Construire le chemin vers le répertoire des documents téléchargés
            output_dir = os.path.join(self.data_dir, "sec-edgar-filings", ticker, filing_type)
            
            if not os.path.exists(output_dir):
                logger.error(f"Le téléchargement a échoué. Le répertoire {output_dir} n'existe pas.")
                raise FileNotFoundError(f"Le téléchargement a échoué. Le répertoire {output_dir} n'existe pas.")
            
            logger.info(f"Document téléchargé avec succès dans {output_dir}")
            return output_dir
            
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du document: {str(e)}")
            raise
    
    def extract_text_from_filing(self, filing_dir: str) -> str:
        """
        Extrait le texte d'un document financier.
        
        Args:
            filing_dir: Le chemin vers le répertoire contenant le document
            
        Returns:
            str: Le texte extrait du document
        """
        logger.info(f"Extraction du texte depuis {filing_dir}")
        
        try:
            # Trouver le fichier HTML complet
            html_files = [f for f in os.listdir(filing_dir) if f.endswith('.html') and not f.startswith('filing-details')]
            
            if not html_files:
                logger.error(f"Aucun fichier HTML trouvé dans {filing_dir}")
                raise FileNotFoundError(f"Aucun fichier HTML trouvé dans {filing_dir}")
            
            # Utiliser le premier fichier HTML trouvé
            html_file = os.path.join(filing_dir, html_files[0])
            
            # Lire le fichier HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extraire le texte avec BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Supprimer les balises script et style
            for script in soup(["script", "style"]):
                script.extract()
            
            # Obtenir le texte
            text = soup.get_text()
            
            # Nettoyer le texte
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            logger.info(f"Texte extrait avec succès ({len(text)} caractères)")
            return text
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
            raise
    
    def extract_financial_data(self, text: str) -> Dict[str, Dict[str, float]]:
        """
        Extrait les données financières du texte.
        
        Args:
            text: Le texte du document financier
            
        Returns:
            Dict: Les données financières extraites
        """
        logger.info("Extraction des données financières du texte")
        
        financial_data = {
            'revenue': {},
            'net_income': {},
            'gross_margin': {}
        }
        
        try:
            # Extraire les revenus
            revenue_pattern = r'(Total net sales|Total revenue|Net sales|Revenue)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)'
            revenue_match = re.search(revenue_pattern, text)
            
            if revenue_match:
                years = [2022, 2023, 2024]  # Années correspondant aux colonnes
                for i, year in enumerate(years):
                    value_str = revenue_match.group(i + 2).replace(',', '')
                    try:
                        value = float(value_str)
                        financial_data['revenue'][year] = value
                    except ValueError:
                        pass
            
            # Extraire la marge brute
            margin_pattern = r'Gross margin percentage\s+([0-9.]+)%\s+([0-9.]+)%\s+([0-9.]+)%'
            margin_match = re.search(margin_pattern, text)
            
            if margin_match:
                years = [2022, 2023, 2024]  # Années correspondant aux colonnes
                for i, year in enumerate(years):
                    try:
                        value = float(margin_match.group(i + 1))
                        financial_data['gross_margin'][year] = value
                    except ValueError:
                        pass
            
            # Extraire le bénéfice net
            income_pattern = r'Net income\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)'
            income_match = re.search(income_pattern, text)
            
            if income_match:
                years = [2022, 2023, 2024]  # Années correspondant aux colonnes
                for i, year in enumerate(years):
                    value_str = income_match.group(i + 1).replace(',', '')
                    try:
                        value = float(value_str)
                        financial_data['net_income'][year] = value
                    except ValueError:
                        pass
            
            logger.info(f"Données financières extraites avec succès: {financial_data}")
            return financial_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données financières: {str(e)}")
            raise
    
    def save_extracted_text(self, ticker: str, text: str) -> str:
        """
        Sauvegarde le texte extrait dans un fichier.
        
        Args:
            ticker: Le symbole boursier de l'entreprise
            text: Le texte à sauvegarder
            
        Returns:
            str: Le chemin vers le fichier sauvegardé
        """
        ticker = ticker.lower()
        output_file = os.path.join(DATA_DIR, f"{ticker}_10k_extracted.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"Texte sauvegardé dans {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du texte: {str(e)}")
            raise
    
    def save_financial_data(self, ticker: str, data: Dict[str, Dict[str, float]]) -> str:
        """
        Sauvegarde les données financières dans un fichier JSON.
        
        Args:
            ticker: Le symbole boursier de l'entreprise
            data: Les données financières à sauvegarder
            
        Returns:
            str: Le chemin vers le fichier sauvegardé
        """
        ticker = ticker.lower()
        output_file = os.path.join(DATA_DIR, f"{ticker}_financials.json")
        
        try:
            import json
            
            # Convertir les clés d'année en chaînes pour la sérialisation JSON
            serializable_data = {}
            for metric, years_data in data.items():
                serializable_data[metric] = {str(year): value for year, value in years_data.items()}
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "name": COMPANIES.get(ticker.upper(), ticker.upper()),
                    "ticker": ticker.upper(),
                    "metrics": serializable_data
                }, f, indent=2)
            
            logger.info(f"Données financières sauvegardées dans {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données financières: {str(e)}")
            raise
    
    def process_company(self, ticker: str, filing_type: str = '10-K') -> Tuple[str, str]:
        """
        Traite les documents financiers d'une entreprise.
        
        Args:
            ticker: Le symbole boursier de l'entreprise
            filing_type: Le type de document (10-K, 10-Q, etc.)
            
        Returns:
            Tuple[str, str]: Les chemins vers les fichiers de texte et de données financières
        """
        logger.info(f"Traitement des documents financiers pour {ticker}")
        
        try:
            # Respecter la limite de taux de l'API EDGAR
            time.sleep(1 / EDGAR_RATE_LIMIT)
            
            # Télécharger le document
            filing_dir = self.download_filing(ticker, filing_type)
            
            # Extraire le texte
            text = self.extract_text_from_filing(filing_dir)
            
            # Sauvegarder le texte
            text_file = self.save_extracted_text(ticker, text)
            
            # Extraire les données financières
            financial_data = self.extract_financial_data(text)
            
            # Sauvegarder les données financières
            data_file = self.save_financial_data(ticker, financial_data)
            
            logger.info(f"Traitement terminé pour {ticker}")
            return text_file, data_file
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des documents pour {ticker}: {str(e)}")
            raise

# Instance singleton de l'intégration EDGAR
edgar_integration = EdgarIntegration() 