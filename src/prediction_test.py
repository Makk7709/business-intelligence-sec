#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour les fonctionnalités de prédiction financière.
Ce script utilise scikit-learn pour implémenter une régression linéaire
et prédire les performances financières futures de Tesla.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import matplotlib.ticker as mtick

# Ajouter le répertoire parent au chemin de recherche des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Données financières historiques de Tesla (en millions de $)
years = np.array([2022, 2023, 2024]).reshape(-1, 1)  # Années sous forme de tableau 2D
revenues = np.array([81462, 96773, 97690])  # Revenus pour chaque année
net_income = np.array([12583, 14975, 7146])  # Bénéfice net pour chaque année
gross_profit = np.array([20853, 17660, 17450])  # Bénéfice brut pour chaque année

# Années futures pour la prédiction
future_years = np.array([2025, 2026]).reshape(-1, 1)

def predict_metric(years, values, future_years, metric_name):
    """Prédit les valeurs futures d'une métrique financière en utilisant une régression linéaire."""
    # Créer et entraîner le modèle
    model = LinearRegression()
    model.fit(years, values)
    
    # Calculer le coefficient de détermination (R²)
    r_squared = model.score(years, values)
    confidence = r_squared * 100
    
    # Prédire les valeurs futures
    predicted_values = model.predict(future_years)
    
    # Calculer le taux de croissance annuel moyen prédit
    growth_rate = ((predicted_values[1] / values[-1]) ** (1/2) - 1) * 100
    
    print(f"Prédiction {metric_name} pour 2025 : ${predicted_values[0]:,.0f}")
    print(f"Prédiction {metric_name} pour 2026 : ${predicted_values[1]:,.0f}")
    print(f"Taux de croissance annuel moyen prédit pour {metric_name} : {growth_rate:.2f}%")
    print(f"Confiance dans la prédiction pour {metric_name} : {confidence:.2f}%")
    
    return predicted_values, confidence, growth_rate

def create_visualization(years, values, future_years, predicted_values, confidence, growth_rate, metric_name):
    """Crée une visualisation pour les prédictions financières."""
    plt.figure(figsize=(12, 7))
    
    # Définir un style professionnel pour les graphiques
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # Couleurs pour les graphiques
    historical_color = '#1f77b4'  # Bleu
    prediction_color = '#ff7f0e'  # Orange
    confidence_color = '#ff7f0e20'  # Orange transparent pour l'intervalle de confiance
    
    # Toutes les années et valeurs
    all_years = np.vstack((years, future_years)).flatten()
    all_values = np.append(values, predicted_values)
    
    # Tracer les données historiques
    plt.plot(years.flatten(), values, 'o-', color=historical_color, linewidth=3, markersize=10, label='Données historiques')
    
    # Tracer les prédictions
    plt.plot(future_years.flatten(), predicted_values, 'o--', color=prediction_color, linewidth=3, markersize=10, label='Prédictions')
    
    # Ajouter une zone d'intervalle de confiance
    confidence_level = confidence / 100
    # Calculer un intervalle de confiance simple basé sur le niveau de confiance
    confidence_range = [(1 - confidence_level) * value * 0.5 for value in predicted_values]
    
    plt.fill_between(
        future_years.flatten(),
        [predicted_values[i] - confidence_range[i] for i in range(len(predicted_values))],
        [predicted_values[i] + confidence_range[i] for i in range(len(predicted_values))],
        color=confidence_color, alpha=0.5,
        label=f'Intervalle de confiance ({confidence_level:.2%})'
    )
    
    # Ajouter les valeurs sur les points
    for i, year in enumerate(all_years):
        if i < len(years):
            value = values[i]
            plt.annotate(f'${value:,.0f}', 
                        xy=(year, value), 
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold')
        else:
            value = predicted_values[i - len(years)]
            plt.annotate(f'${value:,.0f}', 
                        xy=(year, value), 
                        xytext=(0, 10),
                        textcoords='offset points',
                        ha='center', va='bottom',
                        fontsize=9, fontweight='bold',
                        color=prediction_color)
    
    # Ajouter le taux de croissance prédit
    growth_text = f'Taux de croissance annuel moyen prédit: {growth_rate:.2f}%'
    plt.figtext(0.5, 0.01, growth_text, ha='center', fontsize=12, fontweight='bold')
    
    # Formater l'axe Y pour afficher les valeurs en millions/milliards
    def format_y_axis(value, pos):
        if value >= 1e9:
            return f'${value/1e9:.1f}B'
        elif value >= 1e6:
            return f'${value/1e6:.1f}M'
        else:
            return f'${value:.0f}'
    
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(format_y_axis))
    
    # Ajouter des titres et des étiquettes
    metric_names = {
        'revenue': 'Revenus',
        'net_income': 'Bénéfice Net',
        'gross_profit': 'Bénéfice Brut'
    }
    
    plt.title(f'Prédiction des {metric_names.get(metric_name, metric_name)} (2022-2026)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Année', fontsize=12, labelpad=10)
    plt.ylabel('Valeur ($)', fontsize=12, labelpad=10)
    
    # Personnaliser les ticks de l'axe X
    plt.xticks(all_years, fontsize=10)
    plt.yticks(fontsize=10)
    
    # Ajouter une grille
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Ajouter une légende
    plt.legend(loc='best', fontsize=10)
    
    # Ajuster les marges
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Sauvegarder le graphique
    os.makedirs('data/results/predictions', exist_ok=True)
    output_path = f'data/results/predictions/prediction_{metric_name}.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Graphique de prédiction pour {metric_name} sauvegardé dans {output_path}")
    plt.close()

