# Dashboard d'Intelligence Financière avec IA

Ce projet est un dashboard d'intelligence financière qui intègre des technologies d'IA avancées (LangChain, ChatGPT et Pinecone) pour analyser des données financières d'entreprises comme Apple et Microsoft.

## Nouvelle structure du projet

Le projet a été restructuré pour améliorer la maintenabilité et la séparation des responsabilités :

```
business-intelligence-sec/
├── app/                    # Répertoire principal de l'application
│   ├── core/               # Logique métier
│   │   ├── ai_bridge.py    # Pont IA pour LangChain, ChatGPT et Pinecone
│   │   ├── ai_manager.py   # Gestionnaire du pont IA
│   │   └── data_loader.py  # Chargement des données financières
│   ├── models/             # Modèles de données
│   │   └── financial_data.py # Classes pour les données financières
│   ├── routes/             # Routes API et UI
│   │   ├── api.py          # Routes API
│   │   └── ui.py           # Routes UI
│   ├── static/             # Fichiers statiques
│   │   ├── css/            # Styles CSS
│   │   ├── js/             # Scripts JavaScript
│   │   └── img/            # Images
│   ├── ui/                 # Fichiers UI
│   │   └── dashboard_static.html # Dashboard statique
│   ├── comm/               # Répertoire pour la communication avec le pont IA
│   └── app.py              # Point d'entrée de l'application
├── data/                   # Données financières
├── logs/                   # Logs de l'application
├── tests/                  # Tests unitaires
├── .env                    # Variables d'environnement
├── .gitignore              # Fichiers à ignorer par Git
├── requirements.txt        # Dépendances Python
├── run.py                  # Script pour lancer l'application
└── README.md               # Documentation du projet
```

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

### Lancement de l'application

Pour lancer l'application, exécutez la commande suivante :

```
python run.py
```

Options disponibles :
- `--port PORT` : Port sur lequel lancer l'application (par défaut : 5115)
- `--host HOST` : Hôte sur lequel lancer l'application (par défaut : 127.0.0.1)
- `--debug` : Activer le mode debug
- `--no-ai` : Désactiver le pont IA

Exemple :
```
python run.py --port 8080 --debug
```

### Utilisation du dashboard

1. Accédez au dashboard à l'adresse : http://127.0.0.1:5115
2. Explorez les données financières d'Apple et Microsoft
3. Utilisez l'assistant IA en cliquant sur le bouton d'assistant en bas à droite
4. Posez des questions comme :
   - "Quelle est la marge brute d'Apple en 2024 ?"
   - "Compare les revenus d'Apple et Microsoft sur les 3 dernières années"
   - "Quelles sont les prévisions de croissance pour Microsoft ?"

## API

L'application expose plusieurs endpoints API :

- `GET /api/company/<company_code>` : Obtenir les données d'une entreprise
- `GET /api/comparative-data` : Obtenir les données comparatives
- `GET /api/predictions/<company_code>` : Obtenir les prédictions pour une entreprise
- `POST /api/ai-query` : Envoyer une requête à l'assistant IA
- `POST /api/load-document` : Charger un document dans Pinecone

## Dépannage

### Problèmes d'installation des dépendances

Si vous rencontrez des problèmes lors de l'installation des dépendances, le script `run.sh` tentera d'installer les dépendances essentielles pour que l'application fonctionne avec des fonctionnalités réduites.

### Erreurs de segmentation

Si vous rencontrez des erreurs de segmentation (segmentation fault), assurez-vous que :
1. Vous utilisez le script `run.py` pour lancer l'application
2. Vous n'avez pas modifié l'architecture en deux parties (application Flask + pont IA)

### Problèmes avec les API

Si l'assistant IA ne répond pas correctement :
1. Vérifiez que vos clés API sont correctement configurées dans le fichier `.env`
2. Consultez les logs dans `logs/ai_bridge.log` pour plus d'informations

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 