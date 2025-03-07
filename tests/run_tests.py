#!/usr/bin/env python
"""
Script pour exécuter tous les tests.
"""

import os
import sys
import unittest
import argparse

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_tests(test_type=None, verbose=False):
    """
    Exécute les tests.
    
    Args:
        test_type: Type de tests à exécuter ('unit', 'integration' ou None pour tous)
        verbose: Afficher les détails des tests
    
    Returns:
        True si tous les tests ont réussi, False sinon
    """
    # Créer le test loader
    loader = unittest.TestLoader()
    
    # Créer la suite de tests
    suite = unittest.TestSuite()
    
    # Déterminer les répertoires de tests
    if test_type == 'unit':
        test_dirs = ['unit']
    elif test_type == 'integration':
        test_dirs = ['integration']
    else:
        test_dirs = ['unit', 'integration']
    
    # Ajouter les tests à la suite
    for test_dir in test_dirs:
        test_path = os.path.join(os.path.dirname(__file__), test_dir)
        tests = loader.discover(test_path, pattern='test_*.py')
        suite.addTests(tests)
    
    # Exécuter les tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Retourner True si tous les tests ont réussi, False sinon
    return result.wasSuccessful()


if __name__ == '__main__':
    # Analyser les arguments de la ligne de commande
    parser = argparse.ArgumentParser(description='Exécuter les tests')
    parser.add_argument('--type', choices=['unit', 'integration'], help='Type de tests à exécuter')
    parser.add_argument('--verbose', action='store_true', help='Afficher les détails des tests')
    args = parser.parse_args()
    
    # Exécuter les tests
    success = run_tests(args.type, args.verbose)
    
    # Sortir avec le code approprié
    sys.exit(0 if success else 1) 