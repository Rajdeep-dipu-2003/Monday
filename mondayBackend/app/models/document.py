from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)

    rag_id = Column(Integer, ForeignKey("rags.id"), nullable=False)

    rag = relationship("RAG", back_populates="documents")