from app.models.rag import RAG
from sqlalchemy.orm import Session

def create_rag(db: Session, *, name: str, description: str, model: str, provider: str) -> str:
    new_rag = RAG(
        name = name,
        description = description,
        model = model,
        provider = provider
    )

    db.add(new_rag)
    db.commit()
    db.refresh(new_rag)

    return new_rag.uuid

def get_rag_detail(db: Session, *, rag_id: str) -> RAG:
    rag = db.query(RAG).filter(RAG.uuid == rag_id).first()
    return rag