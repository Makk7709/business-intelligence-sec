"""
Modèles de données pour les informations financières.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

@dataclass
class FinancialMetric:
    """Représente une métrique financière pour une année spécifique."""
    year: int
    value: float
    
    def __post_init__(self):
        """Convertit les types si nécessaire."""
        self.year = int(self.year)
        self.value = float(self.value)

@dataclass
class MetricSeries:
    """Représente une série de métriques financières sur plusieurs années."""
    name: str
    metrics: Dict[int, float] = field(default_factory=dict)
    
    def add_metric(self, year: int, value: float):
        """Ajoute une métrique pour une année spécifique."""
        self.metrics[int(year)] = float(value)
    
    def get_years(self) -> List[int]:
        """Retourne la liste des années disponibles, triées."""
        return sorted(self.metrics.keys())
    
    def get_values(self) -> List[float]:
        """Retourne la liste des valeurs, triées par année."""
        return [self.metrics[year] for year in self.get_years()]
    
    def get_latest_value(self) -> Optional[float]:
        """Retourne la valeur la plus récente."""
        years = self.get_years()
        if not years:
            return None
        return self.metrics[years[-1]]

@dataclass
class CompanyFinancials:
    """Représente l'ensemble des données financières d'une entreprise."""
    name: str
    ticker: str
    metrics: Dict[str, MetricSeries] = field(default_factory=dict)
    
    def add_metric_series(self, name: str, series: MetricSeries):
        """Ajoute une série de métriques."""
        self.metrics[name] = series
    
    def get_metric(self, name: str) -> Optional[MetricSeries]:
        """Récupère une série de métriques par son nom."""
        return self.metrics.get(name)
    
    def to_dict(self) -> Dict:
        """Convertit les données en dictionnaire."""
        return {
            "name": self.name,
            "ticker": self.ticker,
            "metrics": {
                name: {str(year): value for year, value in series.metrics.items()}
                for name, series in self.metrics.items()
            }
        }
    
    def to_json(self) -> str:
        """Convertit les données en JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, file_path: str):
        """Sauvegarde les données dans un fichier JSON."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CompanyFinancials':
        """Crée une instance à partir d'un dictionnaire."""
        company = cls(name=data["name"], ticker=data["ticker"])
        for metric_name, years_data in data["metrics"].items():
            series = MetricSeries(name=metric_name)
            for year, value in years_data.items():
                series.add_metric(int(year), float(value))
            company.add_metric_series(metric_name, series)
        return company
    
    @classmethod
    def from_json(cls, json_str: str) -> 'CompanyFinancials':
        """Crée une instance à partir d'une chaîne JSON."""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_file(cls, file_path: str) -> 'CompanyFinancials':
        """Charge les données depuis un fichier JSON."""
        with open(file_path, 'r') as f:
            return cls.from_json(f.read())

@dataclass
class FinancialPrediction:
    """Représente une prédiction financière."""
    company: str
    metric: str
    year: int
    value: float
    confidence: float = 0.0
    growth_rate: float = 0.0
    
    def __post_init__(self):
        """Convertit les types si nécessaire."""
        self.year = int(self.year)
        self.value = float(self.value)
        self.confidence = float(self.confidence)
        self.growth_rate = float(self.growth_rate)

@dataclass
class PredictionSeries:
    """Représente une série de prédictions pour une métrique."""
    company: str
    metric: str
    predictions: Dict[int, FinancialPrediction] = field(default_factory=dict)
    
    def add_prediction(self, prediction: FinancialPrediction):
        """Ajoute une prédiction."""
        self.predictions[prediction.year] = prediction
    
    def get_years(self) -> List[int]:
        """Retourne la liste des années prédites, triées."""
        return sorted(self.predictions.keys())
    
    def get_values(self) -> List[float]:
        """Retourne la liste des valeurs prédites, triées par année."""
        return [self.predictions[year].value for year in self.get_years()]
    
    def to_dict(self) -> Dict:
        """Convertit les prédictions en dictionnaire."""
        return {
            "company": self.company,
            "metric": self.metric,
            "predictions": {
                str(year): {
                    "value": pred.value,
                    "confidence": pred.confidence,
                    "growth_rate": pred.growth_rate
                }
                for year, pred in self.predictions.items()
            }
        }

@dataclass
class ComparativeAnalysis:
    """Représente une analyse comparative entre plusieurs entreprises."""
    companies: List[str]
    metrics: List[str]
    years: List[int]
    data: Dict[str, Dict[str, Dict[int, float]]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_data_point(self, company: str, metric: str, year: int, value: float):
        """Ajoute un point de données."""
        if company not in self.data:
            self.data[company] = {}
        if metric not in self.data[company]:
            self.data[company][metric] = {}
        self.data[company][metric][int(year)] = float(value)
    
    def get_metric_for_company(self, company: str, metric: str) -> Dict[int, float]:
        """Récupère les données d'une métrique pour une entreprise."""
        return self.data.get(company, {}).get(metric, {})
    
    def to_dict(self) -> Dict:
        """Convertit l'analyse en dictionnaire."""
        return {
            "companies": self.companies,
            "metrics": self.metrics,
            "years": self.years,
            "data": {
                company: {
                    metric: {
                        str(year): value
                        for year, value in years_data.items()
                    }
                    for metric, years_data in metrics_data.items()
                }
                for company, metrics_data in self.data.items()
            },
            "created_at": self.created_at.isoformat()
        }
    
    def to_json(self) -> str:
        """Convertit l'analyse en JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, file_path: str):
        """Sauvegarde l'analyse dans un fichier JSON."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ComparativeAnalysis':
        """Crée une instance à partir d'un dictionnaire."""
        analysis = cls(
            companies=data["companies"],
            metrics=data["metrics"],
            years=data["years"]
        )
        for company, metrics_data in data["data"].items():
            for metric, years_data in metrics_data.items():
                for year, value in years_data.items():
                    analysis.add_data_point(company, metric, int(year), float(value))
        if "created_at" in data:
            analysis.created_at = datetime.fromisoformat(data["created_at"])
        return analysis
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ComparativeAnalysis':
        """Crée une instance à partir d'une chaîne JSON."""
        return cls.from_dict(json.loads(json_str))
    
    @classmethod
    def from_file(cls, file_path: str) -> 'ComparativeAnalysis':
        """Charge l'analyse depuis un fichier JSON."""
        with open(file_path, 'r') as f:
            return cls.from_json(f.read()) 