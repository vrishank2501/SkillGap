import re
import logging
from typing import List, Dict, Any, Optional
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

class DocumentSearchEngine:
    """Handles grounded document retrieval using Supabase full-text search or local cache."""

    def __init__(self):
        self._local_chunks: List[Dict[str, Any]] = []

    def register_local_chunks(self, chunks: List[Dict[str, Any]]):
        """Allows testing retrieval in memory without active Supabase instance."""
        self._local_chunks.extend(chunks)

    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        client = get_supabase_client()
        
        # 1. Attempt Supabase Full-Text Search if client is connected
        if client and user_id:
            try:
                # Query document_chunks using text search
                query_clean = re.sub(r"[^\w\s]", "", query).strip()
                if query_clean:
                    response = (
                        client.table("document_chunks")
                        .select("id, document_id, chunk_index, content, page_number, documents(filename)")
                        .eq("user_id", user_id)
                        .text_search("tsv", query_clean, options={"type": "plain", "config": "english"})
                        .limit(top_k)
                        .execute()
                    )
                    if response.data:
                        results = []
                        for row in response.data:
                            doc_meta = row.get("documents") or {}
                            results.append({
                                "id": row.get("id"),
                                "filename": doc_meta.get("filename", "Uploaded Document"),
                                "page_number": row.get("page_number", 1),
                                "content": row.get("content", ""),
                            })
                        return results
            except Exception as e:
                logger.warning(f"Supabase text_search failed: {e}. Falling back to keyword search.")

        # 2. In-memory keyword scoring fallback
        return self._keyword_search(query, top_k)

    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        if not self._local_chunks:
            return []

        query_tokens = set(re.findall(r"\w+", query.lower()))
        if not query_tokens:
            return self._local_chunks[:top_k]

        scored = []
        for chunk in self._local_chunks:
            content_tokens = set(re.findall(r"\w+", chunk.get("content", "").lower()))
            overlap = len(query_tokens.intersection(content_tokens))
            if overlap > 0:
                scored.append((overlap, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

document_search = DocumentSearchEngine()

