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
    AI_BRIDGE_LOG_FILE, FINANCIAL_CONTEXT, API_TIMEOUT,
    LANGCHAIN_TRACING_V2, LANGCHAIN_ENDPOINT, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT
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
    """
    Traite une requête avec l'API OpenAI.
    
    Args:
        query: La requête à traiter
        
    Returns:
        Dict: La réponse formatée
    """
    import openai
    from openai import OpenAI
    import requests.exceptions
    
    if not OPENAI_API_KEY:
        logger.error("La clé API OpenAI n'est pas configurée.")
        return {
            "response": "La clé API OpenAI n'est pas configurée. Veuillez configurer la clé API dans le fichier .env.",
            "query": query,
            "source": "error"
        }
    
    try:
        logger.info(f"Envoi de la requête à OpenAI: {query}")
        
        # Initialiser le client OpenAI avec timeout
        client = OpenAI(api_key=OPENAI_API_KEY, timeout=API_TIMEOUT)
        
        # Appel à l'API OpenAI
        response = client.chat.completions.create(
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
        
    except openai.RateLimitError:
        logger.error("Limite de taux OpenAI dépassée.")
        return {
            "response": "Désolé, nous avons atteint la limite de requêtes à l'API OpenAI. Veuillez réessayer dans quelques instants.",
            "query": query,
            "source": "error"
        }
    except openai.AuthenticationError:
        logger.error("Erreur d'authentification OpenAI.")
        return {
            "response": "Erreur d'authentification avec l'API OpenAI. Veuillez vérifier votre clé API.",
            "query": query,
            "source": "error"
        }
    except openai.APIError as e:
        logger.error(f"Erreur API OpenAI: {str(e)}")
        return {
            "response": f"Erreur de l'API OpenAI: {str(e)}. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel à l'API OpenAI.")
        return {
            "response": "La requête à l'API OpenAI a pris trop de temps. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête lors de l'appel à l'API OpenAI: {str(e)}")
        return {
            "response": f"Erreur de connexion à l'API OpenAI: {str(e)}. Veuillez vérifier votre connexion internet.",
            "query": query,
            "source": "error"
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
        return {
            "response": f"Une erreur s'est produite lors de l'appel à l'API OpenAI: {str(e)}. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }

def process_with_langchain(query):
    """
    Traite une requête avec LangChain.
    
    Args:
        query: La requête à traiter
        
    Returns:
        Dict: La réponse formatée
    """
    try:
        from langchain.chat_models import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain.callbacks.tracers import LangChainTracer
        from langchain.callbacks.manager import CallbackManager
        import requests.exceptions
        
        if not OPENAI_API_KEY:
            logger.error("La clé API OpenAI n'est pas configurée pour LangChain.")
            return {
                "response": "La clé API OpenAI n'est pas configurée pour LangChain. Veuillez configurer la clé API dans le fichier .env.",
                "query": query,
                "source": "error"
            }
        
        logger.info(f"Envoi de la requête à LangChain: {query}")
        
        # Configurer le traçage LangChain si activé
        callback_manager = None
        if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
            try:
                tracer = LangChainTracer(
                    project_name=LANGCHAIN_PROJECT,
                    endpoint=LANGCHAIN_ENDPOINT,
                    api_key=LANGCHAIN_API_KEY
                )
                callback_manager = CallbackManager([tracer])
                logger.info(f"Traçage LangChain activé pour le projet {LANGCHAIN_PROJECT}")
            except Exception as e:
                logger.warning(f"Impossible d'initialiser le traçage LangChain: {str(e)}")
        
        # Initialiser le modèle de langage avec timeout
        llm = ChatOpenAI(
            model_name=OPENAI_MODEL, 
            temperature=OPENAI_TEMPERATURE, 
            openai_api_key=OPENAI_API_KEY,
            request_timeout=API_TIMEOUT,
            callback_manager=callback_manager if callback_manager else None
        )
        
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
        
    except ImportError as e:
        logger.error(f"Erreur d'importation LangChain: {str(e)}")
        return {
            "response": f"LangChain n'est pas correctement installé: {str(e)}. Veuillez installer les dépendances requises.",
            "query": query,
            "source": "error"
        }
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel à LangChain.")
        return {
            "response": "La requête à LangChain a pris trop de temps. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête lors de l'appel à LangChain: {str(e)}")
        return {
            "response": f"Erreur de connexion à LangChain: {str(e)}. Veuillez vérifier votre connexion internet.",
            "query": query,
            "source": "error"
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à LangChain: {str(e)}")
        return {
            "response": f"Une erreur s'est produite lors de l'appel à LangChain: {str(e)}. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }

def process_with_pinecone(query):
    """
    Traite une requête avec Pinecone.
    
    Args:
        query: La requête à traiter
        
    Returns:
        Dict: La réponse formatée
    """
    try:
        import pinecone
        from langchain.embeddings import OpenAIEmbeddings
        from openai import OpenAI
        import requests.exceptions
        
        if not OPENAI_API_KEY:
            logger.error("La clé API OpenAI n'est pas configurée pour Pinecone.")
            return {
                "response": "La clé API OpenAI n'est pas configurée pour Pinecone. Veuillez configurer la clé API dans le fichier .env.",
                "query": query,
                "source": "error"
            }
        
        if not PINECONE_API_KEY:
            logger.error("La clé API Pinecone n'est pas configurée.")
            return {
                "response": "La clé API Pinecone n'est pas configurée. Veuillez configurer la clé API dans le fichier .env.",
                "query": query,
                "source": "error"
            }
        
        logger.info(f"Envoi de la requête à Pinecone: {query}")
        
        # Initialiser Pinecone
        try:
            pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Pinecone: {str(e)}")
            return {
                "response": f"Erreur lors de l'initialisation de Pinecone: {str(e)}. Veuillez vérifier vos paramètres de configuration.",
                "query": query,
                "source": "error"
            }
        
        # Vérifier si l'index existe
        try:
            indexes = pinecone.list_indexes()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des index Pinecone: {str(e)}")
            return {
                "response": f"Erreur lors de la récupération des index Pinecone: {str(e)}. Veuillez vérifier votre connexion internet.",
                "query": query,
                "source": "error"
            }
        
        if PINECONE_INDEX_NAME not in indexes:
            logger.error(f"L'index Pinecone {PINECONE_INDEX_NAME} n'existe pas.")
            return {
                "response": f"L'index Pinecone '{PINECONE_INDEX_NAME}' n'existe pas. Veuillez d'abord créer l'index et y stocker des documents.",
                "query": query,
                "source": "error"
            }
        
        # Initialiser les embeddings
        try:
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des embeddings: {str(e)}")
            return {
                "response": f"Erreur lors de l'initialisation des embeddings: {str(e)}. Veuillez vérifier votre clé API OpenAI.",
                "query": query,
                "source": "error"
            }
        
        # Créer l'embedding de la requête
        try:
            query_embedding = embeddings.embed_query(query)
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'embedding de la requête: {str(e)}")
            return {
                "response": f"Erreur lors de la création de l'embedding de la requête: {str(e)}. Veuillez réessayer plus tard.",
                "query": query,
                "source": "error"
            }
        
        # Interroger Pinecone
        try:
            index = pinecone.Index(PINECONE_INDEX_NAME)
            results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        except Exception as e:
            logger.error(f"Erreur lors de l'interrogation de Pinecone: {str(e)}")
            return {
                "response": f"Erreur lors de l'interrogation de Pinecone: {str(e)}. Veuillez réessayer plus tard.",
                "query": query,
                "source": "error"
            }
        
        # Extraire les résultats
        if not results.get('matches'):
            logger.warning("Aucun résultat trouvé dans Pinecone.")
            return {
                "response": "Aucune information pertinente n'a été trouvée dans la base de connaissances. Veuillez reformuler votre question ou consulter d'autres sources.",
                "query": query,
                "source": "pinecone"
            }
        
        contexts = [match.get('metadata', {}).get('text', '') for match in results['matches'] if match.get('metadata')]
        if not contexts or all(not context for context in contexts):
            logger.warning("Aucun contexte trouvé dans les résultats Pinecone.")
            return {
                "response": "Les documents trouvés ne contiennent pas d'informations exploitables. Veuillez reformuler votre question ou consulter d'autres sources.",
                "query": query,
                "source": "pinecone"
            }
        
        # Utiliser OpenAI pour générer une réponse basée sur les contextes
        try:
            client = OpenAI(api_key=OPENAI_API_KEY, timeout=API_TIMEOUT)
            
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
            logger.error(f"Erreur lors de la génération de la réponse avec OpenAI: {str(e)}")
            return {
                "response": f"Erreur lors de la génération de la réponse: {str(e)}. Veuillez réessayer plus tard.",
                "query": query,
                "source": "error"
            }
        
    except ImportError as e:
        logger.error(f"Erreur d'importation Pinecone: {str(e)}")
        return {
            "response": f"Pinecone n'est pas correctement installé: {str(e)}. Veuillez installer les dépendances requises.",
            "query": query,
            "source": "error"
        }
    except requests.exceptions.Timeout:
        logger.error("Timeout lors de l'appel à Pinecone.")
        return {
            "response": "La requête à Pinecone a pris trop de temps. Veuillez réessayer plus tard.",
            "query": query,
            "source": "error"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de requête lors de l'appel à Pinecone: {str(e)}")
        return {
            "response": f"Erreur de connexion à Pinecone: {str(e)}. Veuillez vérifier votre connexion internet.",
            "query": query,
            "source": "error"
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à Pinecone: {str(e)}")
        return {
            "response": f"Une erreur s'est produite lors de l'appel à Pinecone: {str(e)}. Veuillez réessayer plus tard.",
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