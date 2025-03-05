from flask import Flask, render_template_string, request, jsonify
import json
import os
import socket
from pathlib import Path

app = Flask(__name__)

def find_available_port(start_port=5050, max_attempts=100):
    """Trouve un port disponible en commençant par start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

def load_comparative_data():
    """Charge les données comparatives depuis le fichier JSON"""
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                'data/results/comparative/comparative/comparative_analysis.json')
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return None

def list_json_files(directory):
    """Liste les fichiers JSON dans un répertoire"""
    files = []
    for file in os.listdir(directory):
        if file.endswith('.json'):
            files.append(file)
    return files

def load_json_file(file_path):
    """Charge un fichier JSON"""
    with open(file_path, 'r') as f:
        return json.load(f)

def load_dashboard_html():
    """Charge le contenu HTML du tableau de bord amélioré"""
    try:
        dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'improved_dashboard.html')
        with open(dashboard_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Erreur lors du chargement du tableau de bord: {e}")
        return None

@app.route('/')
def index():
    # Chemin vers le répertoire des données
    data_dir = Path("data/results")
    
    # Vérifier si le répertoire existe
    if not data_dir.exists():
        return "Directory data/results does not exist", 404
    
    # Lister les sous-répertoires
    subdirs = [d.name for d in data_dir.iterdir() if d.is_dir()]
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Analysis Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .container-fluid {
                padding: 0;
            }
            .sidebar {
                background-color: #333;
                color: white;
                padding: 20px;
                min-height: 100vh;
            }
            .content {
                padding: 20px;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            select {
                width: 100%;
                padding: 8px;
                margin-bottom: 15px;
            }
            .btn-primary {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            .btn-primary:hover {
                background-color: #45a049;
                border-color: #45a049;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                color: #777;
            }
            .nav-link {
                color: white;
                margin-bottom: 10px;
                display: block;
            }
            .nav-link:hover {
                color: #4CAF50;
            }
            .nav-link.active {
                color: #4CAF50;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-3 col-lg-2 sidebar">
                    <h2 class="mb-4">Navigation</h2>
                    
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link active" href="/">Accueil</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/dashboard">Tableau de bord</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/explorer">Explorateur de données</a>
                        </li>
                    </ul>
                    
                    <div class="mt-5">
                        <h4>Analyses disponibles</h4>
                        <form id="dataForm">
                            <div class="mb-3">
                                <label for="subdir" class="form-label">Type d'analyse:</label>
                                <select class="form-select" id="subdir" name="subdir">
                                    {% for subdir in subdirs %}
                                    <option value="{{ subdir }}">{{ subdir }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            
                            <div id="fileSelectContainer" style="display: none;" class="mb-3">
                                <label for="file" class="form-label">Fichier:</label>
                                <select class="form-select" id="file" name="file"></select>
                            </div>
                            
                            <button type="button" id="loadSubdirBtn" class="btn btn-primary mb-2">Charger les fichiers</button>
                            <button type="button" id="loadDataBtn" class="btn btn-primary" style="display: none;">Charger les données</button>
                        </form>
                    </div>
                    
                    <div class="footer mt-5">
                        Financial Analysis Dashboard v2.0
                    </div>
                </div>
                
                <div class="col-md-9 col-lg-10 content">
                    <h1>Analyse Financière - Dashboard</h1>
                    <p class="lead">Bienvenue dans l'application d'analyse financière des rapports 10-K</p>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Tableau de bord interactif</h5>
                                    <p class="card-text">Visualisez les données financières clés des entreprises avec des graphiques interactifs.</p>
                                    <a href="/dashboard" class="btn btn-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Explorateur de données</h5>
                                    <p class="card-text">Explorez les données brutes extraites des rapports financiers.</p>
                                    <a href="/explorer" class="btn btn-primary">Accéder</a>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-5">
                        <h2>À propos</h2>
                        <p>Cette application a été développée pour analyser les données financières extraites des rapports 10-K de différentes entreprises.</p>
                        <p>Source des données : Rapports 10-K de Tesla, Apple et Microsoft.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
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
            
            document.getElementById('loadDataBtn').addEventListener('click', function() {
                const subdir = document.getElementById('subdir').value;
                const file = document.getElementById('file').value;
                
                window.location.href = `/data/${subdir}/${file}`;
            });
        </script>
    </body>
    </html>
    """, subdirs=subdirs)

