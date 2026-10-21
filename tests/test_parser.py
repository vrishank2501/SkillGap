import pytest
from app.documents.parser import document_parser

def test_document_chunker():
    pages = [
        {
            "filename": "guide.txt",
            "page_number": 1,
            "text": " ".join([f"word{i}" for i in range(300)])
        }
    ]
    chunks = document_parser.chunk_document(pages, chunk_size_words=100, overlap_words=20)
    assert len(chunks) >= 3
    assert chunks[0].filename == "guide.txt"
    assert chunks[0].page_number == 1
    assert "word0" in chunks[0].content

