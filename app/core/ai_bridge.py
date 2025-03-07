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

# Ajouter le répertoire parent au chemin d'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importer la configuration
from app.config import (
    OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX_NAME,
    OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS,
    QUERY_FILE, RESPONSE_FILE, STATUS_FILE,
    AI_BRIDGE_LOG_FILE, FINANCIAL_CONTEXT
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=AI_BRIDGE_LOG_FILE
)
logger = logging.getLogger(__name__)

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
    
    if not OPENAI_API_KEY:
        return {
            "response": "La clé API OpenAI n'est pas configurée.",
            "query": query,
            "source": "error"
        }
    
    openai.api_key = OPENAI_API_KEY
    
    try:
        logger.info(f"Envoi de la requête à OpenAI: {query}")
        
        # Appel à l'API OpenAI
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"Tu es un assistant financier spécialisé dans l'analyse des données d'Apple et Microsoft. Réponds de manière concise et précise aux questions sur les données financières. Voici les données dont tu disposes: {FINANCIAL_CONTEXT}"},
                {"role": "user", "content": query}
            ],
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
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
        
        if not OPENAI_API_KEY:
            return {
                "response": "La clé API OpenAI n'est pas configurée pour LangChain.",
                "query": query,
                "source": "error"
            }
        
        logger.info(f"Envoi de la requête à LangChain: {query}")
        
        # Initialiser le modèle de langage
        llm = ChatOpenAI(model_name=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE, openai_api_key=OPENAI_API_KEY)
        
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
        
        if not OPENAI_API_KEY:
            return {
                "response": "La clé API OpenAI n'est pas configurée pour Pinecone.",
                "query": query,
                "source": "error"
            }
        
        if not PINECONE_API_KEY:
            return {
                "response": "La clé API Pinecone n'est pas configurée.",
                "query": query,
                "source": "error"
            }
        
        logger.info(f"Envoi de la requête à Pinecone: {query}")
        
        # Initialiser Pinecone
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        
        # Vérifier si l'index existe
        if PINECONE_INDEX_NAME not in pinecone.list_indexes():
            # L'index n'existe pas, utiliser une réponse prédéfinie
            return {
                "response": "L'index Pinecone n'existe pas. Veuillez d'abord créer l'index et y stocker des documents.",
                "query": query,
                "source": "error"
            }
        
        # Initialiser les embeddings
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Créer l'embedding de la requête
        query_embedding = embeddings.embed_query(query)
        
        # Interroger Pinecone
        index = pinecone.Index(PINECONE_INDEX_NAME)
        results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        
        # Extraire les résultats
        contexts = [match['metadata']['text'] for match in results['matches']]
        
        # Utiliser OpenAI pour générer une réponse basée sur les contextes
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"Tu es un assistant financier spécialisé dans l'analyse des données d'Apple et Microsoft. Réponds de manière concise et précise aux questions sur les données financières. Voici les données dont tu disposes: {FINANCIAL_CONTEXT}\n\nVoici également des contextes pertinents extraits des documents: {contexts}"},
                {"role": "user", "content": query}
            ],
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
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