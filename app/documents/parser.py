import os
from pathlib import Path
from typing import List, Dict, Any

class DocumentChunk:
    def __init__(self, chunk_index: int, content: str, page_number: int, filename: str):
        self.chunk_index = chunk_index
        self.content = content
        self.page_number = page_number
        self.filename = filename

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_index": self.chunk_index,
            "content": self.content,
            "page_number": self.page_number,
            "filename": self.filename,
        }

class DocumentParser:
    """Extracts text from PDF and TXT documents and chunks them for grounded citations."""

    def parse_pdf(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        import fitz  # PyMuPDF
        pages = []
        doc = fitz.open(file_path)
        try:
            for page_idx in range(len(doc)):
                page = doc.load_page(page_idx)
                text = page.get_text("text").strip()
                if text:
                    pages.append({"page_number": page_idx + 1, "text": text, "filename": filename})
        finally:
            doc.close()
        return pages

    def parse_text(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        text = Path(file_path).read_text(encoding="utf-8", errors="replace").strip()
        return [{"page_number": 1, "text": text, "filename": filename}]

    def chunk_document(
        self,
        pages: List[Dict[str, Any]],
        chunk_size_words: int = 250,
        overlap_words: int = 40,
    ) -> List[DocumentChunk]:
        """
        Chunks pages into overlapping segments while preserving original page references.
        """
        chunks: List[DocumentChunk] = []
        chunk_idx = 0

        for page_data in pages:
            page_num = page_data["page_number"]
            filename = page_data["filename"]
            words = page_data["text"].split()

            if not words:
                continue

            i = 0
            while i < len(words):
                chunk_words = words[i : i + chunk_size_words]
                chunk_text = " ".join(chunk_words)
                chunks.append(
                    DocumentChunk(
                        chunk_index=chunk_idx,
                        content=chunk_text,
                        page_number=page_num,
                        filename=filename,
                    )
                )
                chunk_idx += 1
                if i + chunk_size_words >= len(words):
                    break
                i += chunk_size_words - overlap_words

        return chunks

document_parser = DocumentParser()

