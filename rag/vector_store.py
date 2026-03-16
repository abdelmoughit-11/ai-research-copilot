from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def create_vector_db(texts: list[str]):
    """
    Utilise HuggingFace embeddings (gratuit, local, aucune clé API).
    Le modèle se télécharge automatiquement la première fois (~90MB).
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = FAISS.from_texts(texts, embeddings)
    return db