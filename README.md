# Dashboard d'Intelligence Financière avec IA

Ce projet est un dashboard d'intelligence financière qui intègre des technologies d'IA avancées (LangChain, ChatGPT et Pinecone) pour analyser des données financières d'entreprises comme Apple et Microsoft.

## Fonctionnalités

- **Dashboard interactif** : Visualisation des données financières d'Apple et Microsoft
- **Assistant IA intégré** : Posez des questions en langage naturel sur les données financières
- **Intégration multi-technologies** :
  - **OpenAI (ChatGPT)** : Pour le traitement du langage naturel
  - **LangChain** : Pour la création de chaînes de traitement IA complexes
  - **Pinecone** : Pour la recherche vectorielle et la récupération de contexte

## Architecture

L'application utilise une architecture en deux parties :
1. **Application Flask** : Sert le dashboard et gère les requêtes API
2. **Pont IA** : Processus séparé qui communique avec les technologies d'IA (OpenAI, LangChain, Pinecone)

Cette architecture permet d'éviter les problèmes de segmentation fault et d'incompatibilité entre les bibliothèques.

## Prérequis

- Python 3.8 ou supérieur
- Clé API OpenAI
- Clé API Pinecone (optionnel, mais recommandé pour la recherche vectorielle)

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
   ```

## Utilisation

1. Accédez au dashboard à l'adresse : http://127.0.0.1:5115
2. Explorez les données financières d'Apple et Microsoft
3. Utilisez l'assistant IA en cliquant sur le bouton d'assistant en bas à droite
4. Posez des questions comme :
   - "Quelle est la marge brute d'Apple en 2024 ?"
   - "Compare les revenus d'Apple et Microsoft sur les 3 dernières années"
   - "Quelles sont les prévisions de croissance pour Microsoft ?"

## Structure des fichiers

- `app/run_direct.py` : Point d'entrée de l'application Flask
- `app/ai_bridge.py` : Pont entre l'application et les technologies d'IA
- `app/dashboard_static.html` : Dashboard financier statique
- `app/comm/` : Répertoire pour les fichiers de communication entre l'application et le pont IA
- `data/` : Données financières et documents
- `requirements.txt` : Dépendances Python
- `run.sh` : Script d'installation et de lancement

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

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.  
