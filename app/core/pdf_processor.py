"""
Module pour le traitement des fichiers PDF.
Ce module fournit des fonctionnalités pour extraire du texte et des données financières à partir de fichiers PDF.
"""

import os
import sys
import logging
import re
import json
import hashlib
import time
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime
import functools

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import DATA_DIR, LOGS_DIR

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'pdf_processor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from pdfminer.high_level import extract_text
    from pdfminer.pdfparser import PDFSyntaxError
    HAS_PDFMINER = True
except ImportError:
    logger.warning("pdfminer.six n'est pas installé. L'extraction de texte PDF sera limitée.")
    HAS_PDFMINER = False

try:
    from pdf2image import convert_from_path
    import pytesseract
    HAS_OCR = True
except ImportError:
    logger.warning("pdf2image ou pytesseract n'est pas installé. L'OCR ne sera pas disponible.")
    HAS_OCR = False


# Cache pour les résultats d'extraction de texte
@functools.lru_cache(maxsize=20)
def get_pdf_hash(pdf_path: str) -> str:
    """
    Calcule le hash MD5 d'un fichier PDF.
    Utilise un cache pour éviter de recalculer le hash à chaque appel.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        Hash MD5 du fichier PDF
    """
    if not os.path.exists(pdf_path):
        return ""
    
    hasher = hashlib.md5()
    with open(pdf_path, 'rb') as f:
        buf = f.read(65536)  # Lire par blocs de 64k
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    
    return hasher.hexdigest()


