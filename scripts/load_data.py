# POC-Agent-AI-ouvertures-echecs-FFE/scripts/load_data.py

"""
Script de chargement des données dans Milvus.
Pipeline complet RAG :
- Chargement dataset
- Chunking
- Embedding
- Indexation
"""

import json
from backend.app.rag.embedding_service import embedding_service
from backend.app.rag.milvus_service import milvus_service


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50):
    """
    Découpe un texte en chunks avec overlap.

    Args:
        text: texte brut
        chunk_size: taille des chunks
        overlap: chevauchement

    Returns:
        List[str]
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))

    return chunks


def load_dataset(path: str):
    """
    Charge le dataset JSON.

    Format attendu:
    [
        {"text": "..."},
        {"text": "..."}
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """
    Pipeline principal.
    """
    dataset = load_dataset("data/chess/wikichess_sample.json")

    all_chunks = []

    for item in dataset:
        chunks = chunk_text(item["text"])
        all_chunks.extend(chunks)

    print(f"Nombre de chunks générés: {len(all_chunks)}")

    embeddings = embedding_service.embed_batch(all_chunks)

    milvus_service.insert_data(all_chunks, embeddings)

    print("✅ Données insérées dans Milvus")


if __name__ == "__main__":
    main()
