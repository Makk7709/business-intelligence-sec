import os
import json
import pinecone
import numpy as np
from typing import Dict, List, Any, Optional, Union
import time

# Clé API Pinecone
PINECONE_API_KEY = "pcsk_6qPf8_5pRfWxo8V8oY7PR9bstoYFJkUJK7CkTgTXw39PSqvpwtkzbVy3zDKaEaQFUTEva"
# Environnement Pinecone (généralement "gcp-starter" pour les comptes gratuits)
PINECONE_ENVIRONMENT = "gcp-starter"
# Nom de l'index Pinecone
INDEX_NAME = "financial-data"
# Dimension des vecteurs (à ajuster selon votre modèle d'embedding)
VECTOR_DIMENSION = 1536  # Dimension standard pour les embeddings OpenAI

class PineconeManager:
    """Gestionnaire pour l'intégration avec Pinecone."""
    
    def __init__(self, api_key: str = None, environment: str = None, index_name: str = None):
        """
        Initialise le gestionnaire Pinecone.
        
        Args:
            api_key: Clé API Pinecone (utilise la variable globale si non spécifiée)
            environment: Environnement Pinecone (utilise la variable globale si non spécifié)
            index_name: Nom de l'index (utilise la variable globale si non spécifié)
        """
        self.api_key = api_key or PINECONE_API_KEY
        self.environment = environment or PINECONE_ENVIRONMENT
        self.index_name = index_name or INDEX_NAME
        self.index = None
        
        # Initialiser la connexion à Pinecone
        pinecone.init(api_key=self.api_key, environment=self.environment)
        
    def create_index(self, dimension: int = VECTOR_DIMENSION, metric: str = "cosine") -> bool:
        """
        Crée un nouvel index Pinecone s'il n'existe pas déjà.
        
        Args:
            dimension: Dimension des vecteurs
            metric: Métrique de similarité ('cosine', 'euclidean', 'dotproduct')
            
        Returns:
            bool: True si l'index a été créé ou existe déjà
        """
        try:
            # Vérifier si l'index existe déjà
            if self.index_name not in pinecone.list_indexes():
                print(f"Création de l'index '{self.index_name}'...")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric=metric
                )
                # Attendre que l'index soit prêt
                while not self.index_name in pinecone.list_indexes():
                    time.sleep(1)
                print(f"Index '{self.index_name}' créé avec succès.")
            else:
                print(f"L'index '{self.index_name}' existe déjà.")
            
            # Connecter à l'index
            self.index = pinecone.Index(self.index_name)
            return True
            
        except Exception as e:
            print(f"Erreur lors de la création de l'index: {e}")
            return False
    
    def delete_index(self) -> bool:
        """
        Supprime l'index Pinecone.
        
        Returns:
            bool: True si l'index a été supprimé avec succès
        """
        try:
            if self.index_name in pinecone.list_indexes():
                pinecone.delete_index(self.index_name)
                print(f"Index '{self.index_name}' supprimé avec succès.")
                self.index = None
                return True
            else:
                print(f"L'index '{self.index_name}' n'existe pas.")
                return False
        except Exception as e:
            print(f"Erreur lors de la suppression de l'index: {e}")
            return False
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> bool:
        """
        Insère ou met à jour des vecteurs dans l'index.
        
        Args:
            vectors: Liste de dictionnaires contenant 'id', 'values' (vecteur) et 'metadata'
            
        Returns:
            bool: True si l'opération a réussi
        """
        try:
            if self.index is None:
                self.create_index()
                
            # Formater les vecteurs pour Pinecone
            pinecone_vectors = []
            for vector in vectors:
                pinecone_vectors.append({
                    'id': vector['id'],
                    'values': vector['values'],
                    'metadata': vector.get('metadata', {})
                })
            
            # Insérer les vecteurs par lots de 100 maximum
            batch_size = 100
            for i in range(0, len(pinecone_vectors), batch_size):
                batch = pinecone_vectors[i:i+batch_size]
                self.index.upsert(vectors=batch)
                
            print(f"{len(vectors)} vecteurs insérés avec succès.")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'insertion des vecteurs: {e}")
            return False
    
    def query(self, 
              query_vector: List[float], 
              top_k: int = 5, 
              filter: Dict = None, 
              include_metadata: bool = True) -> List[Dict]:
        """
        Effectue une recherche de similarité dans l'index.
        
        Args:
            query_vector: Vecteur de requête
            top_k: Nombre de résultats à retourner
            filter: Filtre à appliquer sur les métadonnées
            include_metadata: Inclure les métadonnées dans les résultats
            
        Returns:
            List[Dict]: Liste des résultats de la recherche
        """
        try:
            if self.index is None:
                self.create_index()
                
            # Effectuer la recherche
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=include_metadata,
                filter=filter
            )
            
            return results.to_dict()['matches']
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Récupère les statistiques de l'index.
        
        Returns:
            Dict: Statistiques de l'index
        """
        try:
            if self.index is None:
                self.create_index()
                
            return self.index.describe_index_stats()
            
        except Exception as e:
            print(f"Erreur lors de la récupération des statistiques: {e}")
            return {}

def generate_dummy_vector(dimension: int = VECTOR_DIMENSION) -> List[float]:
    """
    Génère un vecteur aléatoire pour les tests.
    
    Args:
        dimension: Dimension du vecteur
        
    Returns:
        List[float]: Vecteur aléatoire normalisé
    """
    vector = np.random.rand(dimension).astype(np.float32)
    # Normaliser le vecteur (pour la similarité cosinus)
    vector = vector / np.linalg.norm(vector)
    return vector.tolist()

def load_financial_data_to_pinecone(data_dir: str = "data/results", manager: PineconeManager = None) -> bool:
    """
    Charge les données financières depuis les fichiers JSON et les insère dans Pinecone.
    
    Args:
        data_dir: Répertoire contenant les données financières
        manager: Instance de PineconeManager (en crée une nouvelle si non spécifiée)
        
    Returns:
        bool: True si l'opération a réussi
    """
    if manager is None:
        manager = PineconeManager()
        
    try:
        # Créer l'index s'il n'existe pas
        manager.create_index()
        
        # Parcourir les sous-répertoires (individual, comparative, etc.)
        vectors = []
        vector_id = 0
        
        for subdir in os.listdir(data_dir):
            subdir_path = os.path.join(data_dir, subdir)
            if not os.path.isdir(subdir_path):
                continue
                
            # Parcourir les fichiers JSON dans le sous-répertoire
            for filename in os.listdir(subdir_path):
                if not filename.endswith('.json'):
                    continue
                    
                file_path = os.path.join(subdir_path, filename)
                try:
                    # Charger les données JSON
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Pour chaque entrée, créer un vecteur
                    # Note: Dans un cas réel, vous utiliseriez un modèle d'embedding pour générer les vecteurs
                    # Ici, nous utilisons des vecteurs aléatoires pour la démonstration
                    
                    # Extraire le nom de l'entreprise du nom de fichier
                    company = filename.split('_')[0] if '_' in filename else filename.replace('.json', '')
                    
                    # Créer un vecteur pour l'ensemble du document
                    vector_id += 1
                    vectors.append({
                        'id': f"doc_{vector_id}",
                        'values': generate_dummy_vector(),
                        'metadata': {
                            'type': 'document',
                            'company': company,
                            'category': subdir,
                            'filename': filename,
                            'path': file_path
                        }
                    })
                    
                    # Si c'est une analyse individuelle, créer des vecteurs pour chaque métrique
                    if subdir == 'individual' and 'metrics' in data:
                        for year, metrics in data['metrics'].items():
                            for metric_name, value in metrics.items():
                                if value is not None:  # Ignorer les valeurs nulles
                                    vector_id += 1
                                    vectors.append({
                                        'id': f"metric_{vector_id}",
                                        'values': generate_dummy_vector(),
                                        'metadata': {
                                            'type': 'metric',
                                            'company': company,
                                            'year': year,
                                            'metric_name': metric_name,
                                            'value': value,
                                            'path': file_path
                                        }
                                    })
                    
                    # Si c'est une analyse comparative, créer des vecteurs pour chaque comparaison
                    elif subdir == 'comparative' and 'comparisons' in data:
                        for metric, companies in data['comparisons'].items():
                            for company_name, rank in companies.items():
                                vector_id += 1
                                vectors.append({
                                    'id': f"comparison_{vector_id}",
                                    'values': generate_dummy_vector(),
                                    'metadata': {
                                        'type': 'comparison',
                                        'metric': metric,
                                        'company': company_name,
                                        'rank': rank,
                                        'path': file_path
                                    }
                                })
                
                except Exception as e:
                    print(f"Erreur lors du traitement du fichier {file_path}: {e}")
        
        # Insérer les vecteurs dans Pinecone
        if vectors:
            return manager.upsert_vectors(vectors)
        else:
            print("Aucune donnée à insérer.")
            return False
            
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return False

def search_financial_data(query: str, filter: Dict = None, top_k: int = 5, manager: PineconeManager = None):
    """
    Recherche des données financières dans Pinecone.
    
    Args:
        query: Requête de recherche (dans un cas réel, serait convertie en embedding)
        filter: Filtre à appliquer sur les métadonnées
        top_k: Nombre de résultats à retourner
        manager: Instance de PineconeManager (en crée une nouvelle si non spécifiée)
        
    Returns:
        List[Dict]: Résultats de la recherche
    """
    if manager is None:
        manager = PineconeManager()
        
    try:
        # Dans un cas réel, vous utiliseriez un modèle d'embedding pour convertir la requête en vecteur
        # Ici, nous utilisons un vecteur aléatoire pour la démonstration
        query_vector = generate_dummy_vector()
        
        # Effectuer la recherche
        results = manager.query(query_vector, top_k=top_k, filter=filter)
        return results
        
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")
        return []

def main():
    """Fonction principale pour tester l'intégration Pinecone."""
    print("=== Test de l'intégration Pinecone ===")
    
    # Créer une instance du gestionnaire Pinecone
    manager = PineconeManager()
    
    # Créer l'index
    manager.create_index()
    
    # Charger les données financières dans Pinecone
    print("\nChargement des données financières dans Pinecone...")
    load_financial_data_to_pinecone(manager=manager)
    
    # Afficher les statistiques de l'index
    print("\nStatistiques de l'index:")
    stats = manager.get_stats()
    print(f"Nombre total de vecteurs: {stats.get('total_vector_count', 0)}")
    print(f"Dimensions des vecteurs: {stats.get('dimension', 0)}")
    
    # Effectuer une recherche
    print("\nRecherche de données financières:")
    
    # Exemple 1: Recherche générale
    print("\n1. Recherche générale:")
    results = search_financial_data("performance financière", top_k=3, manager=manager)
    for i, result in enumerate(results):
        print(f"Résultat {i+1}:")
        print(f"  Score de similarité: {result.get('score', 0):.4f}")
        print(f"  Type: {result.get('metadata', {}).get('type', 'inconnu')}")
        print(f"  Entreprise: {result.get('metadata', {}).get('company', 'inconnue')}")
        if 'metric_name' in result.get('metadata', {}):
            print(f"  Métrique: {result['metadata']['metric_name']}")
            print(f"  Année: {result['metadata']['year']}")
            print(f"  Valeur: {result['metadata']['value']}")
    
    # Exemple 2: Recherche filtrée par entreprise
    print("\n2. Recherche filtrée par entreprise (Tesla):")
    results = search_financial_data(
        "performance financière", 
        filter={"company": "tesla"}, 
        top_k=3, 
        manager=manager
    )
    for i, result in enumerate(results):
        print(f"Résultat {i+1}:")
        print(f"  Score de similarité: {result.get('score', 0):.4f}")
        print(f"  Type: {result.get('metadata', {}).get('type', 'inconnu')}")
        print(f"  Entreprise: {result.get('metadata', {}).get('company', 'inconnue')}")
        if 'metric_name' in result.get('metadata', {}):
            print(f"  Métrique: {result['metadata']['metric_name']}")
            print(f"  Année: {result['metadata']['year']}")
            print(f"  Valeur: {result['metadata']['value']}")
    
    print("\n=== Fin du test ===")

if __name__ == "__main__":
    main() 