#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

class FinancialAnalysisProcessor:
    """
    Classe pour traiter les donnees financieres a l'aide de LangChain
    """
    
    def __init__(self, api_key=None, model_name="gpt-3.5-turbo"):
        """
        Initialise le processeur d'analyse financiere
        
        Args:
            api_key (str, optional): Cle API OpenAI. Si non fournie, utilise OPENAI_API_KEY de l'environnement
            model_name (str, optional): Nom du modèle à utiliser. Par défaut "gpt-3.5-turbo"
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        # Initialiser le modele LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=self.api_key
        )
    
    def _truncate_text(self, text, max_tokens=8000):
        """
        Tronque le texte pour limiter le nombre de tokens
        
        Args:
            text (str): Texte à tronquer
            max_tokens (int): Nombre maximum de tokens approximatif
            
        Returns:
            str: Texte tronqué
        """
        # Estimation approximative: 1 token = ~4 caractères en anglais
        max_chars = max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Garder le début et la fin du texte qui contiennent généralement les informations importantes
        # dans les rapports financiers (résumé au début, données financières à la fin)
        start_portion = int(max_chars * 0.6)  # 60% du début
        end_portion = int(max_chars * 0.4)    # 40% de la fin
        
        truncated_text = text[:start_portion] + "\n...[TEXTE TRONQUÉ]...\n" + text[-end_portion:]
        
        print(f"⚠️ Le texte a été tronqué de {len(text)} à {len(truncated_text)} caractères pour respecter les limites de l'API.")
        
        return truncated_text
    
    def extract_financial_data_from_text(self, text, company_name):
        """
        Extrait les donnees financieres d'un texte brut en utilisant LangChain
        
        Args:
            text (str): Texte brut du rapport financier
            company_name (str): Nom de l'entreprise
            
        Returns:
            dict: Donnees financieres extraites
        """
        # Tronquer le texte pour respecter les limites de l'API
        truncated_text = self._truncate_text(text)
        
        # Definir le prompt pour l'extraction des donnees financieres
        prompt = ChatPromptTemplate.from_template(
            """
            Tu es un expert en analyse financiere. Extrais les donnees financieres suivantes du texte ci-dessous pour {company_name}.
            Recherche les valeurs pour les annees 2022, 2023 et 2024 (si disponibles).
            
            Donnees a extraire:
            - Total des revenus (Total Revenue)
            - Revenu net (Net Income)
            - Benefice brut (Gross Profit)
            - Total des actifs (Total Assets)
            - Total des passifs (Total Liabilities)
            - Flux de tresorerie d'exploitation (Operating Cash Flow)
            
            Texte:
            {text}
            
            Reponds uniquement avec un objet JSON contenant les donnees extraites, avec la structure suivante:
            {{
                "company": "nom de l'entreprise",
                "metrics": {{
                    "total_revenue": {{
                        "2022": valeur,
                        "2023": valeur,
                        "2024": valeur
                    }},
                    "net_income": {{
                        "2022": valeur,
                        "2023": valeur,
                        "2024": valeur
                    }},
                    ...
                }}
            }}
            
            Si une valeur n'est pas disponible, utilise null. Assure-toi que toutes les valeurs sont des nombres (pas de chaines de caracteres avec des symboles $ ou des virgules).
            """
        )
        
        # Creer le parser de sortie JSON
        class FinancialData(BaseModel):
            company: str
            metrics: Dict[str, Dict[str, Optional[float]]]
        
        parser = JsonOutputParser(pydantic_object=FinancialData)
        
        # Creer la chaine de traitement
        chain = prompt | self.llm | parser
        
        # Executer la chaine
        try:
            result = chain.invoke({"company_name": company_name, "text": truncated_text})
            return result
        except Exception as e:
            print(f"⚠️ Erreur lors de l'extraction des données: {e}")
            # Retourner une structure de données vide mais valide en cas d'erreur
            return {
                "company": company_name,
                "metrics": {
                    "total_revenue": {},
                    "net_income": {},
                    "gross_profit": {},
                    "total_assets": {},
                    "total_liabilities": {},
                    "operating_cash_flow": {}
                }
            }
    
    def analyze_financial_metrics(self, metrics_data):
        """
        Analyse les metriques financieres et genere des insights
        
        Args:
            metrics_data (dict): Donnees des metriques financieres
            
        Returns:
            dict: Analyse et insights
        """
        # Definir le prompt pour l'analyse des metriques
        prompt = ChatPromptTemplate.from_template(
            """
            Tu es un analyste financier expert. Analyse les metriques financieres suivantes et fournis des insights detailles.
            
            Donnees financieres:
            {metrics_json}
            
            Fournis une analyse complete qui inclut:
            1. Tendances de croissance des revenus
            2. Analyse de la rentabilite (marges nettes et brutes)
            3. Sante du bilan (ratio dette/actifs)
            4. Efficacite operationnelle
            5. Risques potentiels et opportunites
            6. Recommandations pour les investisseurs
            
            Reponds avec un objet JSON structure contenant ton analyse.
            """
        )
        
        # Creer le parser de sortie JSON
        parser = JsonOutputParser()
        
        # Creer la chaine de traitement
        chain = prompt | self.llm | parser
        
        # Executer la chaine
        try:
            result = chain.invoke({"metrics_json": json.dumps(metrics_data, indent=2)})
            return result
        except Exception as e:
            print(f"⚠️ Erreur lors de l'analyse des métriques: {e}")
            return {"error": str(e), "analysis": "Analyse non disponible en raison d'une erreur."}
    
    def generate_comparative_analysis(self, companies_data):
        """
        Genere une analyse comparative entre plusieurs entreprises
        
        Args:
            companies_data (list): Liste des donnees financieres de plusieurs entreprises
            
        Returns:
            dict: Analyse comparative
        """
        # Definir le prompt pour l'analyse comparative
        prompt = ChatPromptTemplate.from_template(
            """
            Tu es un analyste financier expert. Realise une analyse comparative detaillee des entreprises suivantes basee sur leurs donnees financieres.
            
            Donnees financieres:
            {companies_json}
            
            Fournis une analyse comparative complete qui inclut:
            1. Comparaison des taux de croissance des revenus
            2. Comparaison des marges de profit
            3. Comparaison de l'efficacite operationnelle
            4. Forces et faiblesses relatives
            5. Classement des entreprises selon differents criteres financiers
            6. Recommandations d'investissement basees sur cette comparaison
            
            Reponds avec un objet JSON structure contenant ton analyse comparative.
            """
        )
        
        # Creer le parser de sortie JSON
        parser = JsonOutputParser()
        
        # Creer la chaine de traitement
        chain = prompt | self.llm | parser
        
        # Executer la chaine
        try:
            result = chain.invoke({"companies_json": json.dumps(companies_data, indent=2)})
            return result
        except Exception as e:
            print(f"⚠️ Erreur lors de l'analyse comparative: {e}")
            return {"error": str(e), "analysis": "Analyse comparative non disponible en raison d'une erreur."}
    
    def predict_future_performance(self, historical_data, years_ahead=2):
        """
        Predit les performances futures basees sur les donnees historiques
        
        Args:
            historical_data (dict): Donnees financieres historiques
            years_ahead (int): Nombre d'annees a predire
            
        Returns:
            dict: Predictions de performance
        """
        # Definir le prompt pour les predictions
        prompt = ChatPromptTemplate.from_template(
            """
            Tu es un analyste financier expert specialise dans les predictions financieres. 
            Utilise les donnees historiques suivantes pour predire les performances financieres pour les {years_ahead} prochaines annees.
            
            Donnees historiques:
            {historical_json}
            
            Fournis des predictions pour:
            1. Revenus totaux
            2. Revenu net
            3. Benefice brut
            4. Marges (nette et brute)
            5. Taux de croissance attendus
            
            Pour chaque prediction, inclus:
            - La valeur predite
            - Le taux de croissance par rapport a l'annee precedente
            - Un niveau de confiance (pourcentage)
            - Une justification de la prediction
            
            Reponds avec un objet JSON structure contenant tes predictions pour les annees {current_year} a {end_year}.
            """
        )
        
        # Creer le parser de sortie JSON
        parser = JsonOutputParser()
        
        # Obtenir l'annee actuelle et calculer l'annee de fin
        current_year = datetime.now().year
        end_year = current_year + years_ahead
        
        # Creer la chaine de traitement
        chain = prompt | self.llm | parser
        
        # Executer la chaine
        try:
            result = chain.invoke({
                "historical_json": json.dumps(historical_data, indent=2),
                "years_ahead": years_ahead,
                "current_year": current_year,
                "end_year": end_year
            })
            return result
        except Exception as e:
            print(f"⚠️ Erreur lors de la prédiction des performances futures: {e}")
            return {"error": str(e), "predictions": "Prédictions non disponibles en raison d'une erreur."}
    
    def generate_investment_report(self, company_data, analysis, predictions):
        """
        Genere un rapport d'investissement complet
        
        Args:
            company_data (dict): Donnees de l'entreprise
            analysis (dict): Analyse financiere
            predictions (dict): Predictions de performance
            
        Returns:
            str: Rapport d'investissement formate
        """
        # Definir le prompt pour le rapport d'investissement
        prompt = ChatPromptTemplate.from_template(
            """
            Tu es un analyste financier expert. Genere un rapport d'investissement professionnel et detaille base sur les donnees suivantes.
            
            Donnees de l'entreprise:
            {company_json}
            
            Analyse financiere:
            {analysis_json}
            
            Predictions:
            {predictions_json}
            
            Le rapport doit inclure:
            1. Resume executif
            2. Apercu de l'entreprise
            3. Analyse des performances financieres
            4. Analyse des ratios cles
            5. Predictions de performance future
            6. Risques et opportunites
            7. Recommandation d'investissement (Acheter/Conserver/Vendre)
            8. Justification de la recommandation
            
            Formate le rapport de maniere professionnelle avec des sections claires et des sous-titres.
            """
        )
        
        # Creer le parser de sortie texte
        parser = StrOutputParser()
        
        # Creer la chaine de traitement
        chain = prompt | self.llm | parser
        
        # Executer la chaine
        try:
            result = chain.invoke({
                "company_json": json.dumps(company_data, indent=2),
                "analysis_json": json.dumps(analysis, indent=2),
                "predictions_json": json.dumps(predictions, indent=2)
            })
            return result
        except Exception as e:
            print(f"⚠️ Erreur lors de la génération du rapport d'investissement: {e}")
            return f"Rapport non disponible en raison d'une erreur: {e}"
    
    def process_financial_report(self, file_path, company_name, output_dir):
        """
        Traite un rapport financier complet et genere une analyse
        
        Args:
            file_path (str): Chemin vers le fichier du rapport financier
            company_name (str): Nom de l'entreprise
            output_dir (str): Repertoire de sortie pour les resultats
            
        Returns:
            dict: Resultats complets de l'analyse
        """
        # Creer le repertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Lire le fichier texte
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        # Extraire les donnees financieres
        financial_data = self.extract_financial_data_from_text(text, company_name)
        
        # Calculer les ratios financiers
        metrics = financial_data['metrics']
        ratios = self._calculate_financial_ratios(metrics)
        
        # Analyser les metriques financieres
        analysis = self.analyze_financial_metrics({
            "company": company_name,
            "metrics": metrics,
            "ratios": ratios
        })
        
        # Predire les performances futures
        predictions = self.predict_future_performance({
            "company": company_name,
            "metrics": metrics,
            "ratios": ratios
        })
        
        # Generer le rapport d'investissement
        report = self.generate_investment_report(
            {"company": company_name, "metrics": metrics},
            analysis,
            predictions
        )
        
        # Sauvegarder les resultats
        results = {
            "company": company_name,
            "metrics": metrics,
            "ratios": ratios,
            "analysis": analysis,
            "predictions": predictions,
            "report": report
        }
        
        # Sauvegarder en JSON
        with open(os.path.join(output_dir, f"{company_name.lower()}_analysis.json"), 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        
        # Sauvegarder le rapport en texte
        with open(os.path.join(output_dir, f"{company_name.lower()}_report.txt"), 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Sauvegarder les metriques en CSV
        metrics_df = self._convert_metrics_to_dataframe(metrics)
        metrics_df.to_csv(os.path.join(output_dir, f"{company_name.lower()}_metrics.csv"))
        
        return results
    
    def process_multiple_reports(self, file_paths, company_names, output_dir):
        """
        Traite plusieurs rapports financiers et genere une analyse comparative
        
        Args:
            file_paths (list): Liste des chemins vers les fichiers des rapports financiers
            company_names (list): Liste des noms des entreprises
            output_dir (str): Repertoire de sortie pour les resultats
            
        Returns:
            dict: Resultats de l'analyse comparative
        """
        # Creer le repertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Traiter chaque rapport individuellement
        all_results = []
        for file_path, company_name in zip(file_paths, company_names):
            company_output_dir = os.path.join(output_dir, company_name.lower())
            os.makedirs(company_output_dir, exist_ok=True)
            
            results = self.process_financial_report(file_path, company_name, company_output_dir)
            all_results.append(results)
        
        # Generer l'analyse comparative
        comparative_analysis = self.generate_comparative_analysis(all_results)
        
        # Sauvegarder l'analyse comparative
        with open(os.path.join(output_dir, "comparative_analysis.json"), 'w', encoding='utf-8') as f:
            json.dump(comparative_analysis, f, indent=4)
        
        # Generer un rapport comparatif
        comparative_report = self._generate_comparative_report(all_results, comparative_analysis)
        
        # Sauvegarder le rapport comparatif
        with open(os.path.join(output_dir, "comparative_report.txt"), 'w', encoding='utf-8') as f:
            f.write(comparative_report)
        
        # Creer un fichier Excel avec des onglets pour chaque entreprise et l'analyse comparative
        self._export_to_excel(all_results, comparative_analysis, output_dir)
        
        return {
            "individual_results": all_results,
            "comparative_analysis": comparative_analysis,
            "comparative_report": comparative_report
        }
    
    def _calculate_financial_ratios(self, metrics):
        """
        Calcule les ratios financiers a partir des metriques
        
        Args:
            metrics (dict): Metriques financieres
            
        Returns:
            dict: Ratios financiers calcules
        """
        ratios = {
            "net_margin": {},
            "gross_margin": {},
            "debt_to_assets": {}
        }
        
        # Calculer les marges nettes
        for year in metrics["total_revenue"]:
            if metrics["total_revenue"].get(year) and metrics["net_income"].get(year):
                if metrics["total_revenue"][year] != 0:
                    ratios["net_margin"][year] = metrics["net_income"][year] / metrics["total_revenue"][year]
        
        # Calculer les marges brutes
        for year in metrics["total_revenue"]:
            if metrics["total_revenue"].get(year) and metrics["gross_profit"].get(year):
                if metrics["total_revenue"][year] != 0:
                    ratios["gross_margin"][year] = metrics["gross_profit"][year] / metrics["total_revenue"][year]
        
        # Calculer le ratio dette/actifs
        for year in metrics["total_assets"]:
            if metrics["total_assets"].get(year) and metrics["total_liabilities"].get(year):
                if metrics["total_assets"][year] != 0:
                    ratios["debt_to_assets"][year] = metrics["total_liabilities"][year] / metrics["total_assets"][year]
        
        return ratios
    
    def _convert_metrics_to_dataframe(self, metrics):
        """
        Convertit les metriques en DataFrame pandas
        
        Args:
            metrics (dict): Metriques financieres
            
        Returns:
            pandas.DataFrame: DataFrame des metriques
        """
        # Creer un dictionnaire pour le DataFrame
        data = {}
        
        # Pour chaque metrique, ajouter une colonne pour chaque annee
        for metric, years in metrics.items():
            for year, value in years.items():
                col_name = f"{metric}_{year}"
                data[col_name] = [value]
        
        # Creer le DataFrame
        return pd.DataFrame(data)
    
    def _generate_comparative_report(self, all_results, comparative_analysis):
        """
        Genere un rapport comparatif textuel
        
        Args:
            all_results (list): Resultats individuels pour chaque entreprise
            comparative_analysis (dict): Analyse comparative
            
        Returns:
            str: Rapport comparatif
        """
        # Definir le prompt pour le rapport comparatif
        prompt = ChatPromptTemplate.from_template(
            """
            Tu es un analyste financier expert. Genere un rapport comparatif detaille pour les entreprises suivantes.
            
            Donnees des entreprises:
            {companies_json}
            
            Analyse comparative:
            {comparative_json}
            
            Le rapport doit inclure:
            1. Resume executif
            2. Comparaison des performances financieres
            3. Forces et faiblesses relatives
            4. Classement des entreprises selon differents criteres
            5. Perspectives d'avenir pour chaque entreprise
            6. Recommandations d'investissement comparatives
            
            Formate le rapport de maniere professionnelle avec des sections claires et des sous-titres.
            """
        )
        
        # Creer le parser de sortie texte
        parser = StrOutputParser()
        
        # Creer la chaine de traitement
        chain = prompt | self.llm | parser
        
        # Executer la chaine
        result = chain.invoke({
            "companies_json": json.dumps(all_results, indent=2),
            "comparative_json": json.dumps(comparative_analysis, indent=2)
        })
        
        return result
    
    def _export_to_excel(self, all_results, comparative_analysis, output_dir):
        """
        Exporte les resultats vers un fichier Excel
        
        Args:
            all_results (list): Resultats individuels pour chaque entreprise
            comparative_analysis (dict): Analyse comparative
            output_dir (str): Repertoire de sortie
            
        Returns:
            str: Chemin vers le fichier Excel
        """
        # Creer un nouveau fichier Excel
        excel_path = os.path.join(output_dir, "financial_analysis.xlsx")
        writer = pd.ExcelWriter(excel_path, engine='openpyxl')
        
        # Creer un onglet pour chaque entreprise
        for result in all_results:
            company = result["company"]
            
            # Convertir les metriques en DataFrame
            metrics_df = pd.DataFrame()
            for metric, years in result["metrics"].items():
                for year, value in years.items():
                    metrics_df.loc[metric, year] = value
            
            # Convertir les ratios en DataFrame
            ratios_df = pd.DataFrame()
            for ratio, years in result["ratios"].items():
                for year, value in years.items():
                    ratios_df.loc[ratio, year] = value
            
            # Ecrire les DataFrames dans l'onglet de l'entreprise
            metrics_df.to_excel(writer, sheet_name=company[:31])
            
            # Ajouter les ratios en dessous des metriques
            start_row = len(metrics_df) + 3
            for i, (idx, row) in enumerate(ratios_df.iterrows()):
                for j, value in enumerate(row):
                    writer.sheets[company[:31]].cell(
                        row=start_row + i,
                        column=j + 2,
                        value=value
                    )
            
            # Ajouter les en-tetes pour les ratios
            writer.sheets[company[:31]].cell(
                row=start_row - 1,
                column=1,
                value="Financial Ratios"
            )
            for i, col in enumerate(ratios_df.columns):
                writer.sheets[company[:31]].cell(
                    row=start_row - 1,
                    column=i + 2,
                    value=col
                )
            for i, idx in enumerate(ratios_df.index):
                writer.sheets[company[:31]].cell(
                    row=start_row + i,
                    column=1,
                    value=idx
                )
        
        # Creer un onglet pour l'analyse comparative
        comparative_df = pd.DataFrame()
        
        # Extraire les donnees de l'analyse comparative
        if "rankings" in comparative_analysis:
            for metric, companies in comparative_analysis["rankings"].items():
                for rank, company in enumerate(companies, 1):
                    comparative_df.loc[company, metric] = rank
        
        # Ecrire le DataFrame comparatif
        if not comparative_df.empty:
            comparative_df.to_excel(writer, sheet_name="Comparative Analysis")
        
        # Sauvegarder le fichier Excel
        writer._save()
        
        return excel_path


def main():
    """
    Fonction principale pour executer le processeur d'analyse financiere
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyse financiere avec LangChain")
    parser.add_argument("--files", nargs="+", help="Chemins vers les fichiers des rapports financiers")
    parser.add_argument("--companies", nargs="+", help="Noms des entreprises correspondant aux fichiers")
    parser.add_argument("--output", default="data/results/langchain", help="Repertoire de sortie pour les resultats")
    parser.add_argument("--api_key", help="Cle API OpenAI (optionnel)")
    
    args = parser.parse_args()
    
    if not args.files or not args.companies or len(args.files) != len(args.companies):
        print("Erreur: Vous devez fournir un nombre egal de fichiers et de noms d'entreprises")
        return
    
    # Initialiser le processeur
    processor = FinancialAnalysisProcessor(api_key=args.api_key)
    
    # Traiter les rapports
    if len(args.files) == 1:
        # Traiter un seul rapport
        results = processor.process_financial_report(args.files[0], args.companies[0], args.output)
        print(f"Analyse terminee pour {args.companies[0]}. Resultats sauvegardes dans {args.output}")
    else:
        # Traiter plusieurs rapports
        results = processor.process_multiple_reports(args.files, args.companies, args.output)
        print(f"Analyse comparative terminee. Resultats sauvegardes dans {args.output}")


if __name__ == "__main__":
    main() 