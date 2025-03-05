from flask import Flask, render_template, request, jsonify
import json
import os
from pathlib import Path

app = Flask(__name__)

# Fonction pour lister les fichiers JSON dans un répertoire
def list_json_files(directory):
    files = []
    for file in os.listdir(directory):
        if file.endswith('.json'):
            files.append(file)
    return files

# Fonction pour charger un fichier JSON
def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

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
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial Analysis Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
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
            }
            h1 {
                color: #333;
            }
            select {
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
            }
            button:hover {
                background-color: #45a049;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                color: #777;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="sidebar">
                <h2>Navigation</h2>
                <form id="dataForm">
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
                    <button type="button" id="loadDataBtn" style="display: none;">Load Data</button>
                </form>
                <div class="footer">
                    Financial Analysis Dashboard v1.0
                </div>
            </div>
            
            <div class="content">
                <h1>Financial Analysis Dashboard</h1>
                <div id="dataContainer">
                    <p>Select an analysis type and file to view data.</p>
                </div>
            </div>
        </div>
        
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
                        let html = `<h2>Data from ${file}</h2>`;
                        
                        // Afficher les clés principales
                        html += `<h3>Main Keys</h3><ul>`;
                        Object.keys(data).forEach(key => {
                            html += `<li>${key}</li>`;
                        });
                        html += `</ul>`;
                        
                        // Afficher les données complètes
                        html += `<h3>Complete Data</h3>`;
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

# Fonction pour rendre un template string (puisque nous n'avons pas de dossier templates)
def render_template_string(template_string, **context):
    from jinja2 import Template
    template = Template(template_string)
    return template.render(**context)

if __name__ == '__main__':
    app.run(debug=True, port=5000) 