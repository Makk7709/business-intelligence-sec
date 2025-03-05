import numpy as np

def normalize_vector(vector):
    """Normalise un vecteur pour qu'il ait une norme unitaire."""
    # Convertir en tableau numpy si ce n'est pas déjà le cas
    if not isinstance(vector, np.ndarray):
        vector = np.array(vector, dtype=np.float32)
    
    # Calculer la norme
    norm = np.linalg.norm(vector)
    
    # Normaliser le vecteur
    if norm > 0:
        vector = vector / norm
    else:
        print('Warning: Zero vector detected, cannot normalize')
    
    return vector

# Test de normalisation de vecteur
print("Test de normalisation de vecteur:")
vector = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
print(f"Vecteur original: {vector}")
print(f"Norme du vecteur original: {np.linalg.norm(vector)}")

normalized_vector = normalize_vector(vector)
print(f"Vecteur normalisé: {normalized_vector}")
print(f"Norme du vecteur normalisé: {np.linalg.norm(normalized_vector)}")

# Test avec un vecteur aléatoire
print("\nTest avec un vecteur aléatoire:")
random_vector = np.random.rand(10)
print(f"Vecteur aléatoire: {random_vector}")
print(f"Norme du vecteur aléatoire: {np.linalg.norm(random_vector)}")

normalized_random = normalize_vector(random_vector)
print(f"Vecteur aléatoire normalisé: {normalized_random}")
print(f"Norme du vecteur aléatoire normalisé: {np.linalg.norm(normalized_random)}")

print("\nTest réussi!") 