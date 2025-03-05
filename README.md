# Business Intelligence pour l'Analyse Financière

Outil de Business Intelligence pour analyser les documents financiers 10-K et 10-Q des entreprises cotées en bourse. Ce projet permet d'extraire, d'analyser et de visualiser les données financières à partir des rapports officiels.

## Fonctionnalités

- **Extraction de données** : Extraction automatisée des métriques financières clés à partir des rapports 10-K
- **Analyse financière** : Calcul des ratios financiers et analyse des tendances
- **Analyse comparative** : Comparaison des performances de plusieurs entreprises
- **Prédictions** : Prévision des performances futures basée sur les données historiques
- **Visualisations** : Graphiques et tableaux pour une meilleure compréhension des données
- **Interface utilisateur** : Dashboard interactif pour explorer les données financières
- **Interface web Flask** : Application web pour visualiser et analyser les données financières

## Structure du projet

- `src/` : Code source du système d'analyse financière
  - `parser.py` : Extraction du texte à partir des PDF
  - `financial_analyzer.py` : Analyse des données financières
  - `financial_extractor.py` : Extraction des métriques financières
  - `prediction_test.py` : Tests des fonctionnalités de prédiction
  - `langchain_processor.py` : Intégration avec LangChain
  - `langchain_integration.py` : Fonctions d'intégration avec LangChain
  - `demo_langchain.py` : Démonstration des fonctionnalités LangChain
- `app/` : Interfaces utilisateur
  - `app.py` : Point d'entrée de l'application Streamlit
  - `data_loader.py` : Chargement des données financières
  - `visualizations.py` : Création des visualisations
  - `pages.py` : Définition des pages de l'application Streamlit
  - `flask_app.py` : Application Flask simple
  - `finance_dashboard.py` : Application Flask complète
  - `README.md` : Documentation de l'interface web
- `data/` : Données d'entrée et résultats
  - `results/` : Résultats de l'analyse financière
  - `predictions/` : Prédictions de performance future

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/Makk7709/business-intelligence-sec.git
   cd business-intelligence-sec
   ```

2. Créez un environnement virtuel et installez les dépendances :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configurez votre clé API OpenAI (pour les fonctionnalités LangChain) :
   - Créez un fichier `.env` à la racine du projet
   - Ajoutez votre clé API : `OPENAI_API_KEY=votre_clé_api_ici`

## Utilisation

### Extraction et analyse des données financières

```bash
# Extraire et analyser les données d'une seule entreprise
python src/financial_extractor.py --single

# Extraire et analyser les données de plusieurs entreprises
python src/financial_extractor.py
```

### Prédictions de performance future

```bash
# Générer des prédictions de performance future
python src/prediction_test.py
```

### Interface utilisateur Streamlit

```bash
# Lancer l'interface utilisateur Streamlit
streamlit run app/app.py
```

L'interface utilisateur Streamlit permet d'explorer les données financières de manière interactive :
- **Page d'accueil** : Présentation de l'application
- **Analyse individuelle** : Visualisation des métriques d'une entreprise
- **Analyse comparative** : Comparaison des performances de plusieurs entreprises
- **Prédictions** : Visualisation des prédictions de performance future

### Interface web Flask

```bash
# Lancer l'interface web Flask complète
python app/finance_dashboard.py

# Lancer l'interface web Flask simple
python app/flask_app.py
```

L'interface web Flask offre les fonctionnalités suivantes :
- **Visualisation des analyses existantes** : Exploration des résultats d'analyse
- **Exécution de nouvelles analyses** : Lancement d'analyses sur les données disponibles
- **Visualisation des métriques financières** : Tableaux et graphiques des métriques clés
- **Visualisation des ratios financiers** : Tableaux et graphiques des ratios calculés
- **Rapports d'investissement** : Affichage des rapports détaillés

Pour plus d'informations sur l'interface web, consultez le fichier `app/README.md`.

## Intégration LangChain

Ce projet intègre LangChain pour améliorer l'analyse financière avec des modèles de langage. Pour plus d'informations, consultez le fichier `README_LANGCHAIN.md`.

```bash
# Démonstration des fonctionnalités LangChain
python src/demo_langchain.py --demo enhance
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.  
