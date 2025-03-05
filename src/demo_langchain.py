#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de démonstration pour l'intégration LangChain avec notre système d'analyse financière.
Ce script montre comment utiliser les différentes fonctionnalités de l'intégration.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Importer nos modules
from langchain_processor import FinancialAnalysisProcessor
from langchain_integration import (
    compare_extraction_methods,
    enhance_analysis_with_langchain,
    process_with_hybrid_approach,
    process_multiple_with_hybrid_approach
)

# Charger les variables d'environnement
load_dotenv()

def demo_extraction_comparison():
    """
    Démontre la comparaison entre l'extraction traditionnelle et LangChain
    """
    print("\n=== DEMONSTRATION: COMPARAISON DES METHODES D'EXTRACTION ===\n")
    
    # Fichiers de démonstration
    file_path = "data/tsla_10k_extracted.txt"
    company_name = "Tesla"
    output_dir = "data/results/demo/comparison"
    
    # Comparer les méthodes d'extraction
    comparison = compare_extraction_methods(file_path, company_name, output_dir)
    
    # Afficher un résumé des différences
    print("\nResume des differences d'extraction:")
    for metric, years in comparison["differences"].items():
        print(f"\n{metric.upper()}:")
        for year, values in years.items():
            diff_pct = values.get("difference_pct", "N/A")
            if isinstance(diff_pct, float):
                diff_pct = f"{diff_pct:.2f}%"
            print(f"  {year}: Traditionnel = {values.get('traditional')}, LangChain = {values.get('langchain')}, Difference = {diff_pct}")

def demo_enhanced_analysis():
    """
    Démontre l'amélioration de l'analyse traditionnelle avec LangChain
    """
    print("\n=== DEMONSTRATION: ANALYSE AMELIOREE AVEC LANGCHAIN ===\n")
    
    # Fichiers de démonstration
    file_path = "data/tsla_10k_extracted.txt"
    company_name = "Tesla"
    output_dir = "data/results/demo/enhanced"
    
    # Lire le fichier et extraire les métriques avec la méthode traditionnelle
    from financial_extractor import read_file, extract_key_metrics, calculate_financial_ratios
    
    text = read_file(file_path)
    metrics = extract_key_metrics(text)
    ratios = calculate_financial_ratios(metrics)
    
    # Améliorer l'analyse avec LangChain
    enhanced_results = enhance_analysis_with_langchain(metrics, ratios, company_name, output_dir)
    
    # Afficher un extrait du rapport
    print("\nExtrait du rapport d'investissement genere:")
    report_lines = enhanced_results["report"].split("\n")
    for i, line in enumerate(report_lines):
        if i < 20:  # Afficher les 20 premières lignes
            print(line)
    
    print("\n... [rapport tronque] ...\n")
    print(f"Rapport complet disponible dans: {output_dir}/{company_name.lower()}_enhanced_report.txt")

def demo_hybrid_approach_single():
    """
    Démontre l'approche hybride pour un seul rapport
    """
    print("\n=== DEMONSTRATION: APPROCHE HYBRIDE (UN SEUL RAPPORT) ===\n")
    
    # Fichiers de démonstration
    file_path = "data/tsla_10k_extracted.txt"
    company_name = "Tesla"
    output_dir = "data/results/demo/hybrid_single"
    
    # Traiter avec l'approche hybride
    enhanced_results = process_with_hybrid_approach(file_path, company_name, output_dir)
    
    # Afficher un résumé des prédictions
    print("\nResume des predictions generees:")
    if "predictions" in enhanced_results:
        predictions = enhanced_results["predictions"]
        if "revenue" in predictions:
            print("\nPredictions de revenus:")
            for year, data in predictions["revenue"].items():
                print(f"  {year}: {data.get('value')} (Croissance: {data.get('growth_rate')}%, Confiance: {data.get('confidence_level')}%)")
        
        if "net_income" in predictions:
            print("\nPredictions de revenu net:")
            for year, data in predictions["net_income"].items():
                print(f"  {year}: {data.get('value')} (Croissance: {data.get('growth_rate')}%, Confiance: {data.get('confidence_level')}%)")

