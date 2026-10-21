import pytest
from app.documents.parser import document_parser
from app.documents.search import DocumentSearchEngine

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


@pytest.mark.asyncio
async def test_local_document_search_is_isolated_by_user():
    search = DocumentSearchEngine()
    search.register_local_chunks(
        [{"content": "hippocampus supports memory", "filename": "notes.txt", "page_number": 1}],
        user_id="user-a",
    )
    search.register_local_chunks(
        [{"content": "hippocampus controls unrelated data", "filename": "other.txt", "page_number": 1}],
        user_id="user-b",
    )

    results = await search.search("hippocampus", user_id="user-a")
    other_user_results = await search.search("hippocampus", user_id="user-c")

    assert [result["filename"] for result in results] == ["notes.txt"]
    assert "user_id" not in results[0]
    assert other_user_results == []

