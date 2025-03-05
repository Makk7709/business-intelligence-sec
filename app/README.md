# Financial Analysis Dashboard

Ce dossier contient l'interface web pour l'analyse financière des rapports 10-K.

## Applications disponibles

Plusieurs versions de l'application sont disponibles :

1. **flask_app.py** - Application Flask simple pour visualiser les données JSON
2. **finance_dashboard.py** - Application Flask complète avec toutes les fonctionnalités d'analyse financière
3. **minimal_app.py** - Application Streamlit minimale (peut causer des erreurs de segmentation sur certains systèmes)

## Installation

Assurez-vous d'avoir installé toutes les dépendances requises :

```bash
pip install flask pandas matplotlib
```

## Utilisation

### Application Flask complète

Pour lancer l'application Flask complète :

```bash
python app/finance_dashboard.py
```

L'application sera accessible à l'adresse http://localhost:5000

### Application Flask simple

Pour lancer l'application Flask simple :

```bash
python app/flask_app.py
```

L'application sera accessible à l'adresse http://localhost:5000

## Fonctionnalités

L'application Flask complète (`finance_dashboard.py`) offre les fonctionnalités suivantes :

### Visualisation des analyses existantes

1. Sélectionnez un type d'analyse dans le menu déroulant
2. Cliquez sur "Load Files" pour afficher les fichiers disponibles
3. Sélectionnez un fichier d'analyse
4. Cliquez sur "View Analysis" pour afficher les résultats

### Exécution de nouvelles analyses

1. Sélectionnez une entreprise dans le menu déroulant
2. Choisissez le type d'analyse à effectuer :
   - **Traditional Analysis** : Analyse traditionnelle avec extraction de métriques financières
   - **LangChain Analysis** : Analyse utilisant LangChain pour l'extraction et l'analyse
   - **Enhanced Analysis** : Analyse améliorée avec LangChain pour des insights plus détaillés
3. Cliquez sur "Run Analysis" pour lancer l'analyse

### Navigation dans les résultats

L'application propose plusieurs onglets pour explorer les résultats :

- **Overview** : Présentation générale de l'application
- **Financial Metrics** : Tableau des métriques financières par année
- **Financial Ratios** : Tableau des ratios financiers par année
- **Charts** : Visualisations graphiques des métriques et ratios
- **Report** : Rapport d'investissement détaillé
- **Raw Data** : Données brutes au format JSON

## Structure des fichiers

- **flask_app.py** : Application Flask simple pour visualiser les données JSON
- **finance_dashboard.py** : Application Flask complète avec toutes les fonctionnalités
- **minimal_app.py** : Application Streamlit minimale
- **minimal_pandas.py** : Application Streamlit avec Pandas (peut causer des erreurs)
- **minimal_plus.py** : Version améliorée de l'application Streamlit minimale
- **intermediate_app.py** : Version intermédiaire de l'application Streamlit
- **simple_app.py** : Application Streamlit simple
- **data_loader.py** : Module pour charger les données financières
- **pages.py** : Module définissant les pages de l'application Streamlit
- **app.py** : Point d'entrée principal pour l'application Streamlit
- **visualizations.py** : Module pour générer des visualisations

## Dépannage

### Erreurs de segmentation avec Streamlit

Si vous rencontrez des erreurs de segmentation (segmentation fault) avec les applications Streamlit, essayez d'utiliser les applications Flask à la place. Ces erreurs peuvent être dues à des incompatibilités entre Streamlit et certaines versions de Python ou de bibliothèques.

### Problèmes d'affichage des graphiques

Si les graphiques ne s'affichent pas correctement, assurez-vous que Matplotlib est correctement installé et configuré pour votre environnement.

### Erreurs lors de l'exécution d'analyses

Si vous rencontrez des erreurs lors de l'exécution de nouvelles analyses, vérifiez que :
- Les fichiers 10-K extraits sont présents dans le répertoire `data/`
- La clé API OpenAI est correctement configurée dans le fichier `.env` (pour les analyses LangChain)
- Les modules d'analyse financière sont correctement installés 