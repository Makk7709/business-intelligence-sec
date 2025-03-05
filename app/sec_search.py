import requests
from bs4 import BeautifulSoup
import json
import os
from flask import Blueprint, render_template_string, request, jsonify

# Créer un Blueprint Flask pour la fonctionnalité SEC
sec_bp = Blueprint('sec', __name__)

def search_sec_filings(ticker, filing_type="10-K"):
    """
    Recherche les dépôts SEC pour un ticker spécifique.
    
    Args:
        ticker (str): Le symbole boursier de l'entreprise (ex: TSLA)
        filing_type (str): Le type de dépôt à rechercher (ex: 10-K, 10-Q)
        
    Returns:
        list: Liste des dépôts trouvés avec leurs métadonnées
    """
    # URL de base de l'API EDGAR pour rechercher les rapports
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={ticker}&type={filing_type}&action=getcompany"
    
    # Ajouter un User-Agent comme recommandé par la SEC
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Envoyer une requête à l'API
        response = requests.get(url, headers=headers)
        
        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le HTML avec BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Trouver tous les éléments de la table des résultats
            results = []
            
            # Trouver la table des résultats
            table = soup.find('table', class_='tableFile2')
            
            if table:
                # Parcourir les lignes de la table (ignorer l'en-tête)
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        # Extraire les informations pertinentes
                        filing_type = cells[0].text.strip()
                        filing_date = cells[3].text.strip()
                        
                        # Trouver le lien vers le document
                        filing_link = None
                        if cells[1].find('a'):
                            relative_link = cells[1].find('a')['href']
                            filing_link = f"https://www.sec.gov{relative_link}"
                        
                        # Ajouter les informations au résultat
                        results.append({
                            'type': filing_type,
                            'date': filing_date,
                            'link': filing_link
                        })
            
            return results
        else:
            return [{'error': f"Erreur HTTP {response.status_code}"}]
    
    except Exception as e:
        return [{'error': f"Erreur lors de la récupération des données: {str(e)}"}]

def get_filing_content(url):
    """
    Récupère le contenu d'un dépôt SEC à partir de son URL.
    
    Args:
        url (str): L'URL du dépôt SEC
        
    Returns:
        dict: Les informations extraites du dépôt
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Envoyer une requête à l'URL
        response = requests.get(url, headers=headers)
        
        # Vérifier si la requête est réussie
        if response.status_code == 200:
            # Analyser le HTML avec BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Trouver le lien vers le document HTML
            html_link = None
            for link in soup.find_all('a'):
                if link.text and 'html' in link.text.lower():
                    relative_link = link['href']
                    html_link = f"https://www.sec.gov{relative_link}"
                    break
            
            if html_link:
                # Récupérer le document HTML
                doc_response = requests.get(html_link, headers=headers)
                if doc_response.status_code == 200:
                    return {
                        'url': html_link,
                        'content': doc_response.text
                    }
            
            return {'url': url, 'content': response.text}
        else:
            return {'error': f"Erreur HTTP {response.status_code}"}
    
    except Exception as e:
        return {'error': f"Erreur lors de la récupération du document: {str(e)}"}

@sec_bp.route('/search', methods=['GET', 'POST'])
def search():
    """
    Route pour la recherche de dépôts SEC.
    """
    results = []
    ticker = ""
    filing_type = "10-K"
    
    if request.method == 'POST':
        ticker = request.form.get('ticker', '').upper()
        filing_type = request.form.get('filing_type', '10-K')
        
        if ticker:
            results = search_sec_filings(ticker, filing_type)
    
    # Rendre le template avec les résultats
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recherche SEC</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>Recherche de rapports SEC</h1>
            
            <form method="post" class="mb-4">
                <div class="row g-3 align-items-center">
                    <div class="col-auto">
                        <label for="ticker" class="col-form-label">Ticker:</label>
                    </div>
                    <div class="col-auto">
                        <input type="text" id="ticker" name="ticker" class="form-control" value="{{ ticker }}" required>
                    </div>
                    <div class="col-auto">
                        <label for="filing_type" class="col-form-label">Type:</label>
                    </div>
                    <div class="col-auto">
                        <select id="filing_type" name="filing_type" class="form-select">
                            <option value="10-K" {% if filing_type == '10-K' %}selected{% endif %}>10-K (Rapport annuel)</option>
                            <option value="10-Q" {% if filing_type == '10-Q' %}selected{% endif %}>10-Q (Rapport trimestriel)</option>
                            <option value="8-K" {% if filing_type == '8-K' %}selected{% endif %}>8-K (Événement important)</option>
                        </select>
                    </div>
                    <div class="col-auto">
                        <button type="submit" class="btn btn-primary">Rechercher</button>
                    </div>
                </div>
            </form>
            
            {% if results %}
                <h2>Résultats pour {{ ticker }}</h2>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for result in results %}
                                <tr>
                                    {% if result.get('error') %}
                                        <td colspan="3" class="text-danger">{{ result.error }}</td>
                                    {% else %}
                                        <td>{{ result.type }}</td>
                                        <td>{{ result.date }}</td>
                                        <td>
                                            {% if result.link %}
                                                <a href="{{ result.link }}" target="_blank" class="btn btn-sm btn-outline-primary">Voir sur SEC.gov</a>
                                                <a href="/sec/view?url={{ result.link|urlencode }}" class="btn btn-sm btn-outline-secondary">Voir dans l'application</a>
                                            {% else %}
                                                <span class="text-muted">Lien non disponible</span>
                                            {% endif %}
                                        </td>
                                    {% endif %}
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            {% elif ticker %}
                <div class="alert alert-warning">Aucun résultat trouvé pour {{ ticker }}.</div>
            {% endif %}
            
            <div class="mt-4">
                <a href="/" class="btn btn-secondary">Retour au tableau de bord</a>
            </div>
        </div>
    </body>
    </html>
    """, ticker=ticker, filing_type=filing_type, results=results)

@sec_bp.route('/view')
def view_filing():
    """
    Route pour afficher le contenu d'un dépôt SEC.
    """
    url = request.args.get('url', '')
    
    if not url:
        return "URL non spécifiée", 400
    
    filing = get_filing_content(url)
    
    if 'error' in filing:
        return f"Erreur: {filing['error']}", 500
    
    # Rendre le template avec le contenu du dépôt
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Visualisation du rapport SEC</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .filing-frame {
                width: 100%;
                height: 800px;
                border: 1px solid #ddd;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid mt-4">
            <h1>Visualisation du rapport SEC</h1>
            
            <div class="mb-3">
                <a href="/sec/search" class="btn btn-secondary">Retour à la recherche</a>
                <a href="{{ filing.url }}" target="_blank" class="btn btn-primary">Ouvrir sur SEC.gov</a>
            </div>
            
            <div class="filing-content">
                <iframe class="filing-frame" srcdoc="{{ filing.content|safe }}"></iframe>
            </div>
        </div>
    </body>
    </html>
    """, filing=filing) 