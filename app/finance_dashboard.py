from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend non-interactif
import matplotlib.pyplot as plt
from pathlib import Path
import io
import base64

# Ajouter le répertoire src au chemin Python pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules d'analyse financière
try:
    from src.financial_analyzer import FinancialAnalyzer
    from src.langchain_processor import LangchainProcessor
except ImportError as e:
    print(f"Erreur d'importation: {e}")

app = Flask(__name__)

# Fonction pour lister les fichiers JSON dans un répertoire
def list_json_files(directory):
    files = []
    try:
        for file in os.listdir(directory):
            if file.endswith('.json'):
                files.append(file)
    except Exception as e:
        print(f"Erreur lors de la lecture du répertoire {directory}: {e}")
    return files

# Fonction pour charger un fichier JSON
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return {}

# Fonction pour générer un graphique et le convertir en image base64
def generate_plot(data, title, x_label, y_label):
    plt.figure(figsize=(10, 6))
    
    # Si les données sont un dictionnaire, convertir en DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame(list(data.items()), columns=['Year', 'Value'])
        plt.bar(df['Year'], df['Value'])
    else:
        # Sinon, supposer que c'est une liste de tuples (année, valeur)
        years, values = zip(*data)
        plt.bar(years, values)
    
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Sauvegarder le graphique dans un buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Convertir l'image en base64 pour l'afficher dans HTML
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return img_base64

