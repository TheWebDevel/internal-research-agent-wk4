from langchain.embeddings import SentenceTransformerEmbeddings

def get_embeddings():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")