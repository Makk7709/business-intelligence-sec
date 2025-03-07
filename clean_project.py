#!/usr/bin/env python3
"""
Script pour nettoyer le projet en ne gardant que les fichiers essentiels.
"""

import os
import shutil
import sys
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Fichiers et répertoires à conserver
ESSENTIAL_DIRS = [
    'app/core',
    'app/models',
    'app/routes',
    'app/ui',
    'app/static',
    'app/comm',
    'app/templates',
    'data',
    'logs',
    'tests'
]

ESSENTIAL_FILES = [
    'app/app.py',
    'app/config.py',
    'app/ui/dashboard_static.html',
    'app/static/js/chart_fix.js',
    'app/static/css/styles.css',
    'app/comm/.gitkeep',
    'run.py',
    'run.sh',
    'requirements.txt',
    '.env',
    '.gitignore',
    'README.md',
    'README_RESTRUCTURED.md',
    'LICENSE'
]

# Fichiers à déplacer vers le nouveau répertoire
FILES_TO_MOVE = {
    'app/dashboard_static.html': 'app/ui/dashboard_static.html',
    'app/fix_charts.js': 'app/static/js/chart_fix.js'
}

def create_backup():
    """Crée une sauvegarde du projet."""
    backup_dir = 'backup_' + os.path.basename(os.getcwd())
    parent_dir = os.path.dirname(os.getcwd())
    backup_path = os.path.join(parent_dir, backup_dir)
    
    logger.info(f"Création d'une sauvegarde du projet dans {backup_path}")
    
    # Supprimer la sauvegarde si elle existe déjà
    if os.path.exists(backup_path):
        shutil.rmtree(backup_path)
    
    # Copier le projet dans la sauvegarde
    shutil.copytree(os.getcwd(), backup_path, symlinks=True)
    
    logger.info(f"Sauvegarde créée avec succès dans {backup_path}")
    
    return backup_path

def create_essential_dirs():
    """Crée les répertoires essentiels s'ils n'existent pas."""
    for dir_path in ESSENTIAL_DIRS:
        if not os.path.exists(dir_path):
            logger.info(f"Création du répertoire {dir_path}")
            os.makedirs(dir_path, exist_ok=True)

def move_files():
    """Déplace les fichiers vers leur nouvel emplacement."""
    for src, dst in FILES_TO_MOVE.items():
        if os.path.exists(src) and not os.path.exists(dst):
            logger.info(f"Déplacement de {src} vers {dst}")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

def clean_project():
    """Nettoie le projet en ne gardant que les fichiers essentiels."""
    # Créer les répertoires essentiels
    create_essential_dirs()
    
    # Déplacer les fichiers
    move_files()
    
    # Parcourir tous les fichiers et répertoires du projet
    for root, dirs, files in os.walk('.', topdown=False):
        # Ignorer les répertoires cachés et les répertoires de l'environnement virtuel
        if '/.git' in root or '/.venv' in root or '/venv' in root or '/__pycache__' in root:
            continue
        
        # Supprimer les fichiers non essentiels
        for file in files:
            file_path = os.path.join(root, file)
            file_path = os.path.normpath(file_path)
            
            # Convertir le chemin pour qu'il commence par le nom du répertoire
            if file_path.startswith('./'):
                file_path = file_path[2:]
            
            # Vérifier si le fichier est essentiel
            is_essential = False
            for essential_file in ESSENTIAL_FILES:
                if file_path == essential_file or file_path.startswith(essential_file):
                    is_essential = True
                    break
            
            # Vérifier si le fichier est dans un répertoire essentiel
            in_essential_dir = False
            for essential_dir in ESSENTIAL_DIRS:
                if file_path.startswith(essential_dir):
                    in_essential_dir = True
                    break
            
            # Supprimer le fichier s'il n'est pas essentiel et n'est pas dans un répertoire essentiel
            if not is_essential and not in_essential_dir:
                logger.info(f"Suppression du fichier {file_path}")
                os.remove(file_path)
        
        # Supprimer les répertoires vides
        if not os.listdir(root) and root != '.':
            logger.info(f"Suppression du répertoire vide {root}")
            os.rmdir(root)

def main():
    """Fonction principale."""
    # Vérifier si l'utilisateur a confirmé le nettoyage
    if len(sys.argv) < 2 or sys.argv[1] != '--confirm':
        logger.warning("Ce script va supprimer tous les fichiers non essentiels du projet.")
        logger.warning("Exécutez le script avec l'option --confirm pour confirmer le nettoyage.")
        logger.warning("Exemple : python clean_project.py --confirm")
        return 1
    
    # Créer une sauvegarde du projet
    backup_path = create_backup()
    
    # Nettoyer le projet
    logger.info("Nettoyage du projet...")
    clean_project()
    
    logger.info("Nettoyage terminé avec succès.")
    logger.info(f"Une sauvegarde du projet a été créée dans {backup_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 