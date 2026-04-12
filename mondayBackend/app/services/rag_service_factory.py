from typing import Optional, Dict
from app.services.rag_service import RAGService
from app.models.rag import RAG

class RAGServiceFactory:
    _instance: Optional['RAGServiceFactory'] = None
    _services: Dict[str, RAGService] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RAGServiceFactory, cls).__new__(cls)
            cls._instance._services = {}
        return cls._instance

    def get_service(self, rag: RAG) -> RAGService:
        rag_id = str(rag.uuid)
        
        if rag_id not in self._services:
            self._services[rag_id] = RAGService(rag)

        return self._services[rag_id]

rag_service_factory = RAGServiceFactory()