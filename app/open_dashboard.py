import os
import webbrowser
import platform
import sys

def open_dashboard():
    """Ouvre le tableau de bord statique dans le navigateur par défaut"""
    # Obtenir le chemin absolu du fichier HTML
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, 'static_dashboard.html')
    
    # Vérifier que le fichier existe
    if not os.path.exists(html_path):
        print(f"ERREUR: Le fichier {html_path} n'existe pas!")
        return False
    
    # Convertir le chemin en URL selon le système d'exploitation
    if platform.system() == 'Windows':
        file_url = f'file:///{html_path.replace(os.sep, "/")}'
    else:  # macOS ou Linux
        file_url = f'file://{html_path}'
    
    print(f"\n\n=== OUVERTURE DU TABLEAU DE BORD ===")
    print(f"Ouverture du tableau de bord dans votre navigateur...")
    print(f"Si le navigateur ne s'ouvre pas automatiquement, veuillez ouvrir manuellement ce fichier:")
    print(f"{html_path}")
    print(f"=====================================\n\n")
    
    # Ouvrir le navigateur
    webbrowser.open(file_url)
    return True

if __name__ == "__main__":
    success = open_dashboard()
    sys.exit(0 if success else 1) 