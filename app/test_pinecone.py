import pinecone
import numpy as np
from typing import List

# Configuration Pinecone
API_KEY = "pcsk_6qPf8_5pRfWxo8V8oY7PR9bstoYFJkUJK7CkTgTXw39PSqvpwtkzbVy3zDKaEaQFUTEva"
ENVIRONMENT = "gcp-starter"
INDEX_NAME = "financial-data-test"
VECTOR_DIMENSION = 1536

def generate_dummy_vector(dimension: int = VECTOR_DIMENSION) -> List[float]:
    """Génère un vecteur aléatoire normalisé pour les tests."""
    vector = np.random.rand(dimension).astype(np.float32)
    # Normaliser le vecteur pour qu'il ait une norme unitaire
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    else:
        print('Warning: Zero vector detected, cannot normalize')
