"""
Module pour charger les données financières depuis différentes sources.
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple

# Ajouter le répertoire parent au chemin d'importation
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import DATA_DIR
from app.models.financial_data import (
    CompanyFinancials, MetricSeries, ComparativeAnalysis,
    FinancialPrediction, PredictionSeries
)

def extract_financial_data_from_text(text: str, company_name: str, ticker: str) -> CompanyFinancials:
    """
    Extrait les données financières à partir d'un texte brut.
    
    Args:
        text: Le texte contenant les données financières
        company_name: Le nom de l'entreprise
        ticker: Le symbole boursier de l'entreprise
        
    Returns:
        Un objet CompanyFinancials contenant les données extraites
    """
    # Créer l'objet CompanyFinancials
    financials = CompanyFinancials(name=company_name, ticker=ticker)
    
    # Extraire les revenus
    revenue_match = re.search(r'(Total net sales|Total revenue)\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)', text)
    if revenue_match:
        revenue_series = MetricSeries(name="revenue")
        years = [2022, 2023, 2024]  # Années correspondant aux colonnes
        for i, year in enumerate(years):
            value_str = revenue_match.group(i + 2).replace(',', '')
            try:
                value = float(value_str)
                revenue_series.add_metric(year, value)
            except ValueError:
                pass
        financials.add_metric_series("revenue", revenue_series)
    
    # Extraire la marge brute
    margin_match = re.search(r'Gross margin percentage\s+([0-9.]+)%\s+([0-9.]+)%\s+([0-9.]+)%', text)
    if margin_match:
        margin_series = MetricSeries(name="gross_margin")
        years = [2022, 2023, 2024]  # Années correspondant aux colonnes
        for i, year in enumerate(years):
            try:
                value = float(margin_match.group(i + 1))
                margin_series.add_metric(year, value)
            except ValueError:
                pass
        financials.add_metric_series("gross_margin", margin_series)
    
    # Extraire le bénéfice net
    income_match = re.search(r'Net income\s+([0-9,]+)\s+([0-9,]+)\s+([0-9,]+)', text)
    if income_match:
        income_series = MetricSeries(name="net_income")
        years = [2022, 2023, 2024]  # Années correspondant aux colonnes
        for i, year in enumerate(years):
            value_str = income_match.group(i + 1).replace(',', '')
            try:
                value = float(value_str)
                income_series.add_metric(year, value)
            except ValueError:
                pass
        financials.add_metric_series("net_income", income_series)
    
    return financials

def load_company_data(company_code: str) -> Optional[CompanyFinancials]:
    """
    Charge les données financières d'une entreprise.
    
    Args:
        company_code: Le code de l'entreprise (ex: 'aapl' pour Apple)
        
    Returns:
        Un objet CompanyFinancials ou None si les données ne sont pas trouvées
    """
    # Mapper les codes d'entreprise aux noms et tickers
    company_map = {
        'aapl': ('Apple', 'AAPL'),
        'msft': ('Microsoft', 'MSFT'),
        'tsla': ('Tesla', 'TSLA'),
        'amzn': ('Amazon', 'AMZN'),
        'googl': ('Google', 'GOOGL')
    }
    
    if company_code not in company_map:
        return None
    
    company_name, ticker = company_map[company_code]
    
    # Essayer de charger depuis un fichier JSON existant
    json_path = os.path.join(DATA_DIR, f"{company_code}_financials.json")
    if os.path.exists(json_path):
        try:
            return CompanyFinancials.from_file(json_path)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier JSON: {e}")
    
    # Si le fichier JSON n'existe pas, essayer d'extraire les données depuis le texte
    txt_path = os.path.join(DATA_DIR, f"{company_code}_10k_extracted.txt")
    if os.path.exists(txt_path):
        try:
            with open(txt_path, 'r') as f:
                text = f.read()
            financials = extract_financial_data_from_text(text, company_name, ticker)
            
            # Sauvegarder les données extraites pour une utilisation future
            financials.save_to_file(json_path)
            
            return financials
        except Exception as e:
            print(f"Erreur lors de l'extraction des données: {e}")
    
    return None

def load_comparative_data() -> ComparativeAnalysis:
    """
    Charge ou génère des données comparatives pour plusieurs entreprises.
    
    Returns:
        Un objet ComparativeAnalysis contenant les données comparatives
    """
    # Essayer de charger depuis un fichier JSON existant
    json_path = os.path.join(DATA_DIR, "comparative_analysis.json")
    if os.path.exists(json_path):
        try:
            return ComparativeAnalysis.from_file(json_path)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier JSON: {e}")
    
    # Si le fichier JSON n'existe pas, générer les données à partir des données des entreprises
    companies = ['aapl', 'msft']
    metrics = ['revenue', 'gross_margin', 'net_income']
    years = [2022, 2023, 2024]
    
    analysis = ComparativeAnalysis(
        companies=['Apple', 'Microsoft'],
        metrics=metrics,
        years=years
    )
    
    for company_code in companies:
        financials = load_company_data(company_code)
        if financials:
            for metric_name in metrics:
                metric = financials.get_metric(metric_name)
                if metric:
                    for year in years:
                        if year in metric.metrics:
                            analysis.add_data_point(
                                financials.name,
                                metric_name,
                                year,
                                metric.metrics[year]
                            )
    
    # Sauvegarder les données pour une utilisation future
    analysis.save_to_file(json_path)
    
    return analysis

def load_prediction_data() -> Dict[str, Dict[str, PredictionSeries]]:
    """
    Charge ou génère des prédictions financières.
    
    Returns:
        Un dictionnaire de prédictions par entreprise et par métrique
    """
    # Essayer de charger depuis un fichier JSON existant
    json_path = os.path.join(DATA_DIR, "predictions.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            predictions = {}
            for company, metrics in data.items():
                predictions[company] = {}
                for metric_name, pred_data in metrics.items():
                    series = PredictionSeries(company=company, metric=metric_name)
                    for year_str, pred_info in pred_data["predictions"].items():
                        prediction = FinancialPrediction(
                            company=company,
                            metric=metric_name,
                            year=int(year_str),
                            value=pred_info["value"],
                            confidence=pred_info.get("confidence", 0.0),
                            growth_rate=pred_info.get("growth_rate", 0.0)
                        )
                        series.add_prediction(prediction)
                    predictions[company][metric_name] = series
            
            return predictions
        except Exception as e:
            print(f"Erreur lors du chargement du fichier JSON: {e}")
    
    # Si le fichier JSON n'existe pas, générer des prédictions simples
    predictions = {}
    companies = ['Apple', 'Microsoft']
    metrics = ['revenue', 'gross_margin', 'net_income']
    future_years = [2025, 2026]
    
    # Charger les données comparatives pour obtenir les valeurs historiques
    comparative = load_comparative_data()
    
    for company in companies:
        predictions[company] = {}
        for metric in metrics:
            series = PredictionSeries(company=company, metric=metric)
            
            # Obtenir les données historiques
            historical_data = comparative.get_metric_for_company(company, metric)
            if not historical_data:
                continue
            
            # Calculer la croissance moyenne
            years = sorted(historical_data.keys())
            if len(years) < 2:
                continue
            
            values = [historical_data[year] for year in years]
            growth_rates = []
            for i in range(1, len(values)):
                if values[i-1] > 0:
                    growth_rate = (values[i] - values[i-1]) / values[i-1] * 100
                    growth_rates.append(growth_rate)
            
            if not growth_rates:
                continue
            
            avg_growth_rate = sum(growth_rates) / len(growth_rates)
            last_value = values[-1]
            last_year = years[-1]
            
            # Générer les prédictions
            for future_year in future_years:
                years_ahead = future_year - last_year
                predicted_value = last_value * (1 + avg_growth_rate / 100) ** years_ahead
                confidence = max(0, 100 - (years_ahead * 10))  # Diminue avec le temps
                
                prediction = FinancialPrediction(
                    company=company,
                    metric=metric,
                    year=future_year,
                    value=predicted_value,
                    confidence=confidence,
                    growth_rate=avg_growth_rate
                )
                series.add_prediction(prediction)
            
            predictions[company][metric] = series
    
    # Sauvegarder les prédictions pour une utilisation future
    with open(json_path, 'w') as f:
        json.dump(
            {
                company: {
                    metric: series.to_dict()
                    for metric, series in metrics_data.items()
                }
                for company, metrics_data in predictions.items()
            },
            f,
            indent=2
        )
    
    return predictions

def get_company_data(company_code: str) -> Tuple[Optional[CompanyFinancials], Dict[str, PredictionSeries]]:
    """
    Obtient les données financières et les prédictions pour une entreprise.
    
    Args:
        company_code: Le code de l'entreprise (ex: 'aapl' pour Apple)
        
    Returns:
        Un tuple contenant les données financières et les prédictions
    """
    financials = load_company_data(company_code)
    
    company_name = None
    if financials:
        company_name = financials.name
    else:
        company_map = {
            'aapl': 'Apple',
            'msft': 'Microsoft',
            'tsla': 'Tesla',
            'amzn': 'Amazon',
            'googl': 'Google'
        }
        company_name = company_map.get(company_code)
    
    if not company_name:
        return None, {}
    
    predictions = load_prediction_data().get(company_name, {})
    
    return financials, predictions 