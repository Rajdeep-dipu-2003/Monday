import uuid
import enum
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Provider(enum.Enum):
    ollama: "Ollama"
    openai: "OpenAi"
    gemini: "Gemini"

class RAG(Base):
    __tablename__ = "rags"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    model = Column(String, nullable=False)
    provider = Column(Enum(Provider), nullable=False)

    documents = relationship("Document", back_populates="rag", cascade="all, delete")