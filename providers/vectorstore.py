from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader
from providers.embeddings import get_embeddings
import os

VECTORSTORE = None
RETRIEVER = None
CHUNKS = None

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "hr_policies")


def load_documents():
    docs = []
    for fname in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, fname)
        if fname.endswith(".pdf"):
            docs.extend(PyPDFLoader(path).load())
        elif fname.endswith(".txt"):
            docs.extend(TextLoader(path).load())
    return docs

def get_retriever():
    global VECTORSTORE, RETRIEVER, CHUNKS
    if RETRIEVER is not None:
        return RETRIEVER
    docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    CHUNKS = splitter.split_documents(docs)
    embeddings = get_embeddings()
    VECTORSTORE = Chroma.from_documents(CHUNKS, embeddings)
    RETRIEVER = VECTORSTORE.as_retriever()
    return RETRIEVER

def reset_vector_db():
    global VECTORSTORE, RETRIEVER, CHUNKS
    docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    CHUNKS = splitter.split_documents(docs)
    embeddings = get_embeddings()
    VECTORSTORE = Chroma.from_documents(CHUNKS, embeddings)
    RETRIEVER = VECTORSTORE.as_retriever()