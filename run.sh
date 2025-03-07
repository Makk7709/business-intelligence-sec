#!/bin/bash
# Script pour lancer l'application Business Intelligence SEC

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si les dépendances système sont installées (pour Tesseract OCR)
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    if ! command -v tesseract &> /dev/null; then
        echo "Installation de Tesseract OCR..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-fra
    fi
elif command -v brew &> /dev/null; then
    # macOS avec Homebrew
    if ! command -v tesseract &> /dev/null; then
        echo "Installation de Tesseract OCR..."
        brew install tesseract tesseract-lang
    fi
elif command -v pacman &> /dev/null; then
    # Arch Linux
    if ! command -v tesseract &> /dev/null; then
        echo "Installation de Tesseract OCR..."
        sudo pacman -S tesseract tesseract-data-fra
    fi
elif command -v dnf &> /dev/null; then
    # Fedora
    if ! command -v tesseract &> /dev/null; then
        echo "Installation de Tesseract OCR..."
        sudo dnf install -y tesseract tesseract-langpack-fra
    fi
fi

# Exécuter les tests avant de lancer l'application
if [ "$1" == "--test" ]; then
    echo "Exécution des tests..."
    python3 run.py --test
    exit $?
fi

# Lancer l'application avec les arguments passés
echo "Lancement de l'application..."
python3 run.py "$@" 