import os
import json
import sys

def check_data_directory():
    """Vérifie la structure du répertoire de données et affiche les informations disponibles."""
    base_dir = "data/results"
    
    # Vérifier si le répertoire existe
    if not os.path.exists(base_dir):
        print(f"Le répertoire {base_dir} n'existe pas.")
        # Créer le répertoire
        try:
            os.makedirs(base_dir)
            print(f"Répertoire {base_dir} créé.")
        except Exception as e:
            print(f"Erreur lors de la création du répertoire: {e}")
        return
    
    # Lister les entreprises disponibles
    companies = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    if not companies:
        print(f"Aucune entreprise trouvée dans {base_dir}.")
        # Créer des données de test
        create_test_data()
        return
    
    print(f"Entreprises disponibles: {', '.join(companies)}")
    
    # Vérifier les fichiers pour chaque entreprise
    for company in companies:
        company_dir = os.path.join(base_dir, company)
        print(f"\nDonnées pour {company.capitalize()}:")
        
        # Vérifier les fichiers de métriques
        metrics_file = os.path.join(company_dir, "metrics.json")
        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, "r") as f:
                    metrics_data = json.load(f)
                print(f"  - Métriques: {len(metrics_data)} métriques disponibles")
                # Afficher les années disponibles
                if "revenue" in metrics_data:
                    years = sorted(metrics_data["revenue"].keys())
                    print(f"    Années: {', '.join(years)}")
            except Exception as e:
                print(f"  - Erreur lors de la lecture des métriques: {e}")
        else:
            print(f"  - Fichier de métriques non trouvé")
        
        # Vérifier les fichiers de ratios
        ratios_file = os.path.join(company_dir, "ratios.json")
        if os.path.exists(ratios_file):
            try:
                with open(ratios_file, "r") as f:
                    ratios_data = json.load(f)
                print(f"  - Ratios: {len(ratios_data)} ratios disponibles")
            except Exception as e:
                print(f"  - Erreur lors de la lecture des ratios: {e}")
        else:
            print(f"  - Fichier de ratios non trouvé")

def create_test_data():
    """Crée des données de test pour les entreprises."""
    base_dir = "data/results"
    
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
    check_data_directory() 