import os
import json
import sys

def create_test_data():
    """Crée des données de test pour les entreprises Tesla, Apple et Microsoft."""
    base_dir = "data/results"
    
    # Créer le répertoire de base s'il n'existe pas
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Créer des répertoires pour chaque entreprise
    companies = ["tesla", "apple", "microsoft"]
    
    for company in companies:
        company_dir = os.path.join(base_dir, company)
        
        # Créer le répertoire de l'entreprise s'il n'existe pas
        if not os.path.exists(company_dir):
            os.makedirs(company_dir)
        
        # Créer des données de métriques
        metrics_data = {
            "revenue": {"2022": 81462, "2023": 94000, "2024": 96702},
            "net_income": {"2022": 12656, "2023": 11330, "2024": 10500},
            "gross_profit": {"2022": 20853, "2023": 21501, "2024": 22894},
            "total_assets": {"2022": 128142, "2023": 135000, "2024": 142000},
            "total_liabilities": {"2022": 54848, "2023": 58000, "2024": 62000}
        }
        
        # Ajuster les données pour chaque entreprise
        if company == "apple":
            for key in metrics_data:
                for year in metrics_data[key]:
                    metrics_data[key][year] *= 3
        elif company == "microsoft":
            for key in metrics_data:
                for year in metrics_data[key]:
                    metrics_data[key][year] *= 2
        
        # Enregistrer les données de métriques
        metrics_file = os.path.join(company_dir, "metrics.json")
        with open(metrics_file, "w") as f:
            json.dump(metrics_data, f, indent=2)
        
        # Créer des données de ratios
        ratios_data = {
            "net_margin": {"2022": 15.5, "2023": 12.1, "2024": 10.9},
            "gross_margin": {"2022": 25.6, "2023": 22.9, "2024": 23.7},
            "debt_to_assets": {"2022": 0.43, "2023": 0.43, "2024": 0.44}
        }
        
        # Ajuster les ratios pour chaque entreprise
        if company == "apple":
            ratios_data["net_margin"] = {"2022": 25.3, "2023": 24.8, "2024": 25.0}
            ratios_data["gross_margin"] = {"2022": 43.3, "2023": 44.0, "2024": 45.3}
            ratios_data["debt_to_assets"] = {"2022": 0.35, "2023": 0.33, "2024": 0.32}
        elif company == "microsoft":
            ratios_data["net_margin"] = {"2022": 36.7, "2023": 37.0, "2024": 38.2}
            ratios_data["gross_margin"] = {"2022": 68.4, "2023": 69.7, "2024": 70.1}
            ratios_data["debt_to_assets"] = {"2022": 0.28, "2023": 0.27, "2024": 0.26}
        
        # Enregistrer les données de ratios
        ratios_file = os.path.join(company_dir, "ratios.json")
        with open(ratios_file, "w") as f:
            json.dump(ratios_data, f, indent=2)
    
    print(f"Données de test créées pour {', '.join(companies)}")

if __name__ == "__main__":
    create_test_data() 