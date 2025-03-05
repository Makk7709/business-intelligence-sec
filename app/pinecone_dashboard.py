from flask import Flask, render_template, request, jsonify
import os
import socket
import json

# Initialisation de l'application Flask
app = Flask(__name__)

# Fonction pour trouver un port disponible
def find_available_port(start_port=5050, max_attempts=100):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return start_port  # Retourne le port de départ si aucun port n'est disponible

# Route principale
@app.route('/')
def index():
    return render_template('pinecone_dashboard.html')

# Point d'entrée de l'application
if __name__ == '__main__':
    port = find_available_port(5050)
    print(f"=== DÉMARRAGE DE L'APPLICATION PINECONE ===")
    print(f"Application accessible à l'adresse: http://127.0.0.1:{port}")
    print("Appuyez sur CTRL+C pour arrêter le serveur")
    print("=====================================")
    app.run(debug=True, port=port) 