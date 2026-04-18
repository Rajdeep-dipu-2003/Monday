import logging
import re

from pathlib import Path
from typing import Optional, List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangchainDocument
from llama_index.core.schema import Document as LlamaDocument
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGCreationService:
    _instance: Optional['RAGCreationService'] = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(RAGCreationService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass

    def get_index_path(self, rag_id: str):
        return Path(f"data/rags/{rag_id}/index")
    
    def get_docs_path(self, rag_id: str):
        return Path(f"data/rags/{rag_id}/documents")
    
    def _langchain_docs_to_llama(self, docs: List[LangchainDocument]) -> List[LlamaDocument]:
        return [LlamaDocument(text=doc.page_content, metadata=doc.metadata) for doc in docs]
    
    def _clean_document_content(self, content: str) -> str:
        if not content:
            return ""

        # 🔹 1. Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # 🔹 2. Remove common page patterns
        content = re.sub(r'Page\s*\d+\s*(of\s*\d+)?', '', content, flags=re.IGNORECASE)

        # 🔹 3. Remove repeated headers/footers (generic heuristic)
        # removes lines that repeat too often (basic approach)
        lines = content.split('\n')
        line_counts = {}
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                line_counts[line] = line_counts.get(line, 0) + 1

        # remove lines that appear too frequently (like headers)
        content = '\n'.join([
            line for line in lines
            if line_counts.get(line.strip(), 0) < 5
        ])

        # 🔹 4. Fix broken words (PDF hyphenation)
        content = re.sub(r'(\w+)-\n(\w+)', r'\1\2', content)

        # 🔹 5. Remove extra spaces/tabs
        content = re.sub(r'[ \t]+', ' ', content)

        # 🔹 6. Clean spaces around newlines
        content = re.sub(r'\s*\n\s*', '\n', content)

        # 🔹 7. Remove multiple newlines
        content = re.sub(r'\n{2,}', '\n\n', content)

        # 🔹 8. Remove non-printable characters
        content = re.sub(r'[^\x20-\x7E\n]', '', content)

        # 🔹 9. Strip leading/trailing whitespace
        content = content.strip()

        return content
    
    def _load_documents(self, rag_id: str) -> List[LangchainDocument]:
        try:
            raw_documents = []
            pdf_files = list(self.get_docs_path(rag_id).glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"No PDF files found in {self.get_docs_path(rag_id)}")
                return []
            for file_path in pdf_files:
                try:
                    logger.info(f"Loading {file_path.name}...")
                    loader = PyPDFLoader(str(file_path))
                    docs = loader.load()
                    raw_documents.extend(docs)
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {e}")
                    continue
            cleaned_docs = []
            for doc in raw_documents:
                cleaned_content = self._clean_document_content(content=doc.page_content)
                if cleaned_content:
                    doc.page_content = cleaned_content
                    cleaned_docs.append(doc)
            return cleaned_docs
        except Exception as e:
            logger.error(f"Error in _load_documents: {e}")
            return []
        
    def load_or_create_index(self, rag_id: str) -> Optional[VectorStoreIndex]:
        try:
            if (self.get_index_path(rag_id=rag_id)).exists():
                logger.info(f"Loading existing LlamaIndex vector store from {self.get_index_path(rag_id=rag_id)}")

                embed_model = HuggingFaceEmbedding(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

                Settings.embed_model = embed_model

                storage_context = StorageContext.from_defaults(persist_dir=str(self.get_index_path(rag_id=rag_id)))
                vector_store = load_index_from_storage(storage_context)
                logger.info("LlamaIndex vector store loaded successfully.")
                return vector_store
            else:
                logger.warning(f"No existing index found at {self.get_index_path(rag_id=rag_id)}.")
                logger.warning(f"Creating new vector store at {self.get_index_path(rag_id=rag_id)}.")
                return self.create_index(rag_id=rag_id)
        except Exception as e:
            logger.error(f"Error loading/creating LlamaIndex: {e}", exc_info=True)
    
    def create_index(self, rag_id: str) -> Optional[VectorStoreIndex]:
        try:
            documents = self._load_documents(rag_id)
            if not documents:
                logger.error("No documents found to create index.")
                return None
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_documents(documents)
            llama_chunks = self._langchain_docs_to_llama(chunks)

            embed_model = HuggingFaceEmbedding(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            index = VectorStoreIndex(
                llama_chunks,
                embed_model=embed_model
            )
            index.storage_context.persist(persist_dir=str(self.get_index_path(rag_id)))

            logger.info(f"LlamaIndex vector store created and saved to {self.get_index_path(rag_id)}")
            return index
        except Exception as e:
            logger.error(f"Error creating LlamaIndex: {e}", exc_info=True)
            return None


    
    # def add_document_to_index(self, file_path: str, rag_id: str):

    
rag_creation_service = RAGCreationService()