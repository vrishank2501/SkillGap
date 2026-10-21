import os
import shutil
import logging
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.documents.parser import document_parser
from app.documents.search import document_search

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)

# Fallback in-memory list of documents for local testing
_local_docs = []

@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
):
    uid = request.state.user_id
    filename = file.filename or "uploaded_file"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail="Only .pdf, .txt, and .md files are supported.")

    file_path = os.path.join(settings.DOCUMENT_STORAGE_DIR, f"{uid}_{filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    # Parse and chunk document
    try:
        if ext == ".pdf":
            pages = document_parser.parse_pdf(file_path, filename)
        else:
            pages = document_parser.parse_text(file_path, filename)

        chunks = document_parser.chunk_document(pages)
        raw_chunks = [c.to_dict() for c in chunks]

        # Register chunks in local search engine cache
        document_search.register_local_chunks(raw_chunks, user_id=uid)

        # Persist to Supabase if available
        client = get_supabase_client()
        doc_id = None
        if client and uid:
            try:
                # 1. Insert Document record
                doc_record = {
                    "user_id": uid,
                    "filename": filename,
                    "file_type": ext.replace(".", ""),
                    "file_size": file_size,
                    "storage_path": file_path,
                }
                res = client.table("documents").insert(doc_record).execute()
                if res.data and len(res.data) > 0:
                    doc_id = res.data[0]["id"]

                # 2. Insert Document Chunks
                if doc_id and chunks:
                    chunk_records = []
                    for c in chunks:
                        chunk_records.append({
                            "document_id": doc_id,
                            "user_id": uid,
                            "chunk_index": c.chunk_index,
                            "content": c.content,
                            "page_number": c.page_number,
                        })
                    client.table("document_chunks").insert(chunk_records).execute()
            except Exception as e:
                logger.warning(f"Could not persist document to Supabase: {e}")

        doc_summary = {
            "id": doc_id or f"local-{len(_local_docs) + 1}",
            "user_id": uid,
            "filename": filename,
            "file_size": file_size,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
        }
        _local_docs.append(doc_summary)

        return {
            "status": "success",
            "message": f"Successfully parsed and indexed {filename}",
            "document": doc_summary,
        }

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@router.get("/")
async def list_documents(request: Request):
    uid = request.state.user_id
    client = get_supabase_client()
    if client and uid:
        try:
            res = client.table("documents").select("id, filename, file_size, created_at").eq("user_id", uid).execute()
            if res.data:
                return {"documents": res.data}
        except Exception as e:
            logger.warning(f"Failed to query Supabase documents: {e}")

    return {
        "documents": [
            {key: value for key, value in document.items() if key != "user_id"}
            for document in _local_docs
            if document["user_id"] == uid
        ]
    }

