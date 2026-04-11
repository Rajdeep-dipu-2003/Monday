import uuid
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class RAG(Base):
    __tablename__ = "rags"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)

    documents = relationship("Document", back_populates="rag", cascade="all, delete")