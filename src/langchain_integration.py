#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import argparse
from dotenv import load_dotenv

# Importer nos modules
from financial_extractor import (
    read_file, 
    extract_key_metrics, 
    calculate_financial_ratios,
    create_visualizations,
    save_results,
    process_multiple_reports,
    create_comparative_visualizations,
    save_comparative_results,
    predict_future_performance,
    create_prediction_visualizations,
    save_prediction_results
)
from langchain_processor import FinancialAnalysisProcessor

# Charger les variables d'environnement
load_dotenv()

def compare_extraction_methods(file_path, company_name, output_dir):
    """
    Compare les résultats d'extraction entre notre méthode traditionnelle et LangChain
    
    Args:
        file_path (str): Chemin vers le fichier du rapport financier
        company_name (str): Nom de l'entreprise
        output_dir (str): Répertoire de sortie pour les résultats
        
    Returns:
        dict: Comparaison des résultats
    """
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Méthode traditionnelle
    print(f"Extraction traditionnelle pour {company_name}...")
    text = read_file(file_path)
    traditional_metrics = extract_key_metrics(text)
    traditional_ratios = calculate_financial_ratios(traditional_metrics)
    
    # Méthode LangChain
    print(f"Extraction avec LangChain pour {company_name}...")
    processor = FinancialAnalysisProcessor()
    langchain_results = processor.process_financial_report(file_path, company_name, os.path.join(output_dir, "langchain"))
    langchain_metrics = langchain_results["metrics"]
    langchain_ratios = langchain_results["ratios"]
    
    # Comparer les résultats
    comparison = {
        "company": company_name,
        "traditional_extraction": {
            "metrics": traditional_metrics,
            "ratios": traditional_ratios
        },
        "langchain_extraction": {
            "metrics": langchain_metrics,
            "ratios": langchain_ratios
        },
        "differences": {}
    }
    
    # Calculer les différences pour chaque métrique
    for metric in traditional_metrics:
        if metric in langchain_metrics:
            comparison["differences"][metric] = {}
            for year in traditional_metrics[metric]:
                if year in langchain_metrics[metric]:
                    trad_value = traditional_metrics[metric][year]
                    lang_value = langchain_metrics[metric][year]
                    
                    # Calculer la différence en pourcentage si les deux valeurs existent
                    if trad_value is not None and lang_value is not None and trad_value != 0:
                        diff_pct = ((lang_value - trad_value) / trad_value) * 100
                        comparison["differences"][metric][year] = {
                            "traditional": trad_value,
                            "langchain": lang_value,
                            "difference_pct": diff_pct
                        }
    
    # Sauvegarder la comparaison
    comparison_path = os.path.join(output_dir, f"{company_name.lower()}_extraction_comparison.json")
    with open(comparison_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=4)
    
    print(f"Comparaison des extractions sauvegardée dans {comparison_path}")
    
    return comparison

