from flask import Flask, render_template, request, jsonify
import os
import json
import sys

# Ajouter le répertoire parent au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.interactive_charts import create_dashboard_charts, create_comparative_chart

app = Flask(__name__)

def list_json_files(directory):
    """Liste tous les fichiers JSON dans un répertoire donné."""
    json_files = []
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith('.json'):
                json_files.append(os.path.join(directory, file))
    return json_files

def load_json_file(file_path):
    """Charge un fichier JSON et retourne son contenu."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de {file_path}: {e}")
        return {}

@app.route('/')
def index():
    """Page d'accueil avec sélecteur d'entreprise et graphiques interactifs."""
    # Récupérer l'entreprise sélectionnée (par défaut: tesla)
    company = request.args.get('company', 'tesla').lower()
    
    # Générer tous les graphiques pour cette entreprise
    charts = create_dashboard_charts(company)
    
    # Rendre le template avec les graphiques
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tableau de bord financier interactif</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f8f9fa;
                color: #212529;
            }
            .navbar {
                background-color: #343a40;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .chart-container {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                padding: 20px;
                margin-bottom: 20px;
            }
            .company-selector {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                padding: 20px;
                margin-bottom: 20px;
            }
            h2 {
                font-size: 1.5rem;
                margin-bottom: 15px;
                color: #343a40;
            }
            .btn-primary {
                background-color: #007bff;
                border-color: #007bff;
            }
            .btn-primary:hover {
                background-color: #0069d9;
                border-color: #0062cc;
            }
            .metric-selector {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark">
            <div class="container">
                <a class="navbar-brand" href="/">Tableau de bord financier interactif</a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-md-12">
                    <div class="company-selector">
                        <h2>Sélectionner une entreprise</h2>
                        <form id="companyForm" class="d-flex">
                            <select id="companySelect" name="company" class="form-select me-2">
                                <option value="tesla" {% if company == 'tesla' %}selected{% endif %}>Tesla</option>
                                <option value="apple" {% if company == 'apple' %}selected{% endif %}>Apple</option>
                                <option value="microsoft" {% if company == 'microsoft' %}selected{% endif %}>Microsoft</option>
                            </select>
                            <button type="submit" class="btn btn-primary">Mettre à jour</button>
                        </form>
                        
                        <div class="metric-selector">
                            <h2>Comparaison personnalisée</h2>
                            <div class="d-flex">
                                <select id="metricSelect" class="form-select me-2">
                                    <option value="revenue">Revenus</option>
                                    <option value="net_income">Revenu net</option>
                                    <option value="gross_profit">Bénéfice brut</option>
                                    <option value="net_margin">Marge nette</option>
                                    <option value="gross_margin">Marge brute</option>
                                    <option value="debt_ratio">Ratio d'endettement</option>
                                </select>
                                <button id="compareBtn" class="btn btn-primary">Comparer</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-container">
                        <h2>Évolution des revenus</h2>
                        {{ revenue_chart|safe }}
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <h2>Marges bénéficiaires</h2>
                        {{ margins_chart|safe }}
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-12">
                    <div class="chart-container">
                        <h2>Ratios financiers</h2>
                        {{ ratios_chart|safe }}
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="chart-container">
                        <h2>Comparaison des revenus</h2>
                        {{ comparative_revenue|safe }}
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-container">
                        <h2>Comparaison des marges nettes</h2>
                        {{ comparative_margin|safe }}
                    </div>
                </div>
            </div>
            
            <div class="row mt-3">
                <div class="col-md-12">
                    <div id="customComparisonContainer" class="chart-container" style="display: none;">
                        <h2 id="customComparisonTitle">Comparaison personnalisée</h2>
                        <div id="customComparisonChart"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            $(document).ready(function() {
                // Gestionnaire pour le bouton de comparaison personnalisée
                $('#compareBtn').click(function() {
                    const metric = $('#metricSelect').val();
                    const metricName = $('#metricSelect option:selected').text();
                    
                    // Afficher un message de chargement
                    $('#customComparisonContainer').show();
                    $('#customComparisonTitle').text('Chargement de la comparaison...');
                    $('#customComparisonChart').html('<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>');
                    
                    // Appeler l'API pour obtenir le graphique personnalisé
                    $.get('/api/compare/' + metric, function(data) {
                        $('#customComparisonTitle').text('Comparaison de ' + metricName);
                        $('#customComparisonChart').html(data.chart);
                    });
                });
                
                // Mettre à jour l'URL avec l'entreprise sélectionnée
                $('#companySelect').change(function() {
                    $('#companyForm').submit();
                });
            });
        </script>
    </body>
    </html>
    """, **charts)

@app.route('/api/compare/<metric>')
def compare_metric(metric):
    """API pour générer un graphique comparatif personnalisé."""
    companies = ["tesla", "apple", "microsoft"]
    chart_html = create_comparative_chart(metric, companies)
    return jsonify({"chart": chart_html})

if __name__ == '__main__':
    app.run(debug=True, port=5001) 