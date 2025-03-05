# Intégration LangChain pour l'Analyse Financière

Ce module intègre LangChain à notre système d'analyse financière existant pour automatiser l'extraction et l'analyse des données financières à partir des rapports 10-K.

## Fonctionnalités

- **Extraction automatisée des données financières** : Utilise des modèles de langage pour extraire les métriques financières clés des rapports textuels.
- **Analyse financière avancée** : Génère des insights détaillés sur les performances financières des entreprises.
- **Prédictions de performance future** : Prédit les performances financières futures avec des niveaux de confiance.
- **Analyse comparative** : Compare les performances de plusieurs entreprises et fournit des recommandations d'investissement.
- **Rapports d'investissement** : Génère des rapports d'investissement professionnels et détaillés.
- **Approche hybride** : Combine l'extraction traditionnelle avec l'analyse basée sur LangChain pour des résultats optimaux.

## Prérequis

- Python 3.8+
- Bibliothèques Python : langchain-core, langchain-openai, python-dotenv, pandas, matplotlib, numpy, scikit-learn
- Clé API OpenAI (pour utiliser les modèles de langage)

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/business-intelligence-sec.git
   cd business-intelligence-sec
   ```

2. Installez les dépendances :
   ```bash
   pip install langchain-core langchain-openai python-dotenv pandas matplotlib numpy scikit-learn
   ```

3. Configurez votre clé API OpenAI :
   - Créez un fichier `.env` à la racine du projet
   - Ajoutez votre clé API : `OPENAI_API_KEY=votre_clé_api_ici`

## Structure du projet

- `src/langchain_processor.py` : Classe principale pour traiter les données financières avec LangChain
- `src/langchain_integration.py` : Intégration entre LangChain et notre système d'extraction traditionnel
- `src/demo_langchain.py` : Script de démonstration des fonctionnalités
- `src/financial_extractor.py` : Système d'extraction financière traditionnel

## Utilisation

### Utilisation de base

```python
from langchain_processor import FinancialAnalysisProcessor

# Initialiser le processeur
processor = FinancialAnalysisProcessor()

# Traiter un rapport financier
results = processor.process_financial_report(
    file_path="data/tsla_10k_extracted.txt",
    company_name="Tesla",
    output_dir="data/results/tesla"
)

# Traiter plusieurs rapports et générer une analyse comparative
results = processor.process_multiple_reports(
    file_paths=["data/tsla_10k_extracted.txt", "data/aapl_10k_extracted.txt"],
    company_names=["Tesla", "Apple"],
    output_dir="data/results/comparative"
)
```

### Approche hybride

```python
from langchain_integration import process_with_hybrid_approach, process_multiple_with_hybrid_approach

# Traiter un seul rapport avec l'approche hybride
results = process_with_hybrid_approach(
    file_path="data/tsla_10k_extracted.txt",
    company_name="Tesla",
    output_dir="data/results/hybrid/tesla"
)

# Traiter plusieurs rapports avec l'approche hybride
results = process_multiple_with_hybrid_approach(
    file_paths=["data/tsla_10k_extracted.txt", "data/aapl_10k_extracted.txt", "data/msft_10k_extracted.txt"],
    company_names=["Tesla", "Apple", "Microsoft"],
    output_dir="data/results/hybrid/comparative"
)
```

### Exécution via la ligne de commande

#### Processeur LangChain

```bash
python src/langchain_processor.py --files data/tsla_10k_extracted.txt --companies Tesla --output data/results/langchain
```

#### Intégration LangChain

```bash
# Comparer les méthodes d'extraction
python src/langchain_integration.py --files data/tsla_10k_extracted.txt --companies Tesla --output data/results/comparison --mode compare

# Améliorer l'analyse traditionnelle
python src/langchain_integration.py --files data/tsla_10k_extracted.txt --companies Tesla --output data/results/enhanced --mode enhance

# Approche hybride complète
python src/langchain_integration.py --files data/tsla_10k_extracted.txt data/aapl_10k_extracted.txt --companies Tesla Apple --output data/results/hybrid --mode hybrid
```

#### Script de démonstration

```bash
# Exécuter toutes les démonstrations
python src/demo_langchain.py

# Exécuter une démonstration spécifique
python src/demo_langchain.py --demo hybrid-multiple
```

## Résultats générés

L'intégration LangChain génère les résultats suivants :

- **Métriques financières extraites** : Revenus, revenu net, bénéfice brut, actifs, passifs, flux de trésorerie
- **Ratios financiers calculés** : Marges nettes, marges brutes, ratio dette/actifs
- **Analyse financière détaillée** : Tendances, forces, faiblesses, opportunités, risques
- **Prédictions de performance** : Prévisions pour les années futures avec niveaux de confiance
- **Visualisations** : Graphiques pour les métriques, ratios et prédictions
- **Rapports d'investissement** : Rapports détaillés avec recommandations
- **Analyse comparative** : Comparaison entre plusieurs entreprises

## Exemples de sorties

### Rapport d'investissement

```
# RAPPORT D'INVESTISSEMENT : TESLA

## RÉSUMÉ EXÉCUTIF

Tesla continue de montrer une croissance solide des revenus, avec une augmentation de 18.8% entre 2022 et 2024.
Cependant, la rentabilité montre des signes de pression, avec une marge nette en baisse de 16.6% en 2022 à 10.9% en 2024.
...
```

### Prédictions

```json
{
  "revenue": {
    "2025": {
      "value": 108203,
      "growth_rate": 9.12,
      "confidence_level": 79.22,
      "justification": "Basé sur la tendance de croissance historique..."
    },
    "2026": {
      "value": 116317,
      "growth_rate": 7.50,
      "confidence_level": 72.15,
      "justification": "La croissance devrait se poursuivre mais à un rythme plus modéré..."
    }
  },
  ...
}
```

## Personnalisation

Vous pouvez personnaliser les prompts utilisés dans `langchain_processor.py` pour adapter l'extraction et l'analyse à vos besoins spécifiques. Les prompts sont définis dans les méthodes de la classe `FinancialAnalysisProcessor`.

## Limitations

- Nécessite une clé API OpenAI valide avec des crédits suffisants
- La qualité de l'extraction dépend de la qualité et de la structure du texte d'entrée
- Les prédictions sont basées sur des données historiques et ne prennent pas en compte les facteurs externes

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 