@app.route('/dashboard')
def dashboard():
    # Chargement des données réelles
    data = load_comparative_data()
    
    # Chargement du HTML du tableau de bord
    dashboard_html = load_dashboard_html()
    
    if dashboard_html:
        # Intégration du tableau de bord dans notre template
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Financial Analysis Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }
                .container-fluid {
                    padding: 0;
                }
                .sidebar {
                    background-color: #333;
                    color: white;
                    padding: 20px;
                    min-height: 100vh;
                }
                .content {
                    padding: 20px;
                }
                h1 {
                    color: #333;
                    margin-bottom: 20px;
                }
                .nav-link {
                    color: white;
                    margin-bottom: 10px;
                    display: block;
                }
                .nav-link:hover {
                    color: #4CAF50;
                }
                .nav-link.active {
                    color: #4CAF50;
                    font-weight: bold;
                }
                .footer {
                    margin-top: 20px;
                    text-align: center;
                    color: #777;
                }
                iframe {
                    width: 100%;
                    height: 100vh;
                    border: none;
                }
            </style>
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-3 col-lg-2 sidebar">
                        <h2 class="mb-4">Navigation</h2>
                        
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link" href="/">Accueil</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link active" href="/dashboard">Tableau de bord</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="/explorer">Explorateur de données</a>
                            </li>
                        </ul>
                        
                        <div class="footer mt-5">
                            Financial Analysis Dashboard v2.0
                        </div>
                    </div>
                    
                    <div class="col-md-9 col-lg-10 content p-0">
                        <div id="dashboard-container">
                            {{ dashboard_html|safe }}
                        </div>
                    </div>
                </div>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """, dashboard_html=dashboard_html)
    else:
        return "Erreur lors du chargement du tableau de bord", 500

@app.route('/explorer')
def explorer():
    # Chemin vers le répertoire des données
    data_dir = Path("data/results")
    
    # Vérifier si le répertoire existe
    if not data_dir.exists():
        return "Directory data/results does not exist", 404
    
    # Lister les sous-répertoires
    subdirs = [d.name for d in data_dir.iterdir() if d.is_dir()]
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Analysis Dashboard - Explorer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .container-fluid {
                padding: 0;
            }
            .sidebar {
                background-color: #333;
                color: white;
                padding: 20px;
                min-height: 100vh;
            }
            .content {
                padding: 20px;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            select {
                width: 100%;
                padding: 8px;
                margin-bottom: 15px;
            }
            .btn-primary {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            .btn-primary:hover {
                background-color: #45a049;
                border-color: #45a049;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                color: #777;
            }
            .nav-link {
                color: white;
                margin-bottom: 10px;
                display: block;
            }
            .nav-link:hover {
                color: #4CAF50;
            }
            .nav-link.active {
                color: #4CAF50;
                font-weight: bold;
            }
            pre {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <div class="row">
                <div class="col-md-3 col-lg-2 sidebar">
                    <h2 class="mb-4">Navigation</h2>
                    
                    <ul class="nav flex-column">
                        <li class="nav-item">
                            <a class="nav-link" href="/">Accueil</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="/dashboard">Tableau de bord</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link active" href="/explorer">Explorateur de données</a>
                        </li>
                    </ul>
                    
                    <div class="mt-5">
                        <h4>Explorateur de données</h4>
                        <form id="dataForm">
                            <div class="mb-3">
                                <label for="subdir" class="form-label">Type d'analyse:</label>
                                <select class="form-select" id="subdir" name="subdir">
                                    {% for subdir in subdirs %}
                                    <option value="{{ subdir }}">{{ subdir }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            
                            <div id="fileSelectContainer" style="display: none;" class="mb-3">
                                <label for="file" class="form-label">Fichier:</label>
                                <select class="form-select" id="file" name="file"></select>
                            </div>
                            
                            <button type="button" id="loadSubdirBtn" class="btn btn-primary mb-2">Charger les fichiers</button>
                            <button type="button" id="loadDataBtn" class="btn btn-primary" style="display: none;">Afficher les données</button>
                        </form>
                    </div>
                    
                    <div class="footer mt-5">
                        Financial Analysis Dashboard v2.0
                    </div>
                </div>
                
                <div class="col-md-9 col-lg-10 content">
                    <h1>Explorateur de données</h1>
                    <p class="lead">Explorez les données brutes extraites des rapports financiers</p>
                    
                    <div id="dataContainer" class="mt-4">
                        <p>Sélectionnez un type d'analyse et un fichier pour afficher les données.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
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
            
            document.getElementById('loadDataBtn').addEventListener('click', function() {
                const subdir = document.getElementById('subdir').value;
                const file = document.getElementById('file').value;
                
                fetch(`/data/${subdir}/${file}`)
                    .then(response => response.json())
                    .then(data => {
                        const dataContainer = document.getElementById('dataContainer');
                        
                        // Créer un affichage des données
                        let html = `<h2>Données de ${file}</h2>`;
                        
                        // Afficher les clés principales
                        html += `<h3>Clés principales</h3><ul class="list-group mb-4">`;
                        Object.keys(data).forEach(key => {
                            html += `<li class="list-group-item">${key}</li>`;
                        });
                        html += `</ul>`;
                        
                        // Afficher les données complètes
                        html += `<h3>Données complètes</h3>`;
                        html += `<pre>${JSON.stringify(data, null, 2)}</pre>`;
                        
                        dataContainer.innerHTML = html;
                    });
            });
        </script>
    </body>
    </html>
    """, subdirs=subdirs)

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

if __name__ == '__main__':
    port = find_available_port(5050)
    if port:
        print(f"=== DÉMARRAGE DE L'APPLICATION INTÉGRÉE ===")
        print(f"Application accessible à l'adresse: http://127.0.0.1:{port}")
        print(f"Appuyez sur CTRL+C pour arrêter le serveur")
        print(f"=====================================")
        app.run(debug=True, port=port)
    else:
        print("Impossible de trouver un port disponible. Veuillez libérer des ports ou spécifier un port manuellement.") 