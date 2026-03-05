"""
RAG Embedder — loads the security knowledge base into ChromaDB
and provides semantic retrieval for anomaly context.
"""
import chromadb
from chromadb.utils import embedding_functions
from app.rag_engine.knowledge_base import SECURITY_KNOWLEDGE_BASE
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "secrag_knowledge"

_client = None
_collection = None


def get_chroma_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        ef = embedding_functions.DefaultEmbeddingFunction()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def load_knowledge_base(force_reload: bool = False) -> int:
    """
    Load OWASP/security knowledge into ChromaDB.
    Returns the number of documents loaded.
    """
    collection = get_collection()

    if not force_reload and collection.count() > 0:
        logger.info("Knowledge base already loaded (%d docs). Skipping.", collection.count())
        return collection.count()

    if force_reload:
        get_chroma_client().delete_collection(COLLECTION_NAME)
        # Re-create
        global _collection
        _collection = None
        collection = get_collection()

    ids = [doc["id"] for doc in SECURITY_KNOWLEDGE_BASE]
    docs = [doc["content"] for doc in SECURITY_KNOWLEDGE_BASE]
    metadatas = [
        {
            "title": doc["title"],
            "category": doc["category"],
            "severity": doc["severity"],
            "fix": doc["fix"],
        }
        for doc in SECURITY_KNOWLEDGE_BASE
    ]

    collection.add(ids=ids, documents=docs, metadatas=metadatas)
    logger.info("Loaded %d security knowledge documents into ChromaDB", len(ids))
    return len(ids)


def retrieve_context(query: str, n_results: int = 4) -> str:
    """
    Retrieve the most relevant security knowledge chunks for a query.
    Returns formatted context string for inclusion in LLM prompt.
    """
    collection = get_collection()

    if collection.count() == 0:
        load_knowledge_base()

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas"],
    )

    context_parts = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_parts.append(
            f"### {meta['title']} (Severity: {meta['severity']})\n"
            f"{doc}\n"
            f"**Recommended Fix:** {meta['fix']}"
        )

    return "\n\n".join(context_parts)
