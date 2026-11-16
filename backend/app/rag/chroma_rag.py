import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.app.core.config import settings
from backend.app.rag.embedder import GeminiEmbedder
from backend.app.rag.ingest import load_all_knowledge_chunks

logger = logging.getLogger("rag.chroma")


class KnowledgeBaseRAG:
    """Manages vector storage and semantic retrieval for company knowledge base."""

    def __init__(self, gemini_client: Optional[Any] = None):
        self.persist_dir = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_dir, exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection_name = "novatech_knowledge_base"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.embedder = GeminiEmbedder(gemini_client)

    async def ingest_documents(self, force_reload: bool = False) -> int:
        """Loads and indexes knowledge base markdown chunks into ChromaDB."""
        count = self.collection.count()
        if count > 0 and not force_reload:
            logger.info(f"Knowledge base already indexed with {count} chunks.")
            return count

        if force_reload and count > 0:
            self.chroma_client.delete_collection(self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )

        chunks = load_all_knowledge_chunks(settings.KNOWLEDGE_BASE_DIR)
        if not chunks:
            logger.warning("No knowledge chunks found to index.")
            return 0

        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [c["metadata"]["chunk_id"] for c in chunks]

        # Generate embeddings
        embeddings = await self.embedder.embed_documents(texts)

        # Chroma upsert
        self.collection.upsert(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Successfully indexed {len(texts)} chunks into ChromaDB.")
        return len(texts)

    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Searches ChromaDB for relevant knowledge chunks."""
        count = self.collection.count()
        if count == 0:
            await self.ingest_documents()

        query_embedding = await self.embedder.embed_query(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, max(1, self.collection.count())),
            include=["documents", "metadatas", "distances"]
        )

        retrieved: List[Dict[str, Any]] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return retrieved

        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, dist in zip(docs, metas, distances):
            # Cosine distance: smaller is closer, similarity = 1 - dist
            similarity = 1.0 - dist
            retrieved.append({
                "text": doc,
                "metadata": meta,
                "similarity": round(similarity, 3)
            })

        return retrieved

    def build_grounded_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Formats retrieved chunks into a prompt grounding block."""
        if not chunks:
            return "No verified knowledge base documents found for this query."

        context_lines = ["--- VERIFIED NOVATECH KNOWLEDGE BASE CONTEXT ---"]
        for idx, chunk in enumerate(chunks, 1):
            src = chunk["metadata"].get("source", "Doc")
            sec = chunk["metadata"].get("section", "Section")
            sim = chunk.get("similarity", 0.0)
            context_lines.append(f"[{idx}] Source: {src} | Section: {sec} (Relevance: {sim})")
            context_lines.append(chunk["text"].strip())
            context_lines.append("")
        context_lines.append("--- END OF CONTEXT ---")
        return "\n".join(context_lines)
