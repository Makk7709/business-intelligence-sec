import fitz  # PyMuPDF
import os  # Ajout pour la vérification du fichier après écriture

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un fichier PDF."""
    print(f"🔍 Tentative d'ouverture du fichier PDF : {pdf_path}")
    print(f"Le fichier existe ? {os.path.exists(pdf_path)}")
    
    with fitz.open(pdf_path) as doc:
        print(f"📄 Nombre de pages dans le PDF : {len(doc)}")
        text = "\n".join([page.get_text() for page in doc])
    return text

if __name__ == "__main__":
    pdf_path = "data/tsla-20241231.pdf"
    output_path = "data/tsla_10k_extracted.txt"

    print(f"📂 Dossier de travail actuel : {os.getcwd()}")
    print(f"📂 Le dossier data existe ? {os.path.exists('data')}")

    # Extraction du texte
    text = extract_text_from_pdf(pdf_path)
    print(f"📌 Longueur du texte extrait : {len(text)} caractères")
    print(text[:1000])  # Affiche un extrait du texte

    # Écriture du texte dans un fichier TXT avec vérification
    try:
        print(f"✍️ Tentative d'écriture dans : {output_path}")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"✅ Texte enregistré avec succès dans {output_path}")

        # Vérification immédiate après l'écriture
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Le fichier a bien été créé : {output_path}")
            print(f"📊 Taille du fichier : {file_size} octets")
        else:
            print(f"❌ Problème : Le fichier {output_path} n'existe pas après écriture")
    
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture du fichier : {e}")
        print(f"📂 Vérification : est-ce que le chemin de sortie existe ? {os.path.dirname(output_path)}")
        print(f"📂 Est-ce que le dossier est accessible en écriture ? {os.access(os.path.dirname(output_path), os.W_OK)}")

    print(f"📝 Taille du texte extrait : {len(text)} caractères")
