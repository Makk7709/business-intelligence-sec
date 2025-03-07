"""
Module pour l'intégration avec l'API Alpha Vantage.
Ce module permet de récupérer des données financières en temps réel et historiques.
"""

import os
import sys
import time
import logging
import json
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional, Tuple, Union, Any

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import (
    DATA_DIR, ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_RATE_LIMIT,
    COMPANIES
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AlphaVantageIntegration:
    """Classe pour l'intégration avec l'API Alpha Vantage."""
    
    def __init__(self):
        """Initialise l'intégration avec Alpha Vantage."""
        self.api_key = ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.data_dir = os.path.join(DATA_DIR, "alpha_vantage")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Vérifier si la clé API est configurée
        if not self.api_key or self.api_key == "demo":
            logger.warning("La clé API Alpha Vantage n'est pas configurée ou utilise la valeur par défaut 'demo'.")
    
    def _make_request(self, function: str, symbol: str, **kwargs) -> Dict[str, Any]:
        """
        Effectue une requête à l'API Alpha Vantage.
        
        Args:
            function: La fonction Alpha Vantage à appeler
            symbol: Le symbole boursier de l'entreprise
            **kwargs: Paramètres supplémentaires pour la requête
            
        Returns:
            Dict[str, Any]: Les données retournées par l'API
        """
        # Respecter la limite de taux de l'API Alpha Vantage
        time.sleep(60 / ALPHA_VANTAGE_RATE_LIMIT)
        
        # Construire les paramètres de la requête
        params = {
            "function": function,
            "symbol": symbol,
            "apikey": self.api_key,
            **kwargs
        }
        
        logger.info(f"Requête Alpha Vantage: {function} pour {symbol}")
        
        try:
            # Effectuer la requête
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Analyser la réponse JSON
            data = response.json()
            
            # Vérifier si la réponse contient une erreur
            if "Error Message" in data:
                logger.error(f"Erreur Alpha Vantage: {data['Error Message']}")
                raise ValueError(f"Erreur Alpha Vantage: {data['Error Message']}")
            
            # Vérifier si la limite de requêtes a été atteinte
            if "Note" in data and "API call frequency" in data["Note"]:
                logger.warning(f"Limite de requêtes Alpha Vantage atteinte: {data['Note']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur de requête Alpha Vantage: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Erreur de valeur Alpha Vantage: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erreur inattendue Alpha Vantage: {str(e)}")
            raise
    
    def get_time_series_daily(self, symbol: str, outputsize: str = "compact") -> pd.DataFrame:
        """
        Récupère les données de série temporelle quotidienne pour un symbole.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            outputsize: La taille de sortie (compact ou full)
            
        Returns:
            pd.DataFrame: Les données de série temporelle
        """
        # Vérifier si les données sont déjà en cache
        cache_file = os.path.join(self.data_dir, f"{symbol.lower()}_daily_{outputsize}.json")
        
        # Si le fichier de cache existe et a moins de 24 heures, l'utiliser
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < 86400:
            logger.info(f"Utilisation des données en cache pour {symbol}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Sinon, effectuer la requête
            data = self._make_request(
                function="TIME_SERIES_DAILY",
                symbol=symbol,
                outputsize=outputsize
            )
            
            # Sauvegarder les données en cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        # Convertir les données en DataFrame
        if "Time Series (Daily)" not in data:
            logger.error(f"Données de série temporelle non trouvées pour {symbol}")
            raise ValueError(f"Données de série temporelle non trouvées pour {symbol}")
        
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        
        # Convertir les colonnes en nombres
        for col in df.columns:
            df[col] = pd.to_numeric(df[col])
        
        # Renommer les colonnes
        df.columns = [col.split(". ")[1] for col in df.columns]
        
        # Ajouter une colonne de date
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        
        return df
    
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère les informations générales sur une entreprise.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            
        Returns:
            Dict[str, Any]: Les informations sur l'entreprise
        """
        # Vérifier si les données sont déjà en cache
        cache_file = os.path.join(self.data_dir, f"{symbol.lower()}_overview.json")
        
        # Si le fichier de cache existe et a moins de 7 jours, l'utiliser
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < 604800:
            logger.info(f"Utilisation des données en cache pour {symbol}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Sinon, effectuer la requête
            data = self._make_request(
                function="OVERVIEW",
                symbol=symbol
            )
            
            # Sauvegarder les données en cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère les états financiers d'une entreprise.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            
        Returns:
            Dict[str, Any]: Les états financiers
        """
        # Vérifier si les données sont déjà en cache
        cache_file = os.path.join(self.data_dir, f"{symbol.lower()}_income_statement.json")
        
        # Si le fichier de cache existe et a moins de 30 jours, l'utiliser
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < 2592000:
            logger.info(f"Utilisation des données en cache pour {symbol}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Sinon, effectuer la requête
            data = self._make_request(
                function="INCOME_STATEMENT",
                symbol=symbol
            )
            
            # Sauvegarder les données en cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère le bilan d'une entreprise.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            
        Returns:
            Dict[str, Any]: Le bilan
        """
        # Vérifier si les données sont déjà en cache
        cache_file = os.path.join(self.data_dir, f"{symbol.lower()}_balance_sheet.json")
        
        # Si le fichier de cache existe et a moins de 30 jours, l'utiliser
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < 2592000:
            logger.info(f"Utilisation des données en cache pour {symbol}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Sinon, effectuer la requête
            data = self._make_request(
                function="BALANCE_SHEET",
                symbol=symbol
            )
            
            # Sauvegarder les données en cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère le tableau des flux de trésorerie d'une entreprise.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            
        Returns:
            Dict[str, Any]: Le tableau des flux de trésorerie
        """
        # Vérifier si les données sont déjà en cache
        cache_file = os.path.join(self.data_dir, f"{symbol.lower()}_cash_flow.json")
        
        # Si le fichier de cache existe et a moins de 30 jours, l'utiliser
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < 2592000:
            logger.info(f"Utilisation des données en cache pour {symbol}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Sinon, effectuer la requête
            data = self._make_request(
                function="CASH_FLOW",
                symbol=symbol
            )
            
            # Sauvegarder les données en cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère les bénéfices trimestriels et annuels d'une entreprise.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            
        Returns:
            Dict[str, Any]: Les bénéfices
        """
        # Vérifier si les données sont déjà en cache
        cache_file = os.path.join(self.data_dir, f"{symbol.lower()}_earnings.json")
        
        # Si le fichier de cache existe et a moins de 7 jours, l'utiliser
        if os.path.exists(cache_file) and (time.time() - os.path.getmtime(cache_file)) < 604800:
            logger.info(f"Utilisation des données en cache pour {symbol}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Sinon, effectuer la requête
            data = self._make_request(
                function="EARNINGS",
                symbol=symbol
            )
            
            # Sauvegarder les données en cache
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        
        return data
    
    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Récupère toutes les données financières d'une entreprise.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            
        Returns:
            Dict[str, Any]: Les données financières
        """
        logger.info(f"Récupération des données financières pour {symbol}")
        
        try:
            # Récupérer les différentes données
            overview = self.get_company_overview(symbol)
            income_statement = self.get_income_statement(symbol)
            balance_sheet = self.get_balance_sheet(symbol)
            cash_flow = self.get_cash_flow(symbol)
            earnings = self.get_earnings(symbol)
            
            # Combiner les données
            financial_data = {
                "overview": overview,
                "income_statement": income_statement,
                "balance_sheet": balance_sheet,
                "cash_flow": cash_flow,
                "earnings": earnings
            }
            
            # Sauvegarder les données combinées
            output_file = os.path.join(self.data_dir, f"{symbol.lower()}_financial_data.json")
            with open(output_file, 'w') as f:
                json.dump(financial_data, f, indent=2)
            
            logger.info(f"Données financières récupérées avec succès pour {symbol}")
            return financial_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données financières pour {symbol}: {str(e)}")
            raise
    
    def extract_key_metrics(self, symbol: str) -> Dict[str, Dict[str, float]]:
        """
        Extrait les métriques clés des données financières.
        
        Args:
            symbol: Le symbole boursier de l'entreprise
            
        Returns:
            Dict[str, Dict[str, float]]: Les métriques clés
        """
        logger.info(f"Extraction des métriques clés pour {symbol}")
        
        try:
            # Récupérer les données financières
            financial_data = self.get_financial_data(symbol)
            
            # Extraire les métriques clés
            metrics = {
                'revenue': {},
                'net_income': {},
                'gross_margin': {},
                'operating_income': {},
                'eps': {},
                'pe_ratio': {},
                'dividend_yield': {},
                'debt_to_equity': {},
                'roe': {},
                'roa': {}
            }
            
            # Extraire les métriques de l'aperçu
            overview = financial_data['overview']
            metrics['pe_ratio'][2024] = float(overview.get('PERatio', 0))
            metrics['dividend_yield'][2024] = float(overview.get('DividendYield', 0)) * 100
            
            # Extraire les métriques des états financiers
            income_statement = financial_data['income_statement']
            annual_reports = income_statement.get('annualReports', [])
            
            for i, report in enumerate(annual_reports[:3]):  # Utiliser les 3 derniers rapports
                year = 2024 - i  # Année actuelle - i
                
                # Extraire les métriques
                total_revenue = float(report.get('totalRevenue', 0))
                gross_profit = float(report.get('grossProfit', 0))
                operating_income = float(report.get('operatingIncome', 0))
                net_income = float(report.get('netIncome', 0))
                
                # Calculer les métriques
                metrics['revenue'][year] = total_revenue
                metrics['net_income'][year] = net_income
                metrics['operating_income'][year] = operating_income
                
                # Calculer la marge brute
                if total_revenue > 0:
                    metrics['gross_margin'][year] = (gross_profit / total_revenue) * 100
                
                # Extraire le BPA
                metrics['eps'][year] = float(report.get('reportedEPS', 0))
            
            # Extraire les métriques du bilan
            balance_sheet = financial_data['balance_sheet']
            annual_reports = balance_sheet.get('annualReports', [])
            
            for i, report in enumerate(annual_reports[:3]):  # Utiliser les 3 derniers rapports
                year = 2024 - i  # Année actuelle - i
                
                # Extraire les métriques
                total_assets = float(report.get('totalAssets', 0))
                total_liabilities = float(report.get('totalLiabilities', 0))
                total_shareholder_equity = float(report.get('totalShareholderEquity', 0))
                
                # Calculer les métriques
                if total_shareholder_equity > 0:
                    metrics['debt_to_equity'][year] = (total_liabilities / total_shareholder_equity) * 100
                
                # Calculer le ROE et le ROA
                if year in metrics['net_income']:
                    net_income = metrics['net_income'][year]
                    if total_shareholder_equity > 0:
                        metrics['roe'][year] = (net_income / total_shareholder_equity) * 100
                    if total_assets > 0:
                        metrics['roa'][year] = (net_income / total_assets) * 100
            
            # Sauvegarder les métriques
            output_file = os.path.join(self.data_dir, f"{symbol.lower()}_key_metrics.json")
            
            # Convertir les clés d'année en chaînes pour la sérialisation JSON
            serializable_metrics = {}
            for metric, years_data in metrics.items():
                serializable_metrics[metric] = {str(year): value for year, value in years_data.items()}
            
            with open(output_file, 'w') as f:
                json.dump({
                    "name": COMPANIES.get(symbol.upper(), symbol.upper()),
                    "ticker": symbol.upper(),
                    "metrics": serializable_metrics
                }, f, indent=2)
            
            logger.info(f"Métriques clés extraites avec succès pour {symbol}")
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des métriques clés pour {symbol}: {str(e)}")
            raise

# Instance singleton de l'intégration Alpha Vantage
alpha_vantage_integration = AlphaVantageIntegration() 