class PDFProcessor:
    """
    Classe pour traiter les fichiers PDF et extraire des informations financières.
    """
    
    def __init__(self):
        """
        Initialise le processeur PDF.
        """
        self.extracted_dir = os.path.join(DATA_DIR, 'extracted')
        os.makedirs(self.extracted_dir, exist_ok=True)
        
        # Modèles regex pour l'extraction de données financières
        self.regex_patterns = {
            'revenue': [
                r'(?:Total\s+)?(?:Net\s+)?(?:Revenue|Sales)(?:\s+was|\s+were|\s+of|\s+:|\s+\()?\s*(?:\$|USD)?\s*([\d,\.]+)\s*(?:million|billion|m|b|M|B)?',
                r'(?:Revenue|Sales)(?:\s+was|\s+were|\s+of|\s+:|\s+\()?\s*(?:\$|USD)?\s*([\d,\.]+)\s*(?:million|billion|m|b|M|B)?'
            ],
            'gross_margin': [
                r'Gross\s+margin(?:\s+was|\s+of|\s+:|\s+\()?\s*([\d,\.]+)\s*%',
                r'Gross\s+margin(?:\s+was|\s+of|\s+:|\s+\()?\s*([\d,\.]+)'
            ],
            'net_income': [
                r'(?:Net\s+income|Net\s+earnings|Net\s+profit)(?:\s+was|\s+were|\s+of|\s+:|\s+\()?\s*(?:\$|USD)?\s*([\d,\.]+)\s*(?:million|billion|m|b|M|B)?',
                r'(?:Net\s+income|Net\s+earnings|Net\s+profit)(?:\s+was|\s+were|\s+of|\s+:|\s+\()?\s*(?:\$|USD)?\s*([\d,\.]+)'
            ]
        }
        
        # Cache pour les résultats d'extraction
        self.cache = {}
        self.cache_ttl = 3600  # 1 heure
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrait le texte d'un fichier PDF.
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            Le texte extrait du PDF
        """
        logger.info(f"Extraction du texte du fichier PDF: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Le fichier PDF n'existe pas: {pdf_path}")
        
        # Vérifier si le texte est déjà en cache
        pdf_hash = get_pdf_hash(pdf_path)
        cache_key = f"text_{pdf_hash}"
        
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                logger.info(f"Utilisation du texte en cache pour {pdf_path}")
                return cache_entry['text']
        
        text = ""
        
        # Essayer d'extraire le texte avec pdfminer
        if HAS_PDFMINER:
            try:
                text = extract_text(pdf_path)
                logger.info(f"Texte extrait avec pdfminer: {len(text)} caractères")
            except PDFSyntaxError as e:
                logger.error(f"Erreur lors de l'extraction du texte avec pdfminer: {str(e)}")
            except Exception as e:
                logger.error(f"Erreur inattendue lors de l'extraction du texte avec pdfminer: {str(e)}")
        
        # Si le texte est vide ou trop court, essayer l'OCR
        if (not text or len(text) < 1000) and HAS_OCR:
            logger.info("Texte insuffisant extrait avec pdfminer, tentative avec OCR...")
            try:
                # Convertir les pages PDF en images
                images = convert_from_path(pdf_path)
                
                # Extraire le texte de chaque image
                ocr_text = []
                for i, image in enumerate(images):
                    logger.info(f"OCR sur la page {i+1}/{len(images)}...")
                    page_text = pytesseract.image_to_string(image, lang='fra+eng')
                    ocr_text.append(page_text)
                
                # Combiner le texte de toutes les pages
                text = "\n".join(ocr_text)
                logger.info(f"Texte extrait avec OCR: {len(text)} caractères")
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction du texte avec OCR: {str(e)}")
        
        if not text:
            logger.warning("Aucun texte n'a pu être extrait du PDF")
        
        # Mettre en cache le texte extrait
        self.cache[cache_key] = {
            'text': text,
            'timestamp': time.time()
        }
        
        return text
    
    def extract_financial_data(self, text: str) -> Dict[str, Any]:
        """
        Extrait les données financières du texte.
        
        Args:
            text: Texte extrait du PDF
            
        Returns:
            Dictionnaire contenant les données financières extraites
        """
        logger.info("Extraction des données financières du texte...")
        
        # Vérifier si les données sont déjà en cache
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"data_{text_hash}"
        
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                logger.info("Utilisation des données financières en cache")
                return cache_entry['data']
        
        financial_data = {
            'revenue': None,
            'gross_margin': None,
            'net_income': None
        }
        
        # Extraire les données pour chaque métrique
        for metric, patterns in self.regex_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # Prendre la première correspondance
                    value_str = matches[0]
                    
                    # Nettoyer la valeur
                    value_str = value_str.replace(',', '')
                    
                    try:
                        value = float(value_str)
                        financial_data[metric] = value
                        logger.info(f"Métrique extraite: {metric} = {value}")
                        break
                    except ValueError:
                        logger.warning(f"Impossible de convertir la valeur en nombre: {value_str}")
        
        # Mettre en cache les données extraites
        self.cache[cache_key] = {
            'data': financial_data,
            'timestamp': time.time()
        }
        
        return financial_data
    
    def save_extracted_text(self, text: str, original_filename: str) -> str:
        """
        Sauvegarde le texte extrait dans un fichier.
        
        Args:
            text: Texte extrait
            original_filename: Nom du fichier PDF original
            
        Returns:
            Chemin vers le fichier texte sauvegardé
        """
        # Créer un nom de fichier basé sur le nom du fichier original
        base_name = os.path.splitext(os.path.basename(original_filename))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        text_filename = f"{base_name}_{timestamp}_extracted.txt"
        text_filepath = os.path.join(self.extracted_dir, text_filename)
        
        # Sauvegarder le texte
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"Texte extrait sauvegardé dans: {text_filepath}")
        return text_filepath
    
    def save_financial_data(self, financial_data: Dict[str, Any], original_filename: str) -> str:
        """
        Sauvegarde les données financières dans un fichier JSON.
        
        Args:
            financial_data: Données financières extraites
            original_filename: Nom du fichier PDF original
            
        Returns:
            Chemin vers le fichier JSON sauvegardé
        """
        # Créer un nom de fichier basé sur le nom du fichier original
        base_name = os.path.splitext(os.path.basename(original_filename))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_filename = f"{base_name}_{timestamp}_financial_data.json"
        json_filepath = os.path.join(self.extracted_dir, json_filename)
        
        # Sauvegarder les données
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(financial_data, f, indent=4)
        
        logger.info(f"Données financières sauvegardées dans: {json_filepath}")
        return json_filepath
    
    def process_pdf(self, pdf_path: str) -> Tuple[str, str]:
        """
        Traite un fichier PDF pour extraire le texte et les données financières.
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            Tuple contenant les chemins vers les fichiers texte et JSON sauvegardés
        """
        logger.info(f"Traitement du fichier PDF: {pdf_path}")
        
        # Nettoyer le cache des entrées expirées
        self._clean_cache()
        
        # Vérifier si le PDF a déjà été traité
        pdf_hash = get_pdf_hash(pdf_path)
        cache_key = f"process_{pdf_hash}"
        
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                # Vérifier que les fichiers existent toujours
                if os.path.exists(cache_entry['text_filepath']) and os.path.exists(cache_entry['json_filepath']):
                    logger.info(f"Utilisation des résultats en cache pour {pdf_path}")
                    return cache_entry['text_filepath'], cache_entry['json_filepath']
        
        # Extraire le texte
        text = self.extract_text_from_pdf(pdf_path)
        
        # Extraire les données financières
        financial_data = self.extract_financial_data(text)
        
        # Sauvegarder le texte et les données
        text_filepath = self.save_extracted_text(text, pdf_path)
        json_filepath = self.save_financial_data(financial_data, pdf_path)
        
        # Mettre en cache les résultats
        self.cache[cache_key] = {
            'text_filepath': text_filepath,
            'json_filepath': json_filepath,
            'timestamp': time.time()
        }
        
        logger.info(f"Traitement du PDF terminé. Texte: {text_filepath}, Données: {json_filepath}")
        return text_filepath, json_filepath
    
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


# Créer une instance du processeur PDF
pdf_processor = PDFProcessor() 