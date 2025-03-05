import os
import sys
import numpy as np
import pinecone
from dotenv import load_dotenv
import time
import json
import uuid

# Charger les variables d'environnement
load_dotenv()

# Configuration de Pinecone
PINECONE_API_KEY = "pcsk_2ufD2c_AoNVgZYP28gYsABGSdkHM2kFyviRzfTqogKVw8ac8F2g6ZyY1GwW8sYvrdJQCZM"
PINECONE_ENVIRONMENT = "gcp-starter"
INDEX_NAME = "financial-data"
DIMENSION = 10  # Dimension des vecteurs

def normalize_vector(vector):
    """
    Normalise un vecteur pour qu'il ait une norme unitaire.
    
    Args:
        vector (np.ndarray): Le vecteur à normaliser
        
    Returns:
        np.ndarray: Le vecteur normalisé
    """
    # Convertir en tableau numpy si ce n'est pas déjà le cas
    if not isinstance(vector, np.ndarray):
        vector = np.array(vector, dtype=np.float32)
    
    # Calculer la norme
    norm = np.linalg.norm(vector)
    
    # Normaliser le vecteur
    if norm > 0:
        normalized_vector = vector / norm
    else:
        print('Warning: Zero vector detected, cannot normalize')
        normalized_vector = vector
    
    return normalized_vector

def initialize_pinecone():
    """
    Initialise la connexion à Pinecone et crée l'index s'il n'existe pas.
    
    Returns:
        pinecone.Index: L'index Pinecone
    """
    print(f"Initialisation de Pinecone avec la clé API: {PINECONE_API_KEY[:5]}...")
    
    # Initialiser Pinecone
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
    
    # Vérifier si l'index existe, sinon le créer
    if INDEX_NAME not in pinecone.list_indexes():
        print(f"Création de l'index '{INDEX_NAME}'...")
        pinecone.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric="cosine"
        )
        # Attendre que l'index soit prêt
        print("Attente de la création de l'index...")
        time.sleep(10)
    
    # Se connecter à l'index
    index = pinecone.Index(INDEX_NAME)
    print(f"Connecté à l'index '{INDEX_NAME}'")
    
    return index

def upsert_vectors_with_normalization(index, vectors, metadata_list=None):
    """
    Insère des vecteurs normalisés dans Pinecone.
    
    Args:
        index (pinecone.Index): L'index Pinecone
        vectors (list): Liste de vecteurs à insérer
        metadata_list (list, optional): Liste de métadonnées associées aux vecteurs
        
    Returns:
        dict: Résultat de l'opération d'insertion
    """
    if metadata_list is None:
        metadata_list = [{} for _ in range(len(vectors))]
    
    # Normaliser les vecteurs
    normalized_vectors = [normalize_vector(vec) for vec in vectors]
    
    # Préparer les données pour l'insertion
    items = []
    for i, (vec, metadata) in enumerate(zip(normalized_vectors, metadata_list)):
        # Générer un ID unique pour chaque vecteur
        vector_id = str(uuid.uuid4())
        items.append((vector_id, vec.tolist(), metadata))
    
    # Insérer les vecteurs dans Pinecone
    print(f"Insertion de {len(items)} vecteurs normalisés dans Pinecone...")
    upsert_response = index.upsert(vectors=items)
    
    return upsert_response

def query_with_normalized_vector(index, query_vector, top_k=5):
    """
    Effectue une recherche dans Pinecone avec un vecteur de requête normalisé.
    
    Args:
        index (pinecone.Index): L'index Pinecone
        query_vector (list or np.ndarray): Le vecteur de requête
        top_k (int, optional): Nombre de résultats à retourner
        
    Returns:
        dict: Résultats de la recherche
    """
    # Normaliser le vecteur de requête
    normalized_query = normalize_vector(query_vector)
    
    # Effectuer la recherche
    print(f"Recherche des {top_k} vecteurs les plus similaires...")
    query_response = index.query(
        vector=normalized_query.tolist(),
        top_k=top_k,
        include_metadata=True
    )
    
    return query_response

def test_pinecone_normalization():
    """
    Teste l'intégration de la normalisation avec Pinecone.
    """
    print("=== TEST DE L'INTÉGRATION PINECONE AVEC NORMALISATION ===")
    
    try:
        # Initialiser Pinecone
        index = initialize_pinecone()
        
        # Créer des vecteurs de test
        print("\nCréation de vecteurs de test...")
        test_vectors = [
            np.random.rand(DIMENSION) * 10,  # Vecteur avec une grande norme
            np.random.rand(DIMENSION) * 0.1,  # Vecteur avec une petite norme
            np.random.rand(DIMENSION)         # Vecteur avec une norme moyenne
        ]
        
        # Afficher les normes des vecteurs originaux
        for i, vec in enumerate(test_vectors):
            print(f"Vecteur {i+1} - Norme originale: {np.linalg.norm(vec):.6f}")
        
        # Créer des métadonnées pour les vecteurs
        metadata_list = [
            {"type": "large_norm", "description": "Vecteur avec une grande norme"},
            {"type": "small_norm", "description": "Vecteur avec une petite norme"},
            {"type": "medium_norm", "description": "Vecteur avec une norme moyenne"}
        ]
        
        # Insérer les vecteurs normalisés
        upsert_response = upsert_vectors_with_normalization(index, test_vectors, metadata_list)
        print(f"Résultat de l'insertion: {upsert_response}")
        
        # Attendre que les vecteurs soient indexés
        print("Attente de l'indexation des vecteurs...")
        time.sleep(5)
        
        # Effectuer une recherche avec un vecteur de requête
        print("\nCréation d'un vecteur de requête...")
        query_vector = np.random.rand(DIMENSION) * 5
        print(f"Norme du vecteur de requête: {np.linalg.norm(query_vector):.6f}")
        
        # Rechercher les vecteurs similaires
        query_response = query_with_normalized_vector(index, query_vector)
        
        # Afficher les résultats
        print("\nRésultats de la recherche:")
        for i, match in enumerate(query_response['matches']):
            print(f"Match {i+1}:")
            print(f"  ID: {match['id']}")
            print(f"  Score: {match['score']:.6f}")
            print(f"  Métadonnées: {match['metadata']}")
        
        print("\nTest terminé avec succès!")
        
    except Exception as e:
        print(f"Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pinecone_normalization() 