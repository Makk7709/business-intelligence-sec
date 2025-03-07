"""
Module de pont entre l'application principale et les technologies LangChain, ChatGPT et Pinecone.
Ce script est conçu pour être exécuté comme un processus séparé et communiquer via des fichiers.
"""

import os
import sys
import json
import time
import logging
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='ai_bridge.log'
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

# Répertoire pour les fichiers de communication
COMM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'comm')
os.makedirs(COMM_DIR, exist_ok=True)

# Fichiers de communication
QUERY_FILE = os.path.join(COMM_DIR, 'query.json')
RESPONSE_FILE = os.path.join(COMM_DIR, 'response.json')
STATUS_FILE = os.path.join(COMM_DIR, 'status.json')

# Contexte financier pour l'assistant
FINANCIAL_CONTEXT = """
Données financières d'Apple:
- Revenus: 390,036 millions de dollars en 2024, 375,970 millions en 2023, 368,234 millions en 2022
- Marge brute: 43.8% en 2024, 43.2% en 2023, 46.4% en 2022
- Bénéfice net: 97,150 millions de dollars en 2024, 94,320 millions en 2023, 99,803 millions en 2022

Données financières de Microsoft:
- Revenus: 225,340 millions de dollars en 2024, 205,357 millions en 2023, 188,852 millions en 2022
- Marge brute: 70.0% en 2024, 69.0% en 2023, 66.8% en 2022
- Bénéfice net: 72,361 millions de dollars en 2024, 72,361 millions en 2023, 67,430 millions en 2022

Prédictions pour Apple:
- Revenus: environ 405,637 millions de dollars en 2025, 421,863 millions en 2026
- Marge brute: environ 44.1% en 2025, 44.3% en 2026

Prédictions pour Microsoft:
- Revenus: environ 245,621 millions de dollars en 2025, 267,726 millions en 2026
- Marge brute: environ 70.5% en 2025, 71.0% en 2026
"""

def write_status(status, message=""):
    """Écrit le statut du pont IA dans un fichier."""
    with open(STATUS_FILE, 'w') as f:
        json.dump({
            'status': status,
            'message': message,
            'timestamp': time.time()
        }, f)
    logger.info(f"Statut mis à jour: {status} - {message}")

def read_query():
    """Lit une requête depuis le fichier de communication."""
    if not os.path.exists(QUERY_FILE):
        return None
    
    try:
        with open(QUERY_FILE, 'r') as f:
            data = json.load(f)
        
        # Supprimer le fichier après lecture
        os.remove(QUERY_FILE)
        
        return data
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de la requête: {str(e)}")
        return None

def write_response(response):
    """Écrit une réponse dans le fichier de communication."""
    with open(RESPONSE_FILE, 'w') as f:
        json.dump(response, f)
    logger.info(f"Réponse écrite: {response['response'][:50]}...")

