"""
Module pour l'exportation de données dans différents formats.
Ce module fournit des fonctionnalités pour exporter des données au format CSV, Excel, PDF et JSON.
"""

import os
import sys
import logging
import csv
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import functools

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import EXPORTS_DIR, LOGS_DIR, PDF_TEMPLATE_PATH

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'export_manager.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importer les bibliothèques optionnelles
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    logger.warning("pandas n'est pas installé. L'exportation Excel sera limitée.")
    HAS_PANDAS = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_REPORTLAB = True
except ImportError:
    logger.warning("reportlab n'est pas installé. L'exportation PDF sera limitée.")
    HAS_REPORTLAB = False


# Cache pour les styles et autres objets coûteux
@functools.lru_cache(maxsize=10)
def get_pdf_styles():
    """
    Récupère les styles pour les documents PDF.
    Utilise un cache pour éviter de recréer les styles à chaque appel.
    
    Returns:
        Dictionnaire de styles pour les documents PDF
    """
    if not HAS_REPORTLAB:
        return {}
    
    styles = getSampleStyleSheet()
    return {
        'title': styles['Title'],
        'heading': styles['Heading1'],
        'normal': styles['Normal'],
        'table_title': styles['Heading2']
    }


class ExportManager:
    """
    Classe pour gérer l'exportation de données dans différents formats.
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire d'exportation.
        """
        self.exports_dir = EXPORTS_DIR
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Cache pour les données exportées récemment
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def export_to_csv(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Exporte des données au format CSV.
        
        Args:
            data: Données à exporter
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin vers le fichier CSV exporté
        """
        logger.info("Exportation des données au format CSV...")
        
        # Créer un nom de fichier par défaut si non spécifié
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}"
        
        # Ajouter l'extension .csv si nécessaire
        if not filename.endswith('.csv'):
            filename = f"{filename}.csv"
        
        # Chemin complet vers le fichier
        filepath = os.path.join(self.exports_dir, filename)
        
        try:
            # Vérifier si les données sont au format attendu
            if not isinstance(data, dict):
                raise ValueError("Les données doivent être un dictionnaire")
            
            # Extraire les métriques
            metrics = data.get('metrics', {})
            if not metrics:
                raise ValueError("Aucune métrique trouvée dans les données")
            
            # Préparer les données pour l'exportation CSV
            csv_data = []
            
            # Trouver toutes les années uniques
            all_years = set()
            for metric_name, metric_data in metrics.items():
                years = metric_data.get('years', [])
                all_years.update(years)
            
            # Trier les années
            all_years = sorted(all_years)
            
            # Créer l'en-tête
            header = ['Year']
            for metric_name in metrics.keys():
                header.append(metric_name)
            
            csv_data.append(header)
            
            # Créer les lignes de données
            for year in all_years:
                row = [year]
                for metric_name, metric_data in metrics.items():
                    years = metric_data.get('years', [])
                    values = metric_data.get('values', [])
                    
                    # Trouver l'index de l'année
                    try:
                        index = years.index(year)
                        value = values[index]
                    except (ValueError, IndexError):
                        value = ''
                    
                    row.append(value)
                
                csv_data.append(row)
            
            # Écrire les données dans le fichier CSV
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
            
            logger.info(f"Données exportées avec succès au format CSV: {filepath}")
            
            # Mettre en cache les données exportées
            cache_key = f"csv_{filename}"
            self.cache[cache_key] = {
                'data': data,
                'filepath': filepath,
                'timestamp': time.time()
            }
            
            return filepath
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des données au format CSV: {str(e)}")
            raise
    
    def export_to_excel(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Exporte des données au format Excel.
        
        Args:
            data: Données à exporter
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin vers le fichier Excel exporté
        """
        logger.info("Exportation des données au format Excel...")
        
        if not HAS_PANDAS:
            raise ImportError("pandas est requis pour l'exportation Excel")
        
        # Créer un nom de fichier par défaut si non spécifié
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}"
        
        # Ajouter l'extension .xlsx si nécessaire
        if not filename.endswith('.xlsx'):
            filename = f"{filename}.xlsx"
        
        # Chemin complet vers le fichier
        filepath = os.path.join(self.exports_dir, filename)
        
        # Vérifier si les données sont déjà en cache
        cache_key = f"excel_{filename}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                if os.path.exists(cache_entry['filepath']):
                    logger.info(f"Utilisation des données en cache pour l'exportation Excel: {cache_entry['filepath']}")
                    return cache_entry['filepath']
        
        try:
            # Vérifier si les données sont au format attendu
            if not isinstance(data, dict):
                raise ValueError("Les données doivent être un dictionnaire")
            
            # Extraire les métriques
            metrics = data.get('metrics', {})
            if not metrics:
                raise ValueError("Aucune métrique trouvée dans les données")
            
            # Créer un DataFrame pandas
            df_data = {}
            
            # Trouver toutes les années uniques
            all_years = set()
            for metric_name, metric_data in metrics.items():
                years = metric_data.get('years', [])
                all_years.update(years)
            
            # Trier les années
            all_years = sorted(all_years)
            
            # Ajouter les années comme première colonne
            df_data['Year'] = all_years
            
            # Ajouter les données pour chaque métrique
            for metric_name, metric_data in metrics.items():
                years = metric_data.get('years', [])
                values = metric_data.get('values', [])
                
                # Créer un dictionnaire année -> valeur
                year_to_value = dict(zip(years, values))
                
                # Ajouter les valeurs pour chaque année
                df_data[metric_name] = [year_to_value.get(year, '') for year in all_years]
            
            # Créer le DataFrame
            df = pd.DataFrame(df_data)
            
            # Exporter le DataFrame au format Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Ajuster la largeur des colonnes
                worksheet = writer.sheets['Data']
                for i, col in enumerate(df.columns):
                    max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.column_dimensions[chr(65 + i)].width = max_length
            
            logger.info(f"Données exportées avec succès au format Excel: {filepath}")
            
            # Mettre en cache les données exportées
            self.cache[cache_key] = {
                'data': data,
                'filepath': filepath,
                'timestamp': time.time()
            }
            
            return filepath
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des données au format Excel: {str(e)}")
            raise
    
    def export_to_pdf(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Exporte des données au format PDF.
        
        Args:
            data: Données à exporter
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin vers le fichier PDF exporté
        """
        logger.info("Exportation des données au format PDF...")
        
        if not HAS_REPORTLAB:
            raise ImportError("reportlab est requis pour l'exportation PDF")
        
        # Créer un nom de fichier par défaut si non spécifié
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}"
        
        # Ajouter l'extension .pdf si nécessaire
        if not filename.endswith('.pdf'):
            filename = f"{filename}.pdf"
        
        # Chemin complet vers le fichier
        filepath = os.path.join(self.exports_dir, filename)
        
        # Vérifier si les données sont déjà en cache
        cache_key = f"pdf_{filename}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                if os.path.exists(cache_entry['filepath']):
                    logger.info(f"Utilisation des données en cache pour l'exportation PDF: {cache_entry['filepath']}")
                    return cache_entry['filepath']
        
        try:
            # Vérifier si les données sont au format attendu
            if not isinstance(data, dict):
                raise ValueError("Les données doivent être un dictionnaire")
            
            # Extraire les métriques
            metrics = data.get('metrics', {})
            if not metrics:
                raise ValueError("Aucune métrique trouvée dans les données")
            
            # Récupérer les styles
            styles = get_pdf_styles()
            
            # Créer le document PDF
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            
            # Ajouter le titre
            title = data.get('name', 'Rapport financier')
            elements.append(Paragraph(title, styles['title']))
            elements.append(Spacer(1, 12))
            
            # Ajouter les informations supplémentaires
            if 'ticker' in data:
                elements.append(Paragraph(f"Ticker: {data['ticker']}", styles['normal']))
                elements.append(Spacer(1, 12))
            
            # Trouver toutes les années uniques
            all_years = set()
            for metric_name, metric_data in metrics.items():
                years = metric_data.get('years', [])
                all_years.update(years)
            
            # Trier les années
            all_years = sorted(all_years)
            
            # Créer les tableaux pour chaque métrique
            for metric_name, metric_data in metrics.items():
                # Ajouter le titre de la métrique
                elements.append(Paragraph(f"{metric_name}", styles['table_title']))
                elements.append(Spacer(1, 6))
                
                years = metric_data.get('years', [])
                values = metric_data.get('values', [])
                
                # Créer un dictionnaire année -> valeur
                year_to_value = dict(zip(years, values))
                
                # Créer les données du tableau
                table_data = [['Année', 'Valeur']]
                for year in all_years:
                    table_data.append([year, year_to_value.get(year, '')])
                
                # Créer le tableau
                table = Table(table_data, colWidths=[100, 100])
                
                # Styliser le tableau
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 12))
            
            # Générer le PDF
            doc.build(elements)
            
            logger.info(f"Données exportées avec succès au format PDF: {filepath}")
            
            # Mettre en cache les données exportées
            self.cache[cache_key] = {
                'data': data,
                'filepath': filepath,
                'timestamp': time.time()
            }
            
            return filepath
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exportation des données au format PDF: {str(e)}")
            raise
    
    def export_data(self, data: Dict[str, Any], format: str = 'csv', filename: str = None) -> str:
        """
        Exporte des données dans le format spécifié.
        
        Args:
            data: Données à exporter
            format: Format d'exportation (csv, excel, pdf, json)
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin vers le fichier exporté
        """
        logger.info(f"Exportation des données au format {format}...")
        
        # Nettoyer le cache des entrées expirées
        self._clean_cache()
        
        # Vérifier si le format est pris en charge
        format = format.lower()
        if format not in ['csv', 'excel', 'pdf', 'json']:
            raise ValueError(f"Format d'exportation non pris en charge: {format}")
        
        # Exporter les données dans le format spécifié
        if format == 'csv':
            return self.export_to_csv(data, filename)
        elif format == 'excel':
            return self.export_to_excel(data, filename)
        elif format == 'pdf':
            return self.export_to_pdf(data, filename)
        elif format == 'json':
            # Créer un nom de fichier par défaut si non spécifié
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"export_{timestamp}"
            
            # Ajouter l'extension .json si nécessaire
            if not filename.endswith('.json'):
                filename = f"{filename}.json"
            
            # Chemin complet vers le fichier
            filepath = os.path.join(self.exports_dir, filename)
            
            # Écrire les données dans le fichier JSON
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            
            logger.info(f"Données exportées avec succès au format JSON: {filepath}")
            return filepath
    
    def _clean_cache(self):
        """
        Nettoie le cache des entrées expirées.
        """
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry['timestamp'] > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.debug(f"Cache nettoyé: {len(expired_keys)} entrées supprimées")


# Créer une instance du gestionnaire d'exportation
export_manager = ExportManager() 