# Route principale
@app.route('/')
def index():
    # Chemin vers le répertoire des données
    data_dir = Path("data/results")
    
    # Vérifier si le répertoire existe
    if not data_dir.exists():
        return "Directory data/results does not exist", 404
    
    # Lister les sous-répertoires
    subdirs = [d.name for d in data_dir.iterdir() if d.is_dir()]
    
    # Lister les entreprises disponibles
    companies = []
    extracted_dir = Path("data")
    if extracted_dir.exists():
        for file in os.listdir(extracted_dir):
            if file.endswith('_10k_extracted.txt'):
                companies.append(file.split('_')[0])
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Analysis Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .container {
                display: flex;
                min-height: 100vh;
            }
            .sidebar {
                width: 250px;
                background-color: #333;
                color: white;
                padding: 20px;
            }
            .content {
                flex-grow: 1;
                padding: 20px;
                overflow-y: auto;
            }
            h1, h2, h3 {
                color: #333;
            }
            select, input {
                width: 100%;
                padding: 8px;
                margin-bottom: 15px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                cursor: pointer;
                margin-bottom: 10px;
                width: 100%;
            }
            button:hover {
                background-color: #45a049;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                color: #777;
            }
            .card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .tabs {
                display: flex;
                margin-bottom: 20px;
            }
            .tab {
                padding: 10px 20px;
                background-color: #ddd;
                cursor: pointer;
                margin-right: 5px;
                border-radius: 5px 5px 0 0;
            }
            .tab.active {
                background-color: white;
                border-bottom: 2px solid #4CAF50;
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .chart-container {
                margin: 20px 0;
                text-align: center;
            }
            pre {
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="sidebar">
                <h2>Navigation</h2>
                
                <div class="card">
                    <h3>View Existing Analysis</h3>
                    <form id="viewForm">
                        <label for="subdir">Analysis Type:</label>
                        <select id="subdir" name="subdir">
                            {% for subdir in subdirs %}
                            <option value="{{ subdir }}">{{ subdir }}</option>
                            {% endfor %}
                        </select>
                        
                        <div id="fileSelectContainer" style="display: none;">
                            <label for="file">Select File:</label>
                            <select id="file" name="file"></select>
                        </div>
                        
                        <button type="button" id="loadSubdirBtn">Load Files</button>
                        <button type="button" id="loadDataBtn" style="display: none;">View Analysis</button>
                    </form>
                </div>
                
                <div class="card">
                    <h3>Run New Analysis</h3>
                    <form id="analysisForm">
                        <label for="company">Company:</label>
                        <select id="company" name="company">
                            {% for company in companies %}
                            <option value="{{ company }}">{{ company }}</option>
                            {% endfor %}
                        </select>
                        
                        <label for="analysisType">Analysis Type:</label>
                        <select id="analysisType" name="analysisType">
                            <option value="traditional">Traditional Analysis</option>
                            <option value="langchain">LangChain Analysis</option>
                            <option value="enhanced">Enhanced Analysis</option>
                        </select>
                        
                        <button type="button" id="runAnalysisBtn">Run Analysis</button>
                    </form>
                </div>
                
                <div class="footer">
                    Financial Analysis Dashboard v1.0
                </div>
            </div>
            
            <div class="content">
                <h1>Financial Analysis Dashboard</h1>
                
                <div class="tabs">
                    <div class="tab active" data-tab="overview">Overview</div>
                    <div class="tab" data-tab="metrics">Financial Metrics</div>
                    <div class="tab" data-tab="ratios">Financial Ratios</div>
                    <div class="tab" data-tab="charts">Charts</div>
                    <div class="tab" data-tab="report">Report</div>
                    <div class="tab" data-tab="raw">Raw Data</div>
                </div>
                
                <div id="overview" class="tab-content active">
                    <div class="card">
                        <h2>Welcome to the Financial Analysis Dashboard</h2>
                        <p>This dashboard allows you to view and analyze financial data extracted from 10-K reports.</p>
                        <p>You can:</p>
                        <ul>
                            <li>View existing analyses</li>
                            <li>Run new analyses on available company data</li>
                            <li>Compare financial metrics and ratios</li>
                            <li>View visualizations of financial data</li>
                        </ul>
                        <p>To get started, use the navigation panel on the left to select an existing analysis or run a new one.</p>
                    </div>
                </div>
                
                <div id="metrics" class="tab-content">
                    <div class="card">
                        <h2>Financial Metrics</h2>
                        <div id="metricsContainer">
                            <p>Select an analysis to view financial metrics.</p>
                        </div>
                    </div>
                </div>
                
                <div id="ratios" class="tab-content">
                    <div class="card">
                        <h2>Financial Ratios</h2>
                        <div id="ratiosContainer">
                            <p>Select an analysis to view financial ratios.</p>
                        </div>
                    </div>
                </div>
                
                <div id="charts" class="tab-content">
                    <div class="card">
                        <h2>Financial Charts</h2>
                        <div id="chartsContainer">
                            <p>Select an analysis to view financial charts.</p>
                        </div>
                    </div>
                </div>
                
                <div id="report" class="tab-content">
                    <div class="card">
                        <h2>Analysis Report</h2>
                        <div id="reportContainer">
                            <p>Select an analysis to view the report.</p>
                        </div>
                    </div>
                </div>
                
                <div id="raw" class="tab-content">
                    <div class="card">
                        <h2>Raw Data</h2>
                        <div id="rawContainer">
                            <p>Select an analysis to view raw data.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Gestion des onglets
            document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    // Désactiver tous les onglets
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                    
                    // Activer l'onglet cliqué
                    this.classList.add('active');
                    document.getElementById(this.dataset.tab).classList.add('active');
                });
            });
            
            // Charger les fichiers d'un sous-répertoire
            document.getElementById('loadSubdirBtn').addEventListener('click', function() {
                const subdir = document.getElementById('subdir').value;
                
                fetch(`/files/${subdir}`)
                    .then(response => response.json())
                    .then(data => {
                        const fileSelect = document.getElementById('file');
                        fileSelect.innerHTML = '';
                        
                        data.files.forEach(file => {
                            const option = document.createElement('option');
                            option.value = file;
                            option.textContent = file;
                            fileSelect.appendChild(option);
                        });
                        
                        document.getElementById('fileSelectContainer').style.display = 'block';
                        document.getElementById('loadDataBtn').style.display = 'block';
                    });
            });
            
            // Charger les données d'un fichier
            document.getElementById('loadDataBtn').addEventListener('click', function() {
                const subdir = document.getElementById('subdir').value;
                const file = document.getElementById('file').value;
                
                fetch(`/data/${subdir}/${file}`)
                    .then(response => response.json())
                    .then(data => {
                        // Afficher les métriques financières
                        displayMetrics(data);
                        
                        // Afficher les ratios financiers
                        displayRatios(data);
                        
                        // Afficher les graphiques
                        displayCharts(data, file);
                        
                        // Afficher le rapport
                        displayReport(subdir, file);
                        
                        // Afficher les données brutes
                        displayRawData(data);
                        
                        // Passer à l'onglet des métriques
                        document.querySelector('.tab[data-tab="metrics"]').click();
                    });
            });
            
            // Exécuter une nouvelle analyse
            document.getElementById('runAnalysisBtn').addEventListener('click', function() {
                const company = document.getElementById('company').value;
                const analysisType = document.getElementById('analysisType').value;
                
                // Afficher un message de chargement
                document.getElementById('overview').innerHTML = '<div class="card"><h2>Running Analysis</h2><p>Please wait while the analysis is being performed...</p></div>';
                
                fetch(`/run-analysis/${company}/${analysisType}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Recharger la page pour afficher la nouvelle analyse
                            window.location.reload();
                        } else {
                            document.getElementById('overview').innerHTML = `<div class="card"><h2>Error</h2><p>${data.error}</p></div>`;
                        }
                    });
            });
            
            // Fonction pour afficher les métriques financières
            function displayMetrics(data) {
                let html = '<table><tr><th>Year</th><th>Revenue</th><th>Net Income</th><th>Gross Profit</th><th>Total Assets</th><th>Total Liabilities</th></tr>';
                
                // Vérifier si les métriques sont présentes
                if (data.metrics) {
                    const years = Object.keys(data.metrics).sort();
                    
                    years.forEach(year => {
                        const metrics = data.metrics[year];
                        html += `<tr>
                            <td>${year}</td>
                            <td>${formatCurrency(metrics.revenue || metrics.total_revenue || 0)}</td>
                            <td>${formatCurrency(metrics.net_income || 0)}</td>
                            <td>${formatCurrency(metrics.gross_profit || 0)}</td>
                            <td>${formatCurrency(metrics.total_assets || 0)}</td>
                            <td>${formatCurrency(metrics.total_liabilities || 0)}</td>
                        </tr>`;
                    });
                }
                
                html += '</table>';
                document.getElementById('metricsContainer').innerHTML = html;
            }
            
            // Fonction pour afficher les ratios financiers
            function displayRatios(data) {
                let html = '<table><tr><th>Year</th><th>ROA</th><th>ROE</th><th>Net Margin</th><th>Gross Margin</th><th>Debt/Assets</th></tr>';
                
                // Vérifier si les ratios sont présents
                if (data.ratios) {
                    const years = Object.keys(data.ratios).sort();
                    
                    years.forEach(year => {
                        const ratios = data.ratios[year];
                        html += `<tr>
                            <td>${year}</td>
                            <td>${formatPercentage(ratios.roa || 0)}</td>
                            <td>${formatPercentage(ratios.roe || 0)}</td>
                            <td>${formatPercentage(ratios.net_margin || 0)}</td>
                            <td>${formatPercentage(ratios.gross_margin || 0)}</td>
                            <td>${formatPercentage(ratios.debt_to_assets || 0)}</td>
                        </tr>`;
                    });
                }
                
                html += '</table>';
                document.getElementById('ratiosContainer').innerHTML = html;
            }
            
            // Fonction pour afficher les graphiques
            function displayCharts(data, filename) {
                let html = '';
                
                // Obtenir le nom de l'entreprise à partir du nom de fichier
                const company = filename.split('_')[0];
                
                // Ajouter des graphiques pour les métriques principales
                html += `<div class="chart-container">
                    <h3>Revenue Over Time</h3>
                    <img src="/chart/${company}/revenue" alt="Revenue Chart" style="max-width: 100%;">
                </div>`;
                
                html += `<div class="chart-container">
                    <h3>Net Income Over Time</h3>
                    <img src="/chart/${company}/net_income" alt="Net Income Chart" style="max-width: 100%;">
                </div>`;
                
                html += `<div class="chart-container">
                    <h3>Gross Profit Over Time</h3>
                    <img src="/chart/${company}/gross_profit" alt="Gross Profit Chart" style="max-width: 100%;">
                </div>`;
                
                // Ajouter des graphiques pour les ratios principaux
                html += `<div class="chart-container">
                    <h3>Net Margin Over Time</h3>
                    <img src="/chart/${company}/net_margin" alt="Net Margin Chart" style="max-width: 100%;">
                </div>`;
                
                html += `<div class="chart-container">
                    <h3>Gross Margin Over Time</h3>
                    <img src="/chart/${company}/gross_margin" alt="Gross Margin Chart" style="max-width: 100%;">
                </div>`;
                
                document.getElementById('chartsContainer').innerHTML = html;
            }
            
            // Fonction pour afficher le rapport
            function displayReport(subdir, filename) {
                // Obtenir le nom de l'entreprise à partir du nom de fichier
                const company = filename.split('_')[0];
                
                fetch(`/report/${subdir}/${company}`)
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('reportContainer').innerHTML = `<pre>${data}</pre>`;
                    });
            }
            
            // Fonction pour afficher les données brutes
            function displayRawData(data) {
                document.getElementById('rawContainer').innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            }
            
            // Fonction pour formater les valeurs monétaires
            function formatCurrency(value) {
                return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
            }
            
            // Fonction pour formater les pourcentages
            function formatPercentage(value) {
                return new Intl.NumberFormat('en-US', { style: 'percent', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
            }
        </script>
    </body>
    </html>
    """, subdirs=subdirs, companies=companies)

# Route pour obtenir la liste des fichiers dans un sous-répertoire
@app.route('/files/<subdir>')
def get_files(subdir):
    data_dir = Path("data/results") / subdir
    
    if not data_dir.exists():
        return jsonify({"error": "Directory not found"}), 404
    
    files = list_json_files(data_dir)
    return jsonify({"files": files})

# Route pour obtenir les données d'un fichier
@app.route('/data/<subdir>/<file>')
def get_data(subdir, file):
    file_path = Path("data/results") / subdir / file
    
    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404
    
    try:
        data = load_json_file(file_path)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour obtenir le rapport d'analyse
@app.route('/report/<subdir>/<company>')
def get_report(subdir, company):
    report_path = Path("data/results") / subdir / f"{company}_report.txt"
    
    if not report_path.exists():
        report_path = Path("data/results") / subdir / f"{company}_{subdir}_report.txt"
        if not report_path.exists():
            return "Report not found", 404
    
    try:
        with open(report_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading report: {e}", 500

# Route pour générer un graphique
@app.route('/chart/<company>/<metric>')
def get_chart(company, metric):
    # Chercher le fichier d'analyse pour cette entreprise
    data_dir = Path("data/results")
    data = None
    
    # Parcourir les sous-répertoires pour trouver les données de l'entreprise
    for subdir in os.listdir(data_dir):
        subdir_path = data_dir / subdir
        if subdir_path.is_dir():
            for file in os.listdir(subdir_path):
                if file.startswith(company) and file.endswith('.json'):
                    data = load_json_file(subdir_path / file)
                    break
            if data:
                break
    
    if not data:
        return "Data not found", 404
    
    # Extraire les données pour le graphique
    chart_data = []
    
    if metric in ['revenue', 'net_income', 'gross_profit', 'total_assets', 'total_liabilities']:
        # Métriques financières
        if 'metrics' in data:
            for year, metrics in data['metrics'].items():
                # Gérer les différentes façons de nommer les métriques
                if metric == 'revenue' and 'total_revenue' in metrics:
                    chart_data.append((year, metrics['total_revenue']))
                elif metric in metrics:
                    chart_data.append((year, metrics[metric]))
    elif metric in ['roa', 'roe', 'net_margin', 'gross_margin', 'debt_to_assets']:
        # Ratios financiers
        if 'ratios' in data:
            for year, ratios in data['ratios'].items():
                if metric in ratios:
                    chart_data.append((year, ratios[metric]))
    
    # Trier les données par année
    chart_data.sort(key=lambda x: x[0])
    
    if not chart_data:
        return "No data available for this metric", 404
    
    # Générer le graphique
    title = f"{metric.replace('_', ' ').title()} for {company.upper()}"
    img_base64 = generate_plot(chart_data, title, "Year", metric.replace('_', ' ').title())
    
    # Créer une réponse avec l'image
    return f'<img src="data:image/png;base64,{img_base64}" />'

# Route pour exécuter une nouvelle analyse
@app.route('/run-analysis/<company>/<analysis_type>')
def run_analysis(company, analysis_type):
    try:
        # Vérifier si le fichier 10-K extrait existe
        extracted_file = Path(f"data/{company}_10k_extracted.txt")
        if not extracted_file.exists():
            return jsonify({"success": False, "error": f"Extracted 10-K file for {company} not found"}), 404
        
        # Créer le répertoire de résultats si nécessaire
        result_dir = Path(f"data/results/{analysis_type}")
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # Exécuter l'analyse en fonction du type
        if analysis_type == "traditional":
            # Analyse traditionnelle
            analyzer = FinancialAnalyzer()
            metrics = analyzer.extract_financial_metrics(extracted_file)
            ratios = analyzer.calculate_financial_ratios(metrics)
            
            # Sauvegarder les résultats
            results = {
                "metrics": metrics,
                "ratios": ratios
            }
            
            with open(result_dir / f"{company}_analysis.json", 'w') as f:
                json.dump(results, f, indent=2)
            
            # Générer un rapport
            report = analyzer.generate_investment_report(company, metrics, ratios)
            
            with open(result_dir / f"{company}_report.txt", 'w') as f:
                f.write(report)
                
        elif analysis_type in ["langchain", "enhanced"]:
            # Analyse avec LangChain
            processor = LangchainProcessor()
            
            if analysis_type == "langchain":
                # Analyse LangChain standard
                metrics = processor.extract_financial_metrics(extracted_file)
                ratios = processor.calculate_financial_ratios(metrics)
                
                # Sauvegarder les résultats
                results = {
                    "metrics": metrics,
                    "ratios": ratios
                }
                
                with open(result_dir / f"{company}_analysis.json", 'w') as f:
                    json.dump(results, f, indent=2)
                
                # Générer un rapport
                report = processor.generate_investment_report(company, metrics, ratios)
                
                with open(result_dir / f"{company}_report.txt", 'w') as f:
                    f.write(report)
                    
            else:  # enhanced
                # Analyse LangChain améliorée
                processor.run_enhanced_analysis(company, extracted_file, result_dir)
        
        return jsonify({"success": True})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Fonction pour rendre un template string (puisque nous n'avons pas de dossier templates)
def render_template_string(template_string, **context):
    from jinja2 import Template
    template = Template(template_string)
    return template.render(**context)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 