def main():
    """Fonction principale qui exécute les prédictions financières."""
    print("🚀 Démarrage des prédictions financières...")
    
    # Prédiction des revenus
    predicted_revenues, revenue_confidence, revenue_growth_rate = predict_metric(years, revenues, future_years, 'revenue')
    create_visualization(years, revenues, future_years, predicted_revenues, revenue_confidence, revenue_growth_rate, 'revenue')
    
    # Prédiction du bénéfice net
    predicted_net_income, net_income_confidence, net_income_growth_rate = predict_metric(years, net_income, future_years, 'net_income')
    create_visualization(years, net_income, future_years, predicted_net_income, net_income_confidence, net_income_growth_rate, 'net_income')
    
    # Prédiction du bénéfice brut
    predicted_gross_profit, gross_profit_confidence, gross_profit_growth_rate = predict_metric(years, gross_profit, future_years, 'gross_profit')
    create_visualization(years, gross_profit, future_years, predicted_gross_profit, gross_profit_confidence, gross_profit_growth_rate, 'gross_profit')
    
    # Calcul des marges prédites
    net_margin_2025 = (predicted_net_income[0] / predicted_revenues[0]) * 100
    net_margin_2026 = (predicted_net_income[1] / predicted_revenues[1]) * 100
    
    gross_margin_2025 = (predicted_gross_profit[0] / predicted_revenues[0]) * 100
    gross_margin_2026 = (predicted_gross_profit[1] / predicted_revenues[1]) * 100
    
    print(f"\nMarge nette prédite pour 2025 : {net_margin_2025:.2f}%")
    print(f"Marge nette prédite pour 2026 : {net_margin_2026:.2f}%")
    
    print(f"Marge brute prédite pour 2025 : {gross_margin_2025:.2f}%")
    print(f"Marge brute prédite pour 2026 : {gross_margin_2026:.2f}%")
    
    # Création d'un rapport de prédiction
    os.makedirs('data/results/predictions', exist_ok=True)
    report_path = 'data/results/predictions/prediction_report.txt'
    
    with open(report_path, 'w') as f:
        f.write("=================================================================\n")
        f.write("                RAPPORT DE PRÉDICTION FINANCIÈRE                 \n")
        f.write("=================================================================\n\n")
        
        f.write("1. RÉSUMÉ DES PRÉDICTIONS\n")
        f.write("-------------------------\n\n")
        
        f.write("Métriques financières prédites:\n\n")
        f.write(f"{'Année':<10}{'Revenus':<20}{'Bénéfice Net':<20}{'Bénéfice Brut':<20}\n")
        f.write(f"{'-'*10}{'-'*20}{'-'*20}{'-'*20}\n")
        
        # Données historiques
        for i, year in enumerate([2022, 2023, 2024]):
            f.write(f"{year:<10}${revenues[i]:,.0f}".ljust(30))
            f.write(f"${net_income[i]:,.0f}".ljust(20))
            f.write(f"${gross_profit[i]:,.0f}".ljust(20))
            f.write("\n")
        
        # Données prédites
        for i, year in enumerate([2025, 2026]):
            f.write(f"{year:<10}${predicted_revenues[i]:,.0f}".ljust(30))
            f.write(f"${predicted_net_income[i]:,.0f}".ljust(20))
            f.write(f"${predicted_gross_profit[i]:,.0f}".ljust(20))
            f.write("\n")
        
        f.write("\nRatios financiers prédits:\n\n")
        f.write(f"{'Année':<10}{'Marge Nette':<20}{'Marge Brute':<20}\n")
        f.write(f"{'-'*10}{'-'*20}{'-'*20}\n")
        
        # Marges historiques
        net_margins = [(net_income[i] / revenues[i]) * 100 for i in range(len(years))]
        gross_margins = [(gross_profit[i] / revenues[i]) * 100 for i in range(len(years))]
        
        for i, year in enumerate([2022, 2023, 2024]):
            f.write(f"{year:<10}{net_margins[i]:.2f}%".ljust(20))
            f.write(f"{gross_margins[i]:.2f}%".ljust(20))
            f.write("\n")
        
        # Marges prédites
        for i, year in enumerate([2025, 2026]):
            if i == 0:
                f.write(f"{year:<10}{net_margin_2025:.2f}%".ljust(20))
                f.write(f"{gross_margin_2025:.2f}%".ljust(20))
            else:
                f.write(f"{year:<10}{net_margin_2026:.2f}%".ljust(20))
                f.write(f"{gross_margin_2026:.2f}%".ljust(20))
            f.write("\n")
        
        f.write("\n2. ANALYSE DES TENDANCES\n")
        f.write("------------------------\n\n")
        
        f.write("Taux de croissance annuel moyen prédit:\n\n")
        f.write(f"- Revenus: {revenue_growth_rate:.2f}%\n")
        f.write(f"- Bénéfice Net: {net_income_growth_rate:.2f}%\n")
        f.write(f"- Bénéfice Brut: {gross_profit_growth_rate:.2f}%\n\n")
        
        f.write("3. NIVEAU DE CONFIANCE DES PRÉDICTIONS\n")
        f.write("-------------------------------------\n\n")
        
        f.write(f"- Revenus: {revenue_confidence:.2f}%\n")
        f.write(f"- Bénéfice Net: {net_income_confidence:.2f}%\n")
        f.write(f"- Bénéfice Brut: {gross_profit_confidence:.2f}%\n\n")
        
        f.write("4. INTERPRÉTATION DES RÉSULTATS\n")
        f.write("------------------------------\n\n")
        
        # Revenus
        f.write("Revenus:\n")
        if revenue_growth_rate > 10:
            f.write("- Forte croissance prévue des revenus\n")
        elif revenue_growth_rate > 5:
            f.write("- Croissance modérée prévue des revenus\n")
        elif revenue_growth_rate > 0:
            f.write("- Légère croissance prévue des revenus\n")
        elif revenue_growth_rate > -5:
            f.write("- Légère baisse prévue des revenus\n")
        else:
            f.write("- Baisse significative prévue des revenus\n")
        
        f.write(f"- Taux de croissance annuel moyen prévu: {revenue_growth_rate:.2f}%\n\n")
        
        # Bénéfice net
        f.write("Bénéfice net:\n")
        if net_income_growth_rate > 15:
            f.write("- Forte croissance prévue du bénéfice net\n")
        elif net_income_growth_rate > 7:
            f.write("- Croissance modérée prévue du bénéfice net\n")
        elif net_income_growth_rate > 0:
            f.write("- Légère croissance prévue du bénéfice net\n")
        elif net_income_growth_rate > -7:
            f.write("- Légère baisse prévue du bénéfice net\n")
        else:
            f.write("- Baisse significative prévue du bénéfice net\n")
        
        f.write(f"- Taux de croissance annuel moyen prévu: {net_income_growth_rate:.2f}%\n\n")
        
        # Marges
        f.write("Marge nette:\n")
        current_margin = net_margins[-1]
        future_margin = net_margin_2026
        
        if future_margin > current_margin * 1.1:
            f.write("- Amélioration significative prévue de la marge nette\n")
        elif future_margin > current_margin:
            f.write("- Légère amélioration prévue de la marge nette\n")
        elif future_margin > current_margin * 0.9:
            f.write("- Légère détérioration prévue de la marge nette\n")
        else:
            f.write("- Détérioration significative prévue de la marge nette\n")
        
        f.write(f"- Marge nette actuelle (2024): {current_margin:.2f}%\n")
        f.write(f"- Marge nette prévue (2026): {future_margin:.2f}%\n\n")
        
        # Conclusion
        f.write("5. CONCLUSION\n")
        f.write("------------\n\n")
        
        # Évaluer la tendance générale
        positive_trends = 0
        negative_trends = 0
        
        if revenue_growth_rate > 0:
            positive_trends += 1
        else:
            negative_trends += 1
            
        if net_income_growth_rate > 0:
            positive_trends += 1
        else:
            negative_trends += 1
            
        if gross_profit_growth_rate > 0:
            positive_trends += 1
        else:
            negative_trends += 1
        
        if positive_trends > negative_trends:
            f.write("Les prédictions indiquent une tendance globalement positive pour les prochaines années, ")
            f.write("avec une croissance attendue dans la majorité des indicateurs financiers clés. ")
            
            if revenue_confidence > 70:
                f.write("Le niveau de confiance dans ces prédictions est relativement élevé, ")
                f.write("ce qui suggère une bonne fiabilité des projections.\n\n")
            else:
                f.write("Cependant, le niveau de confiance dans ces prédictions est modéré, ")
                f.write("ce qui suggère de prendre ces projections avec une certaine prudence.\n\n")
        else:
            f.write("Les prédictions indiquent des défis potentiels pour les prochaines années, ")
            f.write("avec une tendance à la baisse dans plusieurs indicateurs financiers clés. ")
            
            if revenue_confidence > 70:
                f.write("Le niveau de confiance dans ces prédictions est relativement élevé, ")
                f.write("ce qui suggère une bonne fiabilité des projections.\n\n")
            else:
                f.write("Cependant, le niveau de confiance dans ces prédictions est modéré, ")
                f.write("ce qui suggère de prendre ces projections avec une certaine prudence.\n\n")
        
        f.write("Note: Ces prédictions sont basées sur une analyse de régression linéaire des données historiques ")
        f.write("et ne tiennent pas compte des facteurs externes tels que les changements de marché, ")
        f.write("les innovations technologiques ou les événements macroéconomiques qui pourraient influencer ")
        f.write("significativement les performances futures de l'entreprise.\n")
    
    print(f"Rapport de prédiction détaillé sauvegardé dans {report_path}")
    print("\n✅ Prédictions financières terminées avec succès!")

if __name__ == "__main__":
    main() 