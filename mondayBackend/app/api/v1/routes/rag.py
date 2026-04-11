import os
import shutil
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.rag_service import rag_creation_service

router = APIRouter()

@router.post("/createrag")
def upload_document(
    db: Session = Depends(get_db),
    files: list[UploadFile] = File(...)
):
    rag_id = str(uuid.uuid4())

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
        file_path = os.path.join(rag_creation_service.get_doc_path(rag_id), file.filename)

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

