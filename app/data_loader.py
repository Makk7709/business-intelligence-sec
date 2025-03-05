import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_financial_data(company_code):
    """
    Charge les données financières d'une entreprise spécifique
    
    Args:
        company_code (str): Code de l'entreprise (tsla, aapl, msft)
        
    Returns:
        tuple: (metrics, ratios) contenant les métriques et ratios financiers
    """
    try:
        base_path = f"data/results/comparative/{company_code}"
        
        # Correction des noms de fichiers
        if company_code == "tsla":
            metrics_path = os.path.join(base_path, "tesla_financial_data.json")
        elif company_code == "aapl":
            metrics_path = os.path.join(base_path, "apple_financial_data.json")
        elif company_code == "msft":
            metrics_path = os.path.join(base_path, "microsoft_financial_data.json")
        else:
            metrics_path = os.path.join(base_path, f"{company_code}_financial_data.json")
        
        metrics = {}
        ratios = {}
        
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                data = json.load(f)
                # Extraire les métriques et les ratios du fichier
                if "metrics" in data:
                    metrics = data["metrics"]
                else:
                    metrics = data
                
                # Extraire les ratios s'ils existent
                if "ratios" in data:
                    ratios = data["ratios"]
        else:
            print(f"Fichier non trouvé: {metrics_path}")
                
        return metrics, ratios
    except Exception as e:
        print(f"Erreur lors du chargement des données pour {company_code}: {e}")
        return {}, {}

def load_comparative_data():
    """
    Charge les données comparatives pour toutes les entreprises
    
    Returns:
        dict: Données comparatives
    """
    try:
        comparative_path = "data/results/comparative/comparative/comparative_analysis.json"
        
        if os.path.exists(comparative_path):
            with open(comparative_path, 'r') as f:
                comparative_data = json.load(f)
            return comparative_data
        else:
            print(f"Fichier non trouvé: {comparative_path}")
            return {}
    except Exception as e:
        print(f"Erreur lors du chargement des données comparatives: {e}")
        return {}

def load_prediction_data():
    """
    Charge les données de prédiction
    
    Returns:
        dict: Données de prédiction
    """
    try:
        prediction_path = "data/results/predictions/financial_predictions.json"
        
        if os.path.exists(prediction_path):
            with open(prediction_path, 'r') as f:
                prediction_data = json.load(f)
            return prediction_data
        else:
            print(f"Fichier non trouvé: {prediction_path}")
            return {}
    except Exception as e:
        print(f"Erreur lors du chargement des prédictions: {e}")
        return {}

def metrics_to_dataframe(metrics):
    """
    Convertit les métriques financières en DataFrame pandas
    
    Args:
        metrics (dict): Métriques financières
        
    Returns:
        pandas.DataFrame: DataFrame contenant les métriques
    """
    try:
        data = {}
        years = []
        
        for metric, values in metrics.items():
            if isinstance(values, dict):
                for year, value in values.items():
                    if year not in years:
                        years.append(year)
                    if year not in data:
                        data[year] = {}
                    data[year][metric] = value
        
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_numeric(df.index)
        df = df.sort_index()
        
        return df
    except Exception as e:
        print(f"Erreur lors de la conversion en DataFrame: {e}")
        return pd.DataFrame() 