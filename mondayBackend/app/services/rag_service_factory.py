from typing import Optional
from app.services.rag_service import RAGService

class RAGServiceFactory:
    _instance: Optional['RAGServiceFactory'] = None
    _lock = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RAGServiceFactory, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._services = {}
        self._initialized = True

    def get_service(self, rag_id: str) -> RAGService:
        if rag_id in self._services:
            return self._services[rag_id]
        

