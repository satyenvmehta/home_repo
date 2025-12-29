import faiss
import numpy as np

# Example: dimension of the vectors (e.g., 768 for BERT/GPT-2 embeddings)
dimension = 768

# Create a flat index for L2 distance (Euclidean distance)
index = faiss.IndexFlatL2(dimension)

# Example: Generate random vectors (each representing a document embedding)
num_vectors = 1000  # Number of documents
vectors = np.random.random((num_vectors, dimension)).astype('float32')

# Add these vectors to the index
index.add(vectors)

# Create a random query vector (to simulate searching for similar documents)
query_vector = np.random.random((1, dimension)).astype('float32')

# Perform a search for the top 5 most similar vectors (nearest neighbors)
distances, indices = index.search(query_vector, k=5)

print("Indices of the nearest neighbors:", indices)
print("Distances to the nearest neighbors:", distances)
