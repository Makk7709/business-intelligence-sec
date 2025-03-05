from flask import Flask, render_template_string, request, redirect, url_for
import requests
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)

def search_sec_filings(ticker, filing_type="10-K"):
    """
    Recherche les dépôts SEC pour un ticker et un type de dépôt donnés.
    
    Args:
        ticker (str): Le symbole boursier de l'entreprise.
        filing_type (str): Le type de dépôt à rechercher (par défaut: "10-K").
        
    Returns:
        list: Une liste de résultats contenant des informations sur les dépôts trouvés.
    """
    try:
        # URL de base pour la recherche SEC
        base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        
        # Paramètres de la requête
        params = {
            "action": "getcompany",
            "CIK": ticker,
            "type": filing_type,
            "owner": "exclude",
            "count": "10"
        }
        
        # En-têtes pour simuler un navigateur
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Effectuer la requête
        response = requests.get(base_url, params=params, headers=headers)
        
        # Vérifier si la requête a réussi
        if response.status_code != 200:
            return {"error": f"Erreur lors de la requête: {response.status_code}"}
        
        # Parser le HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver les résultats
        results = []
        for row in soup.select(".tableFile2 tr"):
            cells = row.find_all("td")
            if len(cells) >= 4:
                filing_date = cells[3].text.strip()
                filing_link = cells[1].find("a")
                if filing_link:
                    filing_url = "https://www.sec.gov" + filing_link["href"]
                    filing_description = cells[1].text.strip()
                    results.append({
                        "date": filing_date,
                        "description": filing_description,
                        "url": filing_url
                    })
        
        return results
    
    except Exception as e:
        return {"error": f"Erreur lors de la recherche: {str(e)}"}

def get_filing_content(url):
    """
    Récupère le contenu d'un dépôt SEC à partir de son URL.
    
    Args:
        url (str): L'URL du dépôt SEC.
        
    Returns:
        str: Le contenu HTML du dépôt.
    """
    try:
        # En-têtes pour simuler un navigateur
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Effectuer la requête
        response = requests.get(url, headers=headers)
        
        # Vérifier si la requête a réussi
        if response.status_code != 200:
            return f"<p>Erreur lors de la récupération du contenu: {response.status_code}</p>"
        
        # Parser le HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trouver le lien vers le document HTML
        html_link = None
        for link in soup.find_all("a"):
            if link.text and "html" in link.text.lower():
                html_link = link.get("href")
                break
        
        if html_link:
            # Construire l'URL complète
            if not html_link.startswith("http"):
                html_link = "https://www.sec.gov" + html_link
            
            # Récupérer le contenu du document HTML
            doc_response = requests.get(html_link, headers=headers)
            if doc_response.status_code == 200:
                return doc_response.text
        
        return "<p>Contenu non disponible au format HTML.</p>"
    
    except Exception as e:
        return f"<p>Erreur lors de la récupération du contenu: {str(e)}</p>"

@app.route('/', methods=['GET', 'POST'])
def search():
    """
    Route pour la recherche de dépôts SEC.
    """
    results = []
    error = None
    ticker = ""
    filing_type = "10-K"
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        ticker = request.form.get('ticker', '').strip().upper()
        filing_type = request.form.get('filing_type', '10-K')
        
        # Vérifier si le ticker est valide
        if not ticker:
            error = "Veuillez entrer un symbole boursier."
        else:
            # Effectuer la recherche
            results = search_sec_filings(ticker, filing_type)
            
            # Vérifier s'il y a une erreur
            if isinstance(results, dict) and 'error' in results:
                error = results['error']
                results = []
    
    # Créer le contenu HTML
    content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recherche SEC</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                padding: 20px;
            }
            .container {
                max-width: 1200px;
            }
            .result-item {
                margin-bottom: 15px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">Recherche de Rapports SEC</h1>
            
            <div class="card mb-4">
                <div class="card-body">
                    <form method="post" action="/">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label for="ticker" class="form-label">Symbole boursier</label>
                                <input type="text" class="form-control" id="ticker" name="ticker" placeholder="ex: AAPL" value="{{ ticker }}" required>
                            </div>
                            <div class="col-md-6">
                                <label for="filing_type" class="form-label">Type de rapport</label>
                                <select class="form-select" id="filing_type" name="filing_type">
                                    <option value="10-K" {{ 'selected' if filing_type == '10-K' else '' }}>10-K (Rapport annuel)</option>
                                    <option value="10-Q" {{ 'selected' if filing_type == '10-Q' else '' }}>10-Q (Rapport trimestriel)</option>
                                    <option value="8-K" {{ 'selected' if filing_type == '8-K' else '' }}>8-K (Événement important)</option>
                                    <option value="DEF 14A" {{ 'selected' if filing_type == 'DEF 14A' else '' }}>DEF 14A (Proxy Statement)</option>
                                </select>
                            </div>
                        </div>
                        <div class="mt-3">
                            <button type="submit" class="btn btn-primary">Rechercher</button>
                        </div>
                    </form>
                </div>
            </div>
            
            {% if error %}
            <div class="alert alert-danger" role="alert">
                {{ error }}
            </div>
            {% endif %}
            
            {% if results %}
            <h2 class="mb-3">Résultats pour {{ ticker }} ({{ filing_type }})</h2>
            
            <div class="list-group">
                {% for result in results %}
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">{{ result.description }}</h5>
                        <small>{{ result.date }}</small>
                    </div>
                    <p class="mb-1">
                        <a href="{{ result.url }}" target="_blank" class="btn btn-sm btn-outline-primary">Voir sur le site SEC</a>
                        <a href="/view?url={{ result.url }}" class="btn btn-sm btn-outline-secondary">Voir dans l'application</a>
                    </p>
                </div>
                {% endfor %}
            </div>
            {% elif request.method == 'POST' and not error %}
            <div class="alert alert-info" role="alert">
                Aucun résultat trouvé pour {{ ticker }} ({{ filing_type }}).
            </div>
            {% endif %}
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Remplacer les variables dans le template
    return render_template_string(
        content,
        ticker=ticker,
        filing_type=filing_type,
        results=results,
        error=error
    )

@app.route('/view')
def view_filing():
    """
    Route pour afficher le contenu d'un dépôt SEC.
    """
    # Récupérer l'URL du dépôt
    url = request.args.get('url')
    
    if not url:
        return redirect('/')
    
    # Récupérer le contenu du dépôt
    content = get_filing_content(url)
    
    # Créer le contenu HTML
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Contenu du rapport SEC</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {
                padding: 20px;
            }
            .container {
                max-width: 1200px;
            }
            .filing-content {
                margin-top: 20px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1>Contenu du rapport SEC</h1>
                <a href="/" class="btn btn-primary">Retour à la recherche</a>
            </div>
            
            <div class="filing-content">
                {{ content|safe }}
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    # Remplacer les variables dans le template
    return render_template_string(html, content=content)

if __name__ == '__main__':
    # Vérifier si le port est déjà utilisé
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    # Essayer différents ports
    port = 5004
    while is_port_in_use(port) and port < 5010:
        port += 1
    
    print(f"Démarrage de l'application SEC sur le port {port}")
    app.run(debug=True, port=port) 