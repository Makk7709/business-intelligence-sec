import os
import sys
from parser import extract_text_from_pdf

def main():
    """Extrait le texte du rapport 10-K d'Apple."""
    print("🚀 Démarrage de l'extraction du texte du rapport 10-K d'Apple...")
    
    # Vérifier si le fichier PDF existe
    pdf_path = "data/aapl_10k.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ Le fichier {pdf_path} n'existe pas.")
        print("Veuillez télécharger le rapport 10-K d'Apple et le placer dans le répertoire data/")
        sys.exit(1)
    
    # Extraire le texte
    output_path = "data/aapl_10k_extracted.txt"
    extract_text_from_pdf(pdf_path, output_path)
    
    print(f"✅ Extraction terminée. Le texte a été sauvegardé dans {output_path}")

if __name__ == "__main__":
    main() 