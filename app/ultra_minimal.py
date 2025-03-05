from flask import Flask, jsonify, render_template_string, request
import os
import json

app = Flask(__name__)

# Fonction pour lister les fichiers JSON dans un répertoire
def list_json_files(directory):
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith('.json')]

# Fonction pour charger un fichier JSON
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

# Route pour la page d'accueil
@app.route("/")
def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial Analysis Dashboard</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f7fa;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #2c3e50;
                color: white;
                padding: 20px 0;
                text-align: center;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0;
            }
            .card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                text-decoration: none;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .btn:hover {
                background-color: #2980b9;
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
            
            /* New styles for the three-section layout */
            .app-container {
                display: flex;
                min-height: 100vh;
            }
            
            /* Left sidebar */
            .sidebar {
                width: 250px;
                background-color: #34495e;
                color: white;
                padding-top: 20px;
                flex-shrink: 0;
            }
            
            .sidebar-header {
                padding: 0 20px 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                text-align: center;
            }
            
            .sidebar-menu {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .sidebar-menu li {
                margin-bottom: 5px;
            }
            
            .sidebar-menu a {
                display: block;
                color: white;
                text-decoration: none;
                padding: 12px 20px;
                transition: background-color 0.3s;
            }
            
            .sidebar-menu a:hover, .sidebar-menu a.active {
                background-color: #2c3e50;
                border-left: 4px solid #3498db;
            }
            
            .sidebar-menu i {
                margin-right: 10px;
            }
            
            /* Main content area */
            .main-content {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
            }
            
            /* Top indicators section */
            .indicators {
                background-color: white;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            
            .indicators-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
            }
            
            .indicator-card {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .indicator-card h3 {
                margin-top: 0;
                color: #7f8c8d;
                font-size: 14px;
                text-transform: uppercase;
            }
            
            .indicator-value {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }
            
            .indicator-trend {
                font-size: 14px;
            }
            
            .trend-up {
                color: #2ecc71;
            }
            
            .trend-down {
                color: #e74c3c;
            }
            
            /* Central content area */
            .content-area {
                flex-grow: 1;
                padding: 0 20px 20px;
                overflow-y: auto;
            }
            
            .content-card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            
            /* Company selector */
            .company-selector {
                margin-bottom: 20px;
            }
            
            select, button {
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            
            button {
                background-color: #3498db;
                color: white;
                border: none;
                cursor: pointer;
            }
            
            button:hover {
                background-color: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Left Sidebar Navigation -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <h2>Financial Analysis</h2>
                </div>
                <ul class="sidebar-menu">
                    <li><a href="/" class="active">Dashboard</a></li>
                    <li><a href="/metrics">Reports</a></li>
                    <li><a href="/ratios">Comparisons</a></li>
                    <li><a href="/companies">Companies</a></li>
                    <li><a href="/settings">Settings</a></li>
                </ul>
            </div>
            
            <!-- Main Content Area -->
            <div class="main-content">
                <header>
                    <h1>Financial Analysis Dashboard</h1>
                </header>
                
                <!-- Top Indicators Section -->
                <div class="indicators">
                    <div class="indicators-grid">
                        <div class="indicator-card">
                            <h3>Revenue</h3>
                            <div class="indicator-value">$245.8M</div>
                            <div class="indicator-trend trend-up">+5.2% YoY</div>
                        </div>
                        <div class="indicator-card">
                            <h3>Gross Margin</h3>
                            <div class="indicator-value">42.3%</div>
                            <div class="indicator-trend trend-up">+1.8% YoY</div>
                        </div>
                        <div class="indicator-card">
                            <h3>Net Profit</h3>
                            <div class="indicator-value">$36.4M</div>
                            <div class="indicator-trend trend-up">+3.7% YoY</div>
                        </div>
                        <div class="indicator-card">
                            <h3>P/E Ratio</h3>
                            <div class="indicator-value">18.5</div>
                            <div class="indicator-trend trend-down">-2.1 YoY</div>
                        </div>
                    </div>
                </div>
                
                <!-- Central Content Area -->
                <div class="content-area">
                    <div class="content-card">
                        <h2>Welcome to Financial Analysis Dashboard</h2>
                        <p>This dashboard provides financial analysis for various companies based on their 10-K reports.</p>
                        
                        <h3>Available Features:</h3>
                        <ul>
                            <li>View financial metrics for companies</li>
                            <li>Analyze financial ratios</li>
                            <li>Compare companies performance</li>
                            <li>View predictions for future performance</li>
                        </ul>
                    </div>
                    
                    <div class="content-card">
                        <h2>Quick Access</h2>
                        <a href="/metrics" class="btn">Financial Metrics</a>
                        <a href="/ratios" class="btn">Financial Ratios</a>
                        <a href="/companies" class="btn">Companies</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

# Route pour l'API de statut
@app.route("/api/status")
def status():
    return jsonify({"status": "ok", "message": "API is working"})

# Route pour afficher les métriques financières
@app.route("/metrics")
def metrics():
    # Répertoire des résultats
    results_dir = "data/results"
    companies = []
    
    # Vérifier si le répertoire existe
    if os.path.exists(results_dir):
        # Lister les sous-répertoires (entreprises)
        companies = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
    
    html = """
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
                color: #333;
            }
            .container {
                width: 90%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #2c3e50;
                color: white;
                padding: 20px 0;
                text-align: center;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0;
            }
            .card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                text-decoration: none;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .btn:hover {
                background-color: #2980b9;
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
            .nav {
                background-color: #34495e;
                padding: 10px 0;
            }
            .nav a {
                color: white;
                text-decoration: none;
                padding: 10px 15px;
                margin-right: 5px;
            }
            .nav a:hover {
                background-color: #2c3e50;
            }
            .company-selector {
                margin-bottom: 20px;
            }
            select, button {
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #2980b9;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Financial Analysis Dashboard</h1>
        </header>
        <div class="nav">
            <div class="container">
                <a href="/">Home</a>
                <a href="/metrics">Financial Metrics</a>
                <a href="/ratios">Financial Ratios</a>
                <a href="/companies">Companies</a>
                <a href="/api/status">API Status</a>
            </div>
        </div>
        <div class="container">
            <div class="card">
                <h2>Financial Metrics</h2>
                
                <div class="company-selector">
                    <label for="company">Select a company:</label>
                    <select id="company">
                        <option value="">-- Select --</option>
                        {% for company in companies %}
                        <option value="{{ company }}">{{ company }}</option>
                        {% endfor %}
                    </select>
                    <button onclick="loadMetrics()">View Metrics</button>
                </div>
                
                <div id="metrics-container">
                    <p>Select a company to view its financial metrics.</p>
                </div>
            </div>
        </div>
        
        <script>
        function loadMetrics() {
            const company = document.getElementById('company').value;
            if (!company) {
                alert('Please select a company');
                return;
            }
            
            fetch(`/api/metrics/${company}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('metrics-container').innerHTML = `<p>Error: ${data.error}</p>`;
                        return;
                    }
                    
                    let html = '<h3>Financial Metrics for ' + company + '</h3>';
                    html += '<table>';
                    html += '<tr><th>Metric</th>';
                    
                    // Années comme en-têtes de colonnes
                    const years = Object.keys(data.revenue || {});
                    years.forEach(year => {
                        html += `<th>${year}</th>`;
                    });
                    html += '</tr>';
                    
                    // Lignes pour chaque métrique
                    const metrics = ['revenue', 'net_income', 'gross_profit', 'total_assets', 'total_liabilities'];
                    metrics.forEach(metric => {
                        if (data[metric]) {
                            html += `<tr><td>${metric.replace('_', ' ')}</td>`;
                            years.forEach(year => {
                                const value = data[metric][year] || 'N/A';
                                html += `<td>${value}</td>`;
                            });
                            html += '</tr>';
                        }
                    });
                    
                    html += '</table>';
                    document.getElementById('metrics-container').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('metrics-container').innerHTML = `<p>Error: ${error.message}</p>`;
                });
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, companies=companies)

# Route pour afficher les ratios financiers
@app.route("/ratios")
def ratios():
    # Répertoire des résultats
    results_dir = "data/results"
    companies = []
    
    # Vérifier si le répertoire existe
    if os.path.exists(results_dir):
        # Lister les sous-répertoires (entreprises)
        companies = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
    
    html = """
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
                color: #333;
            }
            .container {
                width: 90%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #2c3e50;
                color: white;
                padding: 20px 0;
                text-align: center;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0;
            }
            .card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                text-decoration: none;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .btn:hover {
                background-color: #2980b9;
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
            .nav {
                background-color: #34495e;
                padding: 10px 0;
            }
            .nav a {
                color: white;
                text-decoration: none;
                padding: 10px 15px;
                margin-right: 5px;
            }
            .nav a:hover {
                background-color: #2c3e50;
            }
            .company-selector {
                margin-bottom: 20px;
            }
            select, button {
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #2980b9;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Financial Analysis Dashboard</h1>
        </header>
        <div class="nav">
            <div class="container">
                <a href="/">Home</a>
                <a href="/metrics">Financial Metrics</a>
                <a href="/ratios">Financial Ratios</a>
                <a href="/companies">Companies</a>
                <a href="/api/status">API Status</a>
            </div>
        </div>
        <div class="container">
            <div class="card">
                <h2>Financial Ratios</h2>
                
                <div class="company-selector">
                    <label for="company">Select a company:</label>
                    <select id="company">
                        <option value="">-- Select --</option>
                        {% for company in companies %}
                        <option value="{{ company }}">{{ company }}</option>
                        {% endfor %}
                    </select>
                    <button onclick="loadRatios()">View Ratios</button>
                </div>
                
                <div id="ratios-container">
                    <p>Select a company to view its financial ratios.</p>
                </div>
            </div>
        </div>
        
        <script>
        function loadRatios() {
            const company = document.getElementById('company').value;
            if (!company) {
                alert('Please select a company');
                return;
            }
            
            fetch(`/api/ratios/${company}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('ratios-container').innerHTML = `<p>Error: ${data.error}</p>`;
                        return;
                    }
                    
                    let html = '<h3>Financial Ratios for ' + company + '</h3>';
                    html += '<table>';
                    html += '<tr><th>Ratio</th>';
                    
                    // Années comme en-têtes de colonnes
                    const years = Object.keys(data.net_margin || {});
                    years.forEach(year => {
                        html += `<th>${year}</th>`;
                    });
                    html += '</tr>';
                    
                    // Lignes pour chaque ratio
                    const ratios = ['net_margin', 'gross_margin', 'debt_to_assets'];
                    ratios.forEach(ratio => {
                        if (data[ratio]) {
                            html += `<tr><td>${ratio.replace('_', ' ')}</td>`;
                            years.forEach(year => {
                                const value = data[ratio][year] || 'N/A';
                                html += `<td>${value}%</td>`;
                            });
                            html += '</tr>';
                        }
                    });
                    
                    html += '</table>';
                    document.getElementById('ratios-container').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('ratios-container').innerHTML = `<p>Error: ${error.message}</p>`;
                });
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, companies=companies)

# Route pour la liste des entreprises
@app.route("/companies")
def companies():
    # Répertoire des résultats
    results_dir = "data/results"
    companies = []
    
    # Vérifier si le répertoire existe
    if os.path.exists(results_dir):
        # Lister les sous-répertoires (entreprises)
        companies = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
    
    html = """
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
                color: #333;
            }
            .container {
                width: 90%;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            header {
                background-color: #2c3e50;
                color: white;
                padding: 20px 0;
                text-align: center;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0;
            }
            .card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            .btn {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 10px 15px;
                border-radius: 5px;
                text-decoration: none;
                margin-right: 10px;
                margin-bottom: 10px;
            }
            .btn:hover {
                background-color: #2980b9;
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
            .nav {
                background-color: #34495e;
                padding: 10px 0;
            }
            .nav a {
                color: white;
                text-decoration: none;
                padding: 10px 15px;
                margin-right: 5px;
            }
            .nav a:hover {
                background-color: #2c3e50;
            }
            .company-selector {
                margin-bottom: 20px;
            }
            select, button {
                padding: 8px 12px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #2980b9;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin-bottom: 20px;
                padding: 15px;
                background-color: #f9f9f9;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Financial Analysis Dashboard</h1>
        </header>
        <div class="nav">
            <div class="container">
                <a href="/">Home</a>
                <a href="/metrics">Financial Metrics</a>
                <a href="/ratios">Financial Ratios</a>
                <a href="/companies">Companies</a>
                <a href="/api/status">API Status</a>
            </div>
        </div>
        <div class="container">
            <div class="card">
                <h2>Companies</h2>
                
                {% if companies %}
                <ul>
                    {% for company in companies %}
                    <li>
                        <h3>{{ company }}</h3>
                        <a href="/metrics?company={{ company }}" class="btn">View Metrics</a>
                        <a href="/ratios?company={{ company }}" class="btn">View Ratios</a>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <p>No company data available.</p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, companies=companies)

# API pour récupérer les métriques d'une entreprise
@app.route("/api/metrics/<company>")
def api_metrics(company):
    metrics_file = f"data/results/{company}/metrics.json"
    if not os.path.exists(metrics_file):
        return jsonify({"error": f"No metrics found for {company}"})
    
    return jsonify(load_json_file(metrics_file))

# API pour récupérer les ratios d'une entreprise
@app.route("/api/ratios/<company>")
def api_ratios(company):
    ratios_file = f"data/results/{company}/ratios.json"
    if not os.path.exists(ratios_file):
        return jsonify({"error": f"No ratios found for {company}"})
    
    return jsonify(load_json_file(ratios_file))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
