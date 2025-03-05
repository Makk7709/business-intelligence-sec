import os
import signal
import subprocess
import sys
import platform

def get_process_list():
    """Récupère la liste des processus en cours d'exécution."""
    if platform.system() == "Windows":
        # Pour Windows
        try:
            output = subprocess.check_output("tasklist", shell=True).decode('utf-8', errors='ignore')
            return output
        except subprocess.CalledProcessError:
            return ""
    else:
        # Pour macOS et Linux
        try:
            output = subprocess.check_output("ps aux", shell=True).decode('utf-8', errors='ignore')
            return output
        except subprocess.CalledProcessError:
            return ""

def kill_process_by_port(port):
    """Tue le processus qui utilise un port spécifique."""
    if platform.system() == "Windows":
        # Pour Windows
        try:
            # Trouver le PID du processus qui utilise le port
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode('utf-8', errors='ignore')
            if output:
                # Extraire le PID (dernier élément de chaque ligne)
                for line in output.strip().split('\n'):
                    if f":{port}" in line:
                        parts = line.strip().split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            # Tuer le processus
                            subprocess.call(f"taskkill /F /PID {pid}", shell=True)
                            print(f"Processus {pid} utilisant le port {port} a été arrêté.")
        except subprocess.CalledProcessError:
            pass
    else:
        # Pour macOS et Linux
        try:
            # Trouver le PID du processus qui utilise le port
            output = subprocess.check_output(f"lsof -i :{port}", shell=True).decode('utf-8', errors='ignore')
            if output:
                # Extraire le PID (deuxième colonne)
                lines = output.strip().split('\n')
                if len(lines) > 1:  # Ignorer l'en-tête
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) > 1:
                            pid = parts[1]
                            # Tuer le processus
                            os.kill(int(pid), signal.SIGTERM)
                            print(f"Processus {pid} utilisant le port {port} a été arrêté.")
        except subprocess.CalledProcessError:
            pass

def kill_python_servers():
    """Tue tous les serveurs Python (Flask, Streamlit) en cours d'exécution."""
    process_list = get_process_list()
    
    # Rechercher les processus Python
    python_processes = []
    for line in process_list.split('\n'):
        if "python" in line.lower() and ("flask" in line.lower() or "streamlit" in line.lower() or "app/" in line.lower()):
            python_processes.append(line)
    
    if not python_processes:
        print("Aucun serveur Python (Flask/Streamlit) trouvé en cours d'exécution.")
        return
    
    print(f"Serveurs Python trouvés: {len(python_processes)}")
    
    # Tuer les processus
    for process in python_processes:
        try:
            # Extraire le PID
            parts = process.split()
            if platform.system() == "Windows":
                # Format différent pour Windows
                for i, part in enumerate(parts):
                    if part.lower() == "python" or part.lower() == "python.exe":
                        pid = parts[1]  # Le PID est généralement dans la deuxième colonne
                        break
            else:
                # Pour macOS et Linux
                pid = parts[1]  # Le PID est généralement dans la deuxième colonne
            
            # Tuer le processus
            if platform.system() == "Windows":
                subprocess.call(f"taskkill /F /PID {pid}", shell=True)
            else:
                os.kill(int(pid), signal.SIGTERM)
            
            print(f"Processus Python {pid} arrêté.")
        except (IndexError, ValueError, ProcessLookupError):
            continue

def stop_servers_on_ports(ports):
    """Arrête les serveurs sur les ports spécifiés."""
    for port in ports:
        print(f"Tentative d'arrêt du serveur sur le port {port}...")
        kill_process_by_port(port)

if __name__ == "__main__":
    print("=== ARRÊT DES SERVEURS ===")
    
    # Ports courants utilisés par nos applications
    common_ports = [5000, 5001, 5002, 5003, 5010, 5050, 8501, 8502, 8080]
    
    # Arrêter les serveurs sur les ports spécifiés
    stop_servers_on_ports(common_ports)
    
    # Tuer tous les serveurs Python
    kill_python_servers()
    
    print("Opération terminée.")
    
    # Attendre que l'utilisateur appuie sur une touche pour quitter
    input("Appuyez sur Entrée pour quitter...") 