def enhance_analysis_with_langchain(metrics, ratios, company_name, output_dir):
    """
    Améliore l'analyse financière traditionnelle avec des insights de LangChain
    
    Args:
        metrics (dict): Métriques financières extraites
        ratios (dict): Ratios financiers calculés
        company_name (str): Nom de l'entreprise
        output_dir (str): Répertoire de sortie pour les résultats
        
    Returns:
        dict: Analyse améliorée
    """
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Amélioration de l'analyse pour {company_name} avec LangChain...")
    
    # Initialiser le processeur LangChain
    processor = FinancialAnalysisProcessor()
    
    # Analyser les métriques avec LangChain
    analysis = processor.analyze_financial_metrics({
        "company": company_name,
        "metrics": metrics,
        "ratios": ratios
    })
    
    # Prédire les performances futures avec LangChain
    predictions = processor.predict_future_performance({
        "company": company_name,
        "metrics": metrics,
        "ratios": ratios
    })
    
    # Générer un rapport d'investissement
    report = processor.generate_investment_report(
        {"company": company_name, "metrics": metrics},
        analysis,
        predictions
    )
    
    # Sauvegarder les résultats
    enhanced_results = {
        "company": company_name,
        "metrics": metrics,
        "ratios": ratios,
        "analysis": analysis,
        "predictions": predictions,
        "report": report
    }
    
    # Sauvegarder en JSON
    json_path = os.path.join(output_dir, f"{company_name.lower()}_enhanced_analysis.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_results, f, indent=4)
    
    # Sauvegarder le rapport en texte
    report_path = os.path.join(output_dir, f"{company_name.lower()}_enhanced_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Analyse améliorée sauvegardée dans {json_path}")
    print(f"Rapport d'investissement sauvegardé dans {report_path}")
    
    # Adapter le format des prédictions pour les visualisations
    adapted_predictions = {
        'revenue': {},
        'net_income': {},
        'gross_profit': {},
        'net_margin': {},
        'gross_margin': {},
        'confidence': {}
    }
    
    # Extraire les prédictions du format LangChain vers le format attendu par create_prediction_visualizations
    if 'predictions' in predictions:
        for year, year_data in predictions['predictions'].items():
            # Traiter les métriques financières
            if 'total_revenue' in year_data:
                value = clean_value(year_data['total_revenue']['predicted_value'])
                adapted_predictions['revenue'][year] = value
                adapted_predictions['confidence']['revenue'] = year_data['total_revenue'].get('confidence_level', 70)
            
            if 'net_income' in year_data:
                value = clean_value(year_data['net_income']['predicted_value'])
                adapted_predictions['net_income'][year] = value
                adapted_predictions['confidence']['net_income'] = year_data['net_income'].get('confidence_level', 70)
            
            if 'gross_profit' in year_data:
                value = clean_value(year_data['gross_profit']['predicted_value'])
                adapted_predictions['gross_profit'][year] = value
                adapted_predictions['confidence']['gross_profit'] = year_data['gross_profit'].get('confidence_level', 70)
            
            # Traiter les ratios
            if 'net_margin' in year_data:
                adapted_predictions['net_margin'][year] = year_data['net_margin']['predicted_value']
                adapted_predictions['confidence']['net_margin'] = year_data['net_margin'].get('confidence_level', 70)
            
            if 'gross_margin' in year_data:
                adapted_predictions['gross_margin'][year] = year_data['gross_margin']['predicted_value']
                adapted_predictions['confidence']['gross_margin'] = year_data['gross_margin'].get('confidence_level', 70)
    
    # Créer des visualisations pour les prédictions adaptées
    try:
        create_prediction_visualizations(metrics, ratios, adapted_predictions, output_dir)
        # Sauvegarder les résultats des prédictions
        save_prediction_results(adapted_predictions, output_dir, ratios)
    except Exception as e:
        print(f"Erreur lors de la création des visualisations prédictives: {e}")
    
    return enhanced_results

def clean_value(value_str):
    """
    Convertit une chaîne de caractères représentant une valeur financière en nombre
    
    Args:
        value_str (str): Chaîne de caractères à convertir
        
    Returns:
        float: Valeur numérique
    """
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    try:
        # Supprimer les caractères non numériques sauf le point décimal
        cleaned = ''.join(c for c in value_str if c.isdigit() or c == '.')
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0

def process_with_hybrid_approach(file_path, company_name, output_dir):
    """
    Traite un rapport financier avec une approche hybride (extraction traditionnelle + analyse LangChain)
    
    Args:
        file_path (str): Chemin vers le fichier du rapport financier
        company_name (str): Nom de l'entreprise
        output_dir (str): Répertoire de sortie pour les résultats
        
    Returns:
        dict: Résultats de l'analyse hybride
    """
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Traitement hybride pour {company_name}...")
    
    # Extraction traditionnelle
    text = read_file(file_path)
    metrics = extract_key_metrics(text)
    ratios = calculate_financial_ratios(metrics)
    
    # Créer les visualisations traditionnelles
    company_output_dir = os.path.join(output_dir, company_name.lower())
    os.makedirs(company_output_dir, exist_ok=True)
    create_visualizations(metrics, ratios, company_output_dir)
    
    # Sauvegarder les résultats traditionnels
    save_results(metrics, ratios, company_output_dir)
    
    # Améliorer l'analyse avec LangChain
    enhanced_results = enhance_analysis_with_langchain(metrics, ratios, company_name, company_output_dir)
    
    return enhanced_results

def process_multiple_with_hybrid_approach(file_paths, company_names, output_dir):
    """
    Traite plusieurs rapports financiers avec une approche hybride et génère une analyse comparative
    
    Args:
        file_paths (list): Liste des chemins vers les fichiers des rapports financiers
        company_names (list): Liste des noms des entreprises
        output_dir (str): Répertoire de sortie pour les résultats
        
    Returns:
        dict: Résultats de l'analyse comparative hybride
    """
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    print("Traitement hybride de plusieurs rapports...")
    
    # Traiter chaque rapport individuellement
    all_metrics = {}
    all_ratios = {}
    all_enhanced_results = []
    
    for file_path, company_name in zip(file_paths, company_names):
        enhanced_results = process_with_hybrid_approach(file_path, company_name, output_dir)
        all_metrics[company_name] = enhanced_results["metrics"]
        all_ratios[company_name] = enhanced_results["ratios"]
        all_enhanced_results.append(enhanced_results)
    
    # Créer des visualisations comparatives
    comparative_dir = os.path.join(output_dir, "comparative")
    os.makedirs(comparative_dir, exist_ok=True)
    create_comparative_visualizations(all_metrics, all_ratios, comparative_dir)
    
    # Sauvegarder les résultats comparatifs traditionnels
    save_comparative_results(all_metrics, all_ratios, comparative_dir)
    
    # Générer une analyse comparative avec LangChain
    processor = FinancialAnalysisProcessor()
    comparative_analysis = processor.generate_comparative_analysis(all_enhanced_results)
    
    # Sauvegarder l'analyse comparative
    comparative_json_path = os.path.join(comparative_dir, "enhanced_comparative_analysis.json")
    with open(comparative_json_path, 'w', encoding='utf-8') as f:
        json.dump(comparative_analysis, f, indent=4)
    
    # Générer un rapport comparatif
    comparative_report = processor._generate_comparative_report(all_enhanced_results, comparative_analysis)
    
    # Sauvegarder le rapport comparatif
    comparative_report_path = os.path.join(comparative_dir, "enhanced_comparative_report.txt")
    with open(comparative_report_path, 'w', encoding='utf-8') as f:
        f.write(comparative_report)
    
    print(f"Analyse comparative améliorée sauvegardée dans {comparative_json_path}")
    print(f"Rapport comparatif amélioré sauvegardé dans {comparative_report_path}")
    
    # Créer un fichier Excel avec des onglets pour chaque entreprise et l'analyse comparative
    processor._export_to_excel(all_enhanced_results, comparative_analysis, comparative_dir)
    
    return {
        "individual_results": all_enhanced_results,
        "comparative_analysis": comparative_analysis,
        "comparative_report": comparative_report
    }

def main():
    """
    Fonction principale pour exécuter l'intégration LangChain
    """
    parser = argparse.ArgumentParser(description="Intégration LangChain pour l'analyse financière")
    parser.add_argument("--files", nargs="+", help="Chemins vers les fichiers des rapports financiers")
    parser.add_argument("--companies", nargs="+", help="Noms des entreprises correspondant aux fichiers")
    parser.add_argument("--output", default="data/results/hybrid", help="Répertoire de sortie pour les résultats")
    parser.add_argument("--mode", choices=["compare", "enhance", "hybrid"], default="hybrid",
                        help="Mode d'intégration: compare (comparer les méthodes d'extraction), enhance (améliorer l'analyse traditionnelle), hybrid (approche hybride complète)")
    
    args = parser.parse_args()
    
    if not args.files or not args.companies or len(args.files) != len(args.companies):
        print("Erreur: Vous devez fournir un nombre égal de fichiers et de noms d'entreprises")
        return
    
    if args.mode == "compare":
        # Comparer les méthodes d'extraction
        for file_path, company_name in zip(args.files, args.companies):
            compare_extraction_methods(file_path, company_name, args.output)
    
    elif args.mode == "enhance":
        # Améliorer l'analyse traditionnelle avec LangChain
        for file_path, company_name in zip(args.files, args.companies):
            text = read_file(file_path)
            metrics = extract_key_metrics(text)
            ratios = calculate_financial_ratios(metrics)
            enhance_analysis_with_langchain(metrics, ratios, company_name, args.output)
    
    elif args.mode == "hybrid":
        # Approche hybride complète
        if len(args.files) == 1:
            # Traiter un seul rapport
            process_with_hybrid_approach(args.files[0], args.companies[0], args.output)
        else:
            # Traiter plusieurs rapports
            process_multiple_with_hybrid_approach(args.files, args.companies, args.output)
    
    print("Intégration LangChain terminée avec succès!")

if __name__ == "__main__":
    main() 