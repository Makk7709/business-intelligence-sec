# Dashboard d'Intelligence Financière avec IA

Ce projet est un dashboard d'intelligence financière qui intègre des technologies d'IA avancées (LangChain, ChatGPT et Pinecone) pour analyser des données financières d'entreprises comme Apple et Microsoft.

## Fonctionnalités

- **Dashboard interactif** : Visualisation des données financières d'Apple et Microsoft
- **Assistant IA intégré** : Posez des questions en langage naturel sur les données financières
- **Traitement de documents** : Extraction de données financières à partir de fichiers PDF
- **Exportation de données** : Exportation des données financières aux formats CSV, Excel, PDF et JSON
- **Intégration multi-technologies** :
  - **OpenAI (ChatGPT)** : Pour le traitement du langage naturel
  - **LangChain** : Pour la création de chaînes de traitement IA complexes
  - **Pinecone** : Pour la recherche vectorielle et la récupération de contexte
  - **EDGAR** : Pour l'accès aux documents financiers officiels
  - **Alpha Vantage** : Pour les données financières en temps réel

## Architecture

L'application utilise une architecture en deux parties :
1. **Application Flask** : Sert le dashboard et gère les requêtes API
2. **Pont IA** : Processus séparé qui communique avec les technologies d'IA (OpenAI, LangChain, Pinecone)

Cette architecture permet d'éviter les problèmes de segmentation fault et d'incompatibilité entre les bibliothèques.

## Prérequis

- Python 3.8 ou supérieur
- Clé API OpenAI
- Clé API Pinecone (optionnel, mais recommandé pour la recherche vectorielle)
- Clé API Alpha Vantage (optionnel, pour les données financières en temps réel)
- Tesseract OCR (optionnel, pour l'extraction de texte à partir de PDF)

## Installation

1. Clonez ce dépôt :
   ```
   git clone https://github.com/votre-utilisateur/business-intelligence-sec.git
   cd business-intelligence-sec
   ```

2. Exécutez le script d'installation et de lancement :
   ```
   ./run.sh
   ```

   Ce script va :
   - Créer un environnement virtuel Python
   - Installer les dépendances nécessaires
   - Créer un fichier `.env` si nécessaire
   - Lancer l'application

3. Configurez vos clés API dans le fichier `.env` :
   ```
   OPENAI_API_KEY=votre-clé-api-openai
   PINECONE_API_KEY=votre-clé-api-pinecone
   PINECONE_ENV=gcp-starter
   ALPHA_VANTAGE_API_KEY=votre-clé-api-alpha-vantage
   EDGAR_USER_AGENT=votre-email@example.com
   ```

## Utilisation

1. Accédez au dashboard à l'adresse : http://127.0.0.1:5115
2. Explorez les données financières d'Apple et Microsoft
3. Utilisez l'assistant IA en cliquant sur le bouton d'assistant en bas à droite
4. Posez des questions comme :
   - "Quelle est la marge brute d'Apple en 2024 ?"
   - "Compare les revenus d'Apple et Microsoft sur les 3 dernières années"
   - "Quelles sont les prévisions de croissance pour Microsoft ?"

### Traitement de documents PDF

Pour traiter un document PDF et en extraire des données financières :

1. Utilisez l'API `/api/pdf/process` avec une requête POST contenant le fichier PDF
2. Les données extraites seront retournées au format JSON
3. Le texte extrait et les données financières seront également sauvegardés dans des fichiers

Exemple avec curl :
```bash
curl -X POST -F "file=@rapport_financier.pdf" http://127.0.0.1:5115/api/pdf/process
```

### Exportation de données

Pour exporter des données financières dans différents formats :

1. Utilisez l'API `/api/export/<format>` avec une requête POST contenant les données à exporter
2. Les formats disponibles sont : csv, excel, pdf, json
3. Le fichier exporté sera retourné ou son chemin sera indiqué dans la réponse

Exemple avec curl :
```bash
curl -X POST -H "Content-Type: application/json" -d '{"name":"Apple","metrics":{"revenue":{"years":[2022,2023,2024],"values":[368234,375970,390036]}}}' http://127.0.0.1:5115/api/export/csv
```

## Structure des fichiers

- `app/run_direct.py` : Point d'entrée de l'application Flask
- `app/ai_bridge.py` : Pont entre l'application et les technologies d'IA
- `app/dashboard_static.html` : Dashboard financier statique
- `app/routes/api.py` : Routes API pour l'application
- `app/core/` : Modules principaux de l'application
  - `export_manager.py` : Gestion de l'exportation de données
  - `pdf_processor.py` : Traitement des fichiers PDF
  - `edgar_integration.py` : Intégration avec EDGAR
  - `alpha_vantage_integration.py` : Intégration avec Alpha Vantage
- `app/comm/` : Répertoire pour les fichiers de communication entre l'application et le pont IA
- `data/` : Données financières et documents
- `tests/` : Tests unitaires et d'intégration
- `requirements.txt` : Dépendances Python
- `run.sh` : Script d'installation et de lancement

## Tests

Le projet inclut des tests unitaires et d'intégration pour vérifier le bon fonctionnement des fonctionnalités.

Pour exécuter tous les tests :
```bash
python tests/run_tests.py
```

Pour plus d'informations sur les tests, consultez le fichier `tests/README.md`.

## Dépannage

### Problèmes d'installation des dépendances

Si vous rencontrez des problèmes lors de l'installation des dépendances, le script `run.sh` tentera d'installer les dépendances essentielles pour que l'application fonctionne avec des fonctionnalités réduites.

### Erreurs de segmentation

Si vous rencontrez des erreurs de segmentation (segmentation fault), assurez-vous que :
1. Vous utilisez le script `run.sh` pour lancer l'application
2. Vous n'avez pas modifié l'architecture en deux parties (application Flask + pont IA)

### Problèmes avec les API

Si l'assistant IA ne répond pas correctement :
1. Vérifiez que vos clés API sont correctement configurées dans le fichier `.env`
2. Consultez les logs dans `ai_bridge.log` pour plus d'informations

### Problèmes avec le traitement des PDF

Si l'extraction de texte à partir de PDF ne fonctionne pas correctement :
1. Assurez-vous que Tesseract OCR est installé sur votre système
2. Vérifiez les logs dans `pdf_processor.log` pour plus d'informations

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.  
