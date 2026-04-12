import os
import shutil
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.crud.crud_rag import create_rag, get_rag_detail
from app.schemas.provider import Provider
from app.schemas.query import QueryRequest
from app.services.rag_creation_service import rag_creation_service
from app.services.rag_service_factory import rag_service_factory

router = APIRouter()

@router.post("/createrag")
def upload_document(
    db: Session = Depends(get_db),
    files: list[UploadFile] = File(...),
    name: str = Form(...),
    description: str = Form(""),
    model: str = Form(...),
    provider: Provider = Form(...)
):
    rag_id = create_rag(
        db,
        name = name,
        description = description,
        model = model,
        provider = provider)

    base_dir = rag_creation_service.get_docs_path(rag_id)
    os.makedirs(base_dir, exist_ok=True)

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
        file_path = os.path.join(base_dir, file.filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to index document: {e}")
        finally:
            file.file.close()

    ## TODO: Take rag metadata such as name and description and add it to the db

    rag_creation_service.create_index(rag_id)
    return {"msg": "Model Created Succesfully"}


@router.post('/initialize')
def initialize_rag(
    db: Session = Depends(get_db),
    rag_id: str = Form(...)
):
    new_rag_details = get_rag_detail(db, rag_id=rag_id)
    new_rag = rag_service_factory.get_service(rag=new_raxg_details)

    if new_rag is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to initialize RAG"
        )

    return {
        "msg": "RAG initialized successfully"
    }

@router.post("/chat")
def chat_stream(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    rag_service = rag_service_factory.get_service(rag=request.rag)

    if not rag_service.retriever or not rag_service.llm:
        raise HTTPException(
            status_code=503, 
            detail="RAG system is not fully initialized. The retriever or LLM provider is unavailable."
        )
    
    return StreamingResponse(rag_service.chat_stream(query, db), media_type="text/plain")