def demo_hybrid_approach_multiple():
    """
    Démontre l'approche hybride pour plusieurs rapports
    """
    print("\n=== DEMONSTRATION: APPROCHE HYBRIDE (PLUSIEURS RAPPORTS) ===\n")
    
    # Fichiers de démonstration
    file_paths = [
        "data/tsla_10k_extracted.txt",
        "data/aapl_10k_extracted.txt",
        "data/msft_10k_extracted.txt"
    ]
    company_names = ["Tesla", "Apple", "Microsoft"]
    output_dir = "data/results/demo/hybrid_multiple"
    
    # Traiter avec l'approche hybride
    results = process_multiple_with_hybrid_approach(file_paths, company_names, output_dir)
    
    # Afficher un résumé de l'analyse comparative
    print("\nResume de l'analyse comparative:")
    if "comparative_analysis" in results:
        analysis = results["comparative_analysis"]
        
        if "rankings" in analysis:
            print("\nClassements des entreprises:")
            for metric, companies in analysis["rankings"].items():
                print(f"  {metric}: {', '.join(companies)}")
        
        if "recommendations" in analysis:
            print("\nRecommandations d'investissement:")
            for company, recommendation in analysis["recommendations"].items():
                print(f"  {company}: {recommendation}")

def demo_direct_langchain_usage():
    """
    Démontre l'utilisation directe du processeur LangChain
    """
    print("\n=== DEMONSTRATION: UTILISATION DIRECTE DE LANGCHAIN ===\n")
    
    # Initialiser le processeur LangChain
    processor = FinancialAnalysisProcessor()
    
    # Exemple de données financières
    financial_data = {
        "company": "Example Corp",
        "metrics": {
            "total_revenue": {
                "2022": 100000,
                "2023": 120000,
                "2024": 150000
            },
            "net_income": {
                "2022": 10000,
                "2023": 15000,
                "2024": 20000
            },
            "gross_profit": {
                "2022": 40000,
                "2023": 50000,
                "2024": 65000
            }
        }
    }
    
    # Calculer les ratios
    ratios = {
        "net_margin": {
            "2022": 0.10,
            "2023": 0.125,
            "2024": 0.133
        },
        "gross_margin": {
            "2022": 0.40,
            "2023": 0.417,
            "2024": 0.433
        }
    }
    
    # Analyser les métriques
    print("Analyse des metriques financieres...")
    analysis = processor.analyze_financial_metrics({
        "company": financial_data["company"],
        "metrics": financial_data["metrics"],
        "ratios": ratios
    })
    
    # Afficher un extrait de l'analyse
    print("\nExtrait de l'analyse:")
    print(json.dumps(analysis, indent=2)[:500] + "...\n")
    
    # Prédire les performances futures
    print("Prediction des performances futures...")
    predictions = processor.predict_future_performance({
        "company": financial_data["company"],
        "metrics": financial_data["metrics"],
        "ratios": ratios
    })
    
    # Afficher un extrait des prédictions
    print("\nExtrait des predictions:")
    print(json.dumps(predictions, indent=2)[:500] + "...\n")

def main():
    """
    Fonction principale pour exécuter les démonstrations
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Demonstration de l'integration LangChain")
    parser.add_argument("--demo", choices=["all", "compare", "enhance", "hybrid-single", "hybrid-multiple", "direct"],
                        default="all", help="Type de demonstration a executer")
    
    args = parser.parse_args()
    
    # Vérifier si la clé API est configurée
    if not os.getenv("OPENAI_API_KEY"):
        print("ERREUR: La variable d'environnement OPENAI_API_KEY n'est pas definie.")
        print("Veuillez definir cette variable dans le fichier .env ou l'environnement.")
        return
    
    # Exécuter les démonstrations sélectionnées
    if args.demo == "all" or args.demo == "compare":
        demo_extraction_comparison()
    
    if args.demo == "all" or args.demo == "enhance":
        demo_enhanced_analysis()
    
    if args.demo == "all" or args.demo == "hybrid-single":
        demo_hybrid_approach_single()
    
    if args.demo == "all" or args.demo == "hybrid-multiple":
        demo_hybrid_approach_multiple()
    
    if args.demo == "all" or args.demo == "direct":
        demo_direct_langchain_usage()
    
    print("\nDemonstration terminee avec succes!")

if __name__ == "__main__":
    main() 