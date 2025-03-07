# Guide d'utilisation du Dashboard Financier

## Lancement de l'application

Vous avez plusieurs options pour lancer l'application :

### Option 1 : Version statique (recommandée)

La version statique est la plus simple et la plus fiable :

1. Ouvrez un terminal
2. Naviguez vers le répertoire du projet
3. Exécutez la commande : `python app/open_dashboard.py`
4. Le dashboard s'ouvrira automatiquement dans votre navigateur par défaut

### Option 2 : Version dynamique

Si vous avez besoin des fonctionnalités dynamiques :

1. Ouvrez un terminal
2. Naviguez vers le répertoire du projet
3. Exécutez la commande : `python app/run_dashboard_simple.py`
4. Accédez à l'application dans votre navigateur à l'adresse : `http://127.0.0.1:5115`

## Fonctionnalités principales

### Dashboard financier
- Visualisez les métriques financières clés pour Apple et Microsoft
  - Revenus
  - Bénéfice net
  - Marge brute
- Les données sont présentées sous forme de graphiques interactifs pour une meilleure compréhension

### Mode nuit/jour
- Cliquez sur le bouton de bascule en haut à droite pour changer entre le mode jour et le mode nuit
- Le mode nuit réduit la fatigue oculaire lors de l'utilisation prolongée

### Analyse comparative
- Comparez les performances d'Apple et Microsoft côte à côte
- Identifiez les tendances et les écarts de performance entre les deux entreprises
- Visualisez les données sous forme de graphiques à barres ou de lignes
- Analysez différentes métriques :
  - Revenus
  - Marges brutes
  - Bénéfice net
  - Taux de croissance

### Prédictions financières
- Consultez les prévisions de performance future basées sur les données historiques
- Les graphiques de prédiction vous aident à anticiper les tendances du marché
- Visualisez les prédictions pour :
  - Revenus futurs
  - Marges brutes futures

### Assistant IA
- Interagissez avec l'assistant IA en cliquant sur le bouton d'assistant en bas à droite
- Posez des questions comme :
  - "Quelle est la tendance des revenus d'Apple ?"
  - "Compare les marges brutes de Microsoft et Apple"
  - "Montre-moi les prévisions pour Microsoft"
  - "Quelles sont les perspectives financières pour Apple ?"

## Résolution des problèmes courants

### L'application ne démarre pas
- Essayez d'utiliser la version statique avec `python app/open_dashboard.py`
- Vérifiez qu'aucune autre instance de l'application n'est en cours d'exécution
- Si vous recevez un message d'erreur concernant le port 5115 déjà utilisé :
  1. Le script tentera automatiquement de libérer le port
  2. Si cela échoue, vous pouvez manuellement libérer le port avec la commande : `lsof -i :5115 -t | xargs kill -9`

### Les graphiques ne s'affichent pas
- Assurez-vous que votre navigateur est à jour
- Essayez d'utiliser la version statique du dashboard
- Vérifiez que JavaScript est activé dans votre navigateur
- Essayez un autre navigateur (Chrome ou Firefox sont recommandés)

### L'assistant IA ne répond pas
- Assurez-vous que votre question est claire et concise
- Rafraîchissez la page si l'assistant reste bloqué
- Vérifiez votre connexion internet

### Problèmes avec la version dynamique
Si vous rencontrez des problèmes avec la version dynamique, utilisez la version statique qui est plus fiable et ne nécessite pas de serveur Flask.

Pour toute autre question ou problème, n'hésitez pas à consulter la documentation complète ou à contacter l'équipe de support. 