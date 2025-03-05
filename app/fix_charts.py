import os
import re

def fix_chart_js_data_binding(file_path):
    """
    Corrige la façon dont les données sont passées à Chart.js dans un fichier Flask.
    Remplace les expressions comme 'const years = {{ years|tojson }};'
    par 'const years = JSON.parse(\'{{ years|tojson }}\');'
    """
    if not os.path.exists(file_path):
        print(f"Le fichier {file_path} n'existe pas.")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Motif pour trouver les déclarations de variables JavaScript utilisant des données Jinja2
    pattern = r'const\s+(\w+)\s*=\s*\{\{\s*(\w+)\|tojson\s*\}\};'
    
    # Remplacer par JSON.parse
    replacement = r"const \1 = JSON.parse('{{ \2|tojson }}');"
    
    # Effectuer le remplacement
    modified_content = re.sub(pattern, replacement, content)
    
    # Vérifier si des modifications ont été apportées
    if modified_content != content:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        print(f"Le fichier {file_path} a été corrigé.")
        return True
    else:
        print(f"Aucune modification nécessaire pour {file_path}.")
        return False

def main():
    # Liste des fichiers à corriger
    files_to_fix = [
        'app/chart_app.py',
        'app/final_app.py',
        'app/improved_flask_app.py'
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        if fix_chart_js_data_binding(file_path):
            fixed_count += 1
    
    print(f"\nRésumé: {fixed_count} fichier(s) corrigé(s) sur {len(files_to_fix)}.")

if __name__ == "__main__":
    main() 