def process_with_openai(query):
    """Traite une requête avec l'API OpenAI."""
    import openai
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return {
            "response": "La clé API OpenAI n'est pas configurée.",
            "query": query,
            "source": "error"
        }
    
    openai.api_key = openai_api_key
    
    try:
        logger.info(f"Envoi de la requête à OpenAI: {query}")
        
        # Appel à l'API OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Tu es un assistant financier spécialisé dans l'analyse des données d'Apple et Microsoft. Réponds de manière concise et précise aux questions sur les données financières. Voici les données dont tu disposes: {FINANCIAL_CONTEXT}"},
                {"role": "user", "content": query}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Extraire la réponse
        ai_response = response.choices[0].message.content
        logger.info(f"Réponse d'OpenAI reçue: {ai_response[:50]}...")
        
        return {
            "response": ai_response,
            "query": query,
            "source": "openai"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
        return {
            "response": f"Erreur lors de l'appel à l'API OpenAI: {str(e)}",
            "query": query,
            "source": "error"
        }

def process_with_langchain(query):
    """Traite une requête avec LangChain."""
    try:
        from langchain.chat_models import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return {
                "response": "La clé API OpenAI n'est pas configurée pour LangChain.",
                "query": query,
                "source": "error"
            }
        
        logger.info(f"Envoi de la requête à LangChain: {query}")
        
        # Initialiser le modèle de langage
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7, openai_api_key=openai_api_key)
        
        # Créer le template de prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Tu es un assistant financier spécialisé dans l'analyse des données d'Apple et Microsoft. "
                      "Réponds de manière concise et précise aux questions sur les données financières. "
                      "Voici les données dont tu disposes:\n\n{context}"),
            ("human", "{query}")
        ])
        
        # Créer la chaîne
        chain = prompt_template | llm
        
        # Exécuter la chaîne
        response = chain.invoke({
            "context": FINANCIAL_CONTEXT,
            "query": query
        })
        
        # Extraire la réponse
        ai_response = response.content
        logger.info(f"Réponse de LangChain reçue: {ai_response[:50]}...")
        
        return {
            "response": ai_response,
            "query": query,
            "source": "langchain"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à LangChain: {str(e)}")
        return {
            "response": f"Erreur lors de l'appel à LangChain: {str(e)}",
            "query": query,
            "source": "error"
        }

def process_with_pinecone(query):
    """Traite une requête avec Pinecone."""
    try:
        import pinecone
        from langchain.embeddings import OpenAIEmbeddings
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_env = os.getenv("PINECONE_ENV", "gcp-starter")
        
        if not openai_api_key:
            return {
                "response": "La clé API OpenAI n'est pas configurée pour Pinecone.",
                "query": query,
                "source": "error"
            }
        
        if not pinecone_api_key:
            return {
                "response": "La clé API Pinecone n'est pas configurée.",
                "query": query,
                "source": "error"
            }
        
        logger.info(f"Envoi de la requête à Pinecone: {query}")
        
        # Initialiser Pinecone
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_env)
        
        # Vérifier si l'index existe
        index_name = "financial-docs"
        if index_name not in pinecone.list_indexes():
            # L'index n'existe pas, utiliser une réponse prédéfinie
            return {
                "response": "L'index Pinecone n'existe pas. Veuillez d'abord créer l'index et y stocker des documents.",
                "query": query,
                "source": "error"
            }
        
        # Initialiser les embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        
        # Créer l'embedding de la requête
        query_embedding = embeddings.embed_query(query)
        
        # Interroger Pinecone
        index = pinecone.Index(index_name)
        results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        
        # Extraire les résultats
        contexts = [match['metadata']['text'] for match in results['matches']]
        
        # Utiliser OpenAI pour générer une réponse basée sur les contextes
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Tu es un assistant financier spécialisé dans l'analyse des données d'Apple et Microsoft. Réponds de manière concise et précise aux questions sur les données financières. Voici les données dont tu disposes: {FINANCIAL_CONTEXT}\n\nVoici également des contextes pertinents extraits des documents: {contexts}"},
                {"role": "user", "content": query}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        # Extraire la réponse
        ai_response = response.choices[0].message.content
        logger.info(f"Réponse de Pinecone reçue: {ai_response[:50]}...")
        
        return {
            "response": ai_response,
            "query": query,
            "source": "pinecone"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à Pinecone: {str(e)}")
        return {
            "response": f"Erreur lors de l'appel à Pinecone: {str(e)}",
            "query": query,
            "source": "error"
        }

def process_query(query_data):
    """Traite une requête en fonction du type demandé."""
    query = query_data.get('query', '')
    query_type = query_data.get('type', 'openai')
    
    if query_type == 'openai':
        return process_with_openai(query)
    elif query_type == 'langchain':
        return process_with_langchain(query)
    elif query_type == 'pinecone':
        return process_with_pinecone(query)
    else:
        return {
            "response": f"Type de requête non reconnu: {query_type}",
            "query": query,
            "source": "error"
        }

def main_loop():
    """Boucle principale du pont IA."""
    write_status('ready', 'Le pont IA est prêt à traiter des requêtes.')
    
    while True:
        # Vérifier s'il y a une nouvelle requête
        query_data = read_query()
        if query_data:
            # Mettre à jour le statut
            write_status('processing', f"Traitement de la requête: {query_data.get('query', '')[:50]}...")
            
            # Traiter la requête
            response = process_query(query_data)
            
            # Écrire la réponse
            write_response(response)
            
            # Mettre à jour le statut
            write_status('ready', 'Le pont IA est prêt à traiter des requêtes.')
        
        # Attendre un peu avant de vérifier à nouveau
        time.sleep(1)

if __name__ == "__main__":
    try:
        logger.info("Démarrage du pont IA...")
        main_loop()
    except KeyboardInterrupt:
        logger.info("Arrêt du pont IA...")
        write_status('stopped', 'Le pont IA a été arrêté.')
    except Exception as e:
        logger.error(f"Erreur dans le pont IA: {str(e)}")
        write_status('error', f"Erreur dans le pont IA: {str(e)}")
        sys.exit(1) 