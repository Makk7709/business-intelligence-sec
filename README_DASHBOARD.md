# Dashboard Financier avec Assistant IA

Ce projet est un dashboard financier interactif avec un assistant IA intégré. Il permet de visualiser et d'analyser les données financières d'entreprises comme Apple et Microsoft, de générer des prédictions et d'interagir avec un assistant IA pour obtenir des informations supplémentaires.

## Fonctionnalités

- **Dashboard financier** : Visualisation des métriques clés pour Apple et Microsoft
- **Analyse comparative** : Comparaison des performances des entreprises
- **Prédictions financières** : Prévisions des performances futures
- **Mode nuit/jour** : Interface adaptable pour une meilleure lisibilité
- **Assistant IA** : Assistant intelligent pour répondre à vos questions

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/business-intelligence-sec.git
   cd business-intelligence-sec
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

### Lancement de l'application

Pour lancer l'application, exécutez la commande suivante :

```bash
python start_dashboard.py
```

L'application sera accessible à l'adresse http://127.0.0.1:5115 et s'ouvrira automatiquement dans votre navigateur par défaut.

### Arrêt de l'application

Pour arrêter l'application, appuyez sur Ctrl+C dans le terminal où vous avez lancé le script `start_dashboard.py`.

## Structure du projet

- `app/dashboard_static.html` : Fichier HTML statique contenant le dashboard
- `app/run_direct.py` : Script Flask pour servir le dashboard
- `app/run_dashboard_simple.py` : Script alternatif pour lancer le dashboard
- `app/GUIDE_UTILISATION.md` : Guide d'utilisation détaillé
- `app/fix_charts.js` : Script JavaScript pour corriger les problèmes d'affichage des graphiques
- `start_dashboard.py` : Script de démarrage simplifié

## Fonctionnalités détaillées

### Dashboard financier

Le dashboard financier affiche les métriques clés pour Apple et Microsoft, notamment :
- Revenus
- Bénéfice net
- Marge brute

### Analyse comparative

L'analyse comparative permet de comparer les performances d'Apple et Microsoft sur plusieurs années, notamment :
- Évolution des revenus
- Évolution des marges brutes
- Évolution des bénéfices nets
- Taux de croissance des revenus

### Prédictions financières

Les prédictions financières permettent de prévoir les performances futures d'Apple et Microsoft, notamment :
- Prédiction des revenus
- Prédiction des marges brutes

### Mode nuit/jour

Le mode nuit/jour permet d'adapter l'interface pour une meilleure lisibilité en fonction de vos préférences. Pour basculer entre les modes, cliquez sur le bouton en haut à droite de l'écran.

### Assistant IA

L'assistant IA vous permet de poser des questions sur les données financières d'Apple et Microsoft. Pour interagir avec l'assistant, cliquez sur le bouton en bas à droite de l'écran.

Exemples de questions :
- "Quels sont les revenus d'Apple ?"
- "Compare les marges de Microsoft et Apple"
- "Montre-moi les prévisions pour Apple"
- "Quelles sont les perspectives financières pour Apple ?"

## Résolution des problèmes courants

### L'application ne démarre pas

- Vérifiez qu'aucune autre application n'utilise le port 5115
- Le script `start_dashboard.py` tentera automatiquement de libérer le port si nécessaire
- Si cela échoue, vous pouvez manuellement libérer le port avec la commande : `lsof -i :5115 -t | xargs kill -9`

### Les graphiques ne s'affichent pas

- Vérifiez que JavaScript est activé dans votre navigateur
- Essayez un autre navigateur (Chrome ou Firefox sont recommandés)
- Rafraîchissez la page

### L'assistant IA ne répond pas

- Assurez-vous que votre question est claire et concise
- Rafraîchissez la page si l'assistant reste bloqué

## Sauvegarde

Une sauvegarde des fichiers importants est disponible dans le répertoire `backups/`. Vous pouvez utiliser ces fichiers en cas de problème avec les fichiers originaux. 