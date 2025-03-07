"""
Routes pour l'interface utilisateur de l'application.
"""

from flask import Blueprint, send_file, render_template, redirect, url_for
import os
import sys

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.config import STATIC_HTML_PATH

# Créer le blueprint pour les routes UI
ui_bp = Blueprint('ui', __name__)

@ui_bp.route('/')
def index():
    """Route principale pour servir le dashboard."""
    return send_file(STATIC_HTML_PATH)

@ui_bp.route('/dashboard')
def dashboard():
    """Route alternative pour servir le dashboard."""
    return redirect(url_for('ui.index')) 