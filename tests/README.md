# Tests pour l'application Business Intelligence SEC

Ce répertoire contient les tests unitaires et d'intégration pour l'application Business Intelligence SEC.

## Structure des tests

Les tests sont organisés comme suit :

- `unit/` : Tests unitaires pour les modules individuels
- `integration/` : Tests d'intégration pour les fonctionnalités combinées
- `run_tests.py` : Script pour exécuter tous les tests

## Tests unitaires

Les tests unitaires vérifient le bon fonctionnement des modules individuels de l'application. Ils sont situés dans le répertoire `unit/` et sont nommés selon le format `test_*.py`.

Tests unitaires disponibles :

- `test_export_manager.py` : Tests pour le module d'exportation de données
- `test_pdf_processor.py` : Tests pour le module de traitement des PDF

## Tests d'intégration

Les tests d'intégration vérifient le bon fonctionnement des fonctionnalités combinées de l'application. Ils sont situés dans le répertoire `integration/` et sont nommés selon le format `test_*.py`.

Tests d'intégration disponibles :

- `test_export_api.py` : Tests pour les routes API d'exportation
- `test_pdf_api.py` : Tests pour les routes API de traitement des PDF

## Exécution des tests

Pour exécuter tous les tests, utilisez la commande suivante :

```bash
python tests/run_tests.py
```

Pour exécuter uniquement les tests unitaires :

```bash
python tests/run_tests.py --type unit
```

Pour exécuter uniquement les tests d'intégration :

```bash
python tests/run_tests.py --type integration
```

Pour afficher les détails des tests :

```bash
python tests/run_tests.py --verbose
```

## Ajout de nouveaux tests

Pour ajouter un nouveau test unitaire, créez un fichier dans le répertoire `unit/` avec un nom commençant par `test_`.

Pour ajouter un nouveau test d'intégration, créez un fichier dans le répertoire `integration/` avec un nom commençant par `test_`.

Chaque fichier de test doit contenir une ou plusieurs classes de test héritant de `unittest.TestCase`.

Exemple de structure pour un nouveau test :

```python
import unittest

class TestMonModule(unittest.TestCase):
    def setUp(self):
        # Configuration avant chaque test
        pass
    
    def tearDown(self):
        # Nettoyage après chaque test
        pass
    
    def test_ma_fonction(self):
        # Test d'une fonction
        self.assertEqual(1 + 1, 2)
```

## Bonnes pratiques

- Chaque test doit être indépendant des autres tests
- Utilisez `setUp()` et `tearDown()` pour initialiser et nettoyer l'environnement de test
- Utilisez des mocks pour simuler les dépendances externes
- Testez les cas normaux et les cas d'erreur
- Écrivez des tests clairs et concis
- Commentez vos tests pour expliquer leur objectif 