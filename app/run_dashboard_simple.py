"""
Script pour lancer le dashboard financier.
Ce script peut utiliser soit la version dynamique (Flask) soit la version statique du dashboard.
"""

import os
import sys
import time
import signal
import socket
import shutil
import logging
import subprocess
import atexit

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Port pour l'application
PORT = 5115

# Chemins vers les fichiers
DASHBOARD_COMPLET = os.path.join('app', 'dashboard_complet.py')
DASHBOARD_FINAL = os.path.join('app', 'dashboard_final.py')
TEMP_FILE = os.path.join('app', 'dashboard_temp.py')
STATIC_HTML = os.path.join('app', 'dashboard_static.html')
STATIC_SERVER = os.path.join('app', 'serve_static_dashboard.py')

def is_port_in_use(port):
    """Vérifie si le port est déjà utilisé."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Tue le processus qui utilise le port spécifié."""
    try:
        # Utiliser une approche plus robuste pour tuer les processus
        subprocess.run(f"lsof -i :{port} -t | xargs kill -9", shell=True)
        time.sleep(1)  # Attendre que le port soit libéré
        return not is_port_in_use(port)
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt du processus sur le port {port}: {e}")
    
    return False

def create_temp_file():
    """Crée un fichier temporaire avec le code du dashboard."""
    # Déterminer quel fichier source utiliser
    source_file = DASHBOARD_FINAL if os.path.exists(DASHBOARD_FINAL) else DASHBOARD_COMPLET
    
    if not os.path.exists(source_file):
        logger.error(f"Fichier source {source_file} introuvable.")
        return False
    
    try:
        # Lire le contenu du fichier source
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Modifier le port dans le contenu
        content = content.replace("app.run(debug=True)", f"app.run(debug=True, port={PORT})")
        content = content.replace("app.run(host='0.0.0.0', port=5000)", f"app.run(host='0.0.0.0', port={PORT})")
        content = content.replace("app.run(host='127.0.0.1', port=5000)", f"app.run(host='127.0.0.1', port={PORT})")
        
        # Ajouter le code pour servir les fichiers statiques
        if "app = Flask(__name__)" in content and "static_folder" not in content:
            content = content.replace("app = Flask(__name__)", "app = Flask(__name__, static_folder='static')")
        
        # Ajouter un script de correction pour les graphiques
        if "</head>" in content:
            fix_script = """
    <script>
    // Script de correction pour les graphiques
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM chargé, initialisation des graphiques...');
        
        // Fonction pour vérifier si Chart.js est chargé
        function isChartJsLoaded() {
            return typeof Chart !== 'undefined';
        }
        
        // Fonction pour corriger les graphiques
        function fixCharts() {
            console.log("Exécution de fixCharts()...");
            
            if (!isChartJsLoaded()) {
                console.error("Chart.js n'est pas chargé");
                return;
            }
            
            console.log("Chart.js est chargé. Version : " + Chart.version);
            
            // Forcer l'appel des fonctions de chargement des données
            if (typeof loadComparativeData === 'function') {
                console.log("Appel de loadComparativeData()...");
                loadComparativeData();
            }
            
            if (typeof loadPredictionData === 'function') {
                console.log("Appel de loadPredictionData()...");
                loadPredictionData();
            }
            
            // Mettre à jour tous les graphiques existants
            if (typeof Chart !== 'undefined' && Chart.instances) {
                Object.keys(Chart.instances).forEach(key => {
                    console.log(`Mise à jour du graphique ${key}...`);
                    Chart.instances[key].update();
                });
            }
        }
        
        // Exécuter la correction après un délai
        setTimeout(fixCharts, 500);
    });
    </script>
    """
            content = content.replace("</head>", fix_script + "</head>")
        
        # Écrire le contenu modifié dans le fichier temporaire
        with open(TEMP_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Fichier temporaire {TEMP_FILE} créé avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création du fichier temporaire: {e}")
        return False

def cleanup_temp_file(temp_file):
    """Supprime le fichier temporaire."""
    try:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            logger.info(f"Fichier temporaire {temp_file} supprimé")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du fichier temporaire: {e}")

def launch_static_dashboard():
    """Lance la version statique du dashboard."""
    if not os.path.exists(STATIC_HTML):
        logger.error(f"Fichier HTML statique {STATIC_HTML} introuvable.")
        return False
    
    if not os.path.exists(STATIC_SERVER):
        logger.error(f"Serveur statique {STATIC_SERVER} introuvable.")
        return False
    
    try:
        logger.info(f"Lancement de la version statique du dashboard sur le port {PORT}...")
        logger.info(f"Accédez à l'application à l'adresse: http://127.0.0.1:{PORT}")
        
        # Exécuter le serveur statique
        subprocess.run([sys.executable, STATIC_SERVER], check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du lancement du serveur statique : {e}")
        return False
    except KeyboardInterrupt:
        logger.info("Application arrêtée par l'utilisateur.")
        return True

def launch_dynamic_dashboard():
    """Lance la version dynamique du dashboard."""
    # Créer le fichier temporaire
    if not create_temp_file():
        logger.error("Impossible de créer le fichier temporaire.")
        return False
    
    # Enregistrer la fonction de nettoyage
    atexit.register(cleanup_temp_file, TEMP_FILE)
    
    try:
        logger.info(f"Lancement de la version dynamique du dashboard sur le port {PORT}...")
        logger.info(f"Accédez à l'application à l'adresse: http://127.0.0.1:{PORT}")
        
        # Exécuter le fichier temporaire en mode non-debug pour éviter les problèmes de redémarrage
        cmd = [sys.executable, "-c", f"import sys; sys.path.append('.'); from app.dashboard_temp import app; app.run(host='127.0.0.1', port={PORT}, debug=False)"]
        subprocess.run(cmd, check=True)
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors du lancement de l'application : {e}")
        return False
    except KeyboardInterrupt:
        logger.info("Application arrêtée par l'utilisateur.")
        return True
    finally:
        # Nettoyer le fichier temporaire
        cleanup_temp_file(TEMP_FILE)

def main():
    """Fonction principale."""
    logger.info("=" * 80)
    logger.info(f"Démarrage du dashboard financier sur le port {PORT}")
    logger.info("=" * 80)
    
    # Vérifier si le port est déjà utilisé
    if is_port_in_use(PORT):
        logger.warning(f"Le port {PORT} est déjà utilisé. Tentative d'arrêt du processus...")
        if not kill_process_on_port(PORT):
            logger.error(f"Impossible de libérer le port {PORT}. Veuillez arrêter le processus manuellement.")
            return 1
    
    # Essayer d'abord la version statique
    if os.path.exists(STATIC_HTML):
        logger.info("Utilisation de la version statique du dashboard.")
        if launch_static_dashboard():
            return 0
        else:
            logger.warning("Échec du lancement de la version statique. Tentative avec la version dynamique...")
    
    # Si la version statique échoue ou n'existe pas, essayer la version dynamique
    logger.info("Utilisation de la version dynamique du dashboard.")
    if launch_dynamic_dashboard():
        return 0
    else:
        logger.error("Échec du lancement de la version dynamique.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 