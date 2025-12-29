import multiprocessing
from llama_index import VectorStoreIndex, Document
from transformers import AutoTokenizer, AutoModel
from llama_index.vector_stores import FAISSVectorStore

# Initialize the tokenizer and model (assuming you're using Hugging Face models)
model_name = "gpt2"  # Or another model that fits your use case
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)


# Function to process a batch of documents and return a partial index
def process_documents_chunk(documents_chunk):
    # Initialize a local VectorStoreIndex for each process
    vector_store = FAISSVectorStore()
    index = VectorStoreIndex(vector_store=vector_store)

    # Process each document, generate embeddings, and add to the index
    for doc in documents_chunk:
        embedding = model(**tokenizer(doc.text, return_tensors='pt'))[0].detach().numpy()
        index.add_document(Document(doc.text), embedding)

    return index


# Function to merge indices
def merge_indices(indices):
    # Merge all the indices into one
    base_index = indices[0]
    for idx in indices[1:]:
        base_index.merge_from(idx)
    return base_index


# Main processing function
def parallel_indexing(documents, num_workers=4):
    # Split the documents into chunks for each worker
    chunks = [documents[i::num_workers] for i in range(num_workers)]

    # Use multiprocessing to process the document chunks in parallel
    with multiprocessing.Pool(processes=num_workers) as pool:
        indices = pool.map(process_documents_chunk, chunks)

    # Merge the partial indices into a single index
    final_index = merge_indices(indices)
    return final_index


# Example usage
if __name__ == "__main__":
    # Example documents
    documents = [Document(f"Document {i} text here.") for i in range(100)]

    # Create the final index using 4 workers
    final_index = parallel_indexing(documents, num_workers=4)

    # Example query
    query_embedding = model(**tokenizer("Search query here", return_tensors='pt'))[0].detach().numpy()
    results = final_index.query(query_embedding)

    # Display results
    for result in results:
        print(result.text)
