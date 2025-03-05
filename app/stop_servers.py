#!/usr/bin/env python3
"""
Script pour arrêter les processus Flask et Streamlit en cours d'exécution.
"""

import os
import signal
import subprocess
import sys
import platform

def get_process_ids(process_name):
    """
    Récupère les IDs des processus correspondant au nom spécifié.
    
    Args:
        process_name (str): Nom du processus à rechercher
        
    Returns:
        list: Liste des IDs de processus
    """
    pids = []
    
    if platform.system() == "Windows":
        # Commande pour Windows
        try:
            output = subprocess.check_output(["tasklist", "/FI", f"IMAGENAME eq {process_name}*", "/NH"], 
                                            universal_newlines=True)
            for line in output.strip().split('\n'):
                if process_name in line:
                    pid = int(line.split()[1])
                    pids.append(pid)
        except subprocess.CalledProcessError:
            print(f"Erreur lors de la recherche des processus {process_name}")
    else:
        # Commande pour Unix/Linux/MacOS
        try:
            # Recherche des processus Python exécutant Flask ou Streamlit
            output = subprocess.check_output(["ps", "aux"], universal_newlines=True)
            for line in output.strip().split('\n'):
                if process_name in line and "python" in line:
                    parts = line.split()
                    pid = int(parts[1])
                    pids.append(pid)
        except subprocess.CalledProcessError:
            print(f"Erreur lors de la recherche des processus {process_name}")
    
    return pids

def kill_processes(pids):
    """
    Tue les processus correspondant aux IDs spécifiés.
    
    Args:
        pids (list): Liste des IDs de processus à tuer
    """
    for pid in pids:
        try:
            if platform.system() == "Windows":
                subprocess.call(["taskkill", "/F", "/PID", str(pid)])
            else:
                os.kill(pid, signal.SIGTERM)
            print(f"Processus {pid} arrêté avec succès")
        except (OSError, subprocess.CalledProcessError) as e:
            print(f"Erreur lors de l'arrêt du processus {pid}: {e}")

def main():
    """
    Fonction principale qui arrête les processus Flask et Streamlit.
    """
    print("Recherche des processus Flask et Streamlit en cours d'exécution...")
    
    # Rechercher les processus Flask
    flask_pids = get_process_ids("flask")
    if flask_pids:
        print(f"Processus Flask trouvés: {flask_pids}")
        kill_processes(flask_pids)
    else:
        print("Aucun processus Flask trouvé")
    
    # Rechercher les processus Streamlit
    streamlit_pids = get_process_ids("streamlit")
    if streamlit_pids:
        print(f"Processus Streamlit trouvés: {streamlit_pids}")
        kill_processes(streamlit_pids)
    else:
        print("Aucun processus Streamlit trouvé")
    
    # Rechercher les processus Python qui exécutent app/finance_dashboard.py ou app/flask_app.py
    python_pids = []
    try:
        output = subprocess.check_output(["ps", "aux"], universal_newlines=True)
        for line in output.strip().split('\n'):
            if ("app/finance_dashboard.py" in line or "app/flask_app.py" in line) and "python" in line:
                parts = line.split()
                pid = int(parts[1])
                python_pids.append(pid)
    except subprocess.CalledProcessError:
        print("Erreur lors de la recherche des processus Python")
    
    if python_pids:
        print(f"Processus Python exécutant les applications Flask trouvés: {python_pids}")
        kill_processes(python_pids)
    else:
        print("Aucun processus Python exécutant les applications Flask trouvé")
    
    print("Opération terminée")

if __name__ == "__main__":
    main() 