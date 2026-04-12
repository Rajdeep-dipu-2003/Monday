import logging
import torch
import json
from pathlib import Path
from typing import Iterator, List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.documents import Document as LangchainDocument
from sqlalchemy.orm import Session
from sentence_transformers import util

from app.models.rag import RAG
from app.services.rag_creation_service import rag_creation_service
from app.schemas.provider import Provider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(
        self,
        rag: RAG,
        initial_k: int = 20,
        rerank_top_n: int = 5,
        score_threshold: float = 0.35
    ):

        try:
            logger.info("Initializing RAG Service...")

            self.docs_path = rag_creation_service.get_docs_path(rag_id=rag.uuid)
            self.index_path = rag_creation_service.get_index_path(rag_id=rag.uuid)
            self.initial_k = initial_k
            self.rerank_top_n = rerank_top_n
            self.score_threshold = score_threshold
            self.model = rag.model
            self.rag_id = rag.uuid

            logger.info("Loading HuggingFace embedding model via LangChain...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'batch_size': 32, 'normalize_embeddings': True}
            )

        except Exception as e:
            logger.error(f"Failed to initialize RAG Service: {e}", exc_info=True)
            raise

    def initialize(self) -> bool:
        try:
            logger.info("Starting full RAG system initialization...")
            if not self._initialize_llm():
                logger.error("Failed to initialize LLM provider during startup.")
                return False
            if not rag_creation_service.load_or_create_index(rag_id=self.rag_id):
                logger.error("Failed to load or create LlamaIndex vector store.")
                return False
            if not self.setup_retriever():
                logger.error("Failed to setup retriever from LlamaIndex.")
                return False
            logger.info("RAG system initialization complete and ready.")

            self.prompt_template = self._create_prompt_template()
            return True
        except Exception as e:
            logger.error(f"Error during RAG system initialization: {e}", exc_info=True)
            return False

    def _create_prompt_template(self) -> str:
        return """
            You are a helpful assistant. Answer the question using only the information provided in the context below.

            Context:
            {context}

            Question:
            {question}

            Instructions:
            - Answer only using the context.
            - Do not use outside knowledge.
            - If the answer is not present in the context, say: "I don't have enough information to answer this."
            - Keep the answer clear and concise.

            Answer:
        """

    def setup_retriver(self) -> bool:
        try:
            if not self.vectorstore:
                logger.error("Cannot setup retriever: LlamaIndex vector store not loaded.")
                return False
            
            self.retriever = self.vectorstore.as_retriever(similarity_top_k=self.initial_k)
            logger.info(f"LlamaIndex retriever ready (similarity_top_k={self.initial_k}).")
            return True
        except Exception as e:
            logger.error(f"Error setting up retriever: {e}", exc_info=True)
            return False

    def initialize_llm(self) -> bool:
        logger.info(f"Activating LLM provider: {self.provider.upper()}")
        try:
            match self.model:
                case Provider.OLLAMA:
                    self.llm = ChatOllama(
                        model = self.model,
                        temperature=0.1
                    )
                case _:
                    raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider '{self.provider}': {e}")
            self.llm = None
            return False
        
    def _rerank_and_filter_docs(self, query: str, docs: List[LangchainDocument]) -> List[LangchainDocument]:
        if not docs:
            return []
        
        try:
            query_emb = self.embeddings.embed_query(query)
            doc_embs = self.embeddings.embed_documents([d.page_content for d in docs])
            scores = util.cos_sim(torch.tensor(query_emb), torch.tensor(doc_embs))[0].cpu().tolist()
            doc_score_pairs = sorted([(doc, score) for doc, score in zip(docs, scores) if score >= self.score_threshold], key=lambda x: x[1], reverse=True)
            top_docs = [doc for doc, _ in doc_score_pairs[:self.rerank_top_n]]
            logger.info(f"Reranked {len(docs)} docs -> {len(top_docs)} docs meeting threshold.")
            return top_docs
        except Exception as e:
            logger.error(f"Error during reranking: {e}")
            return docs[:self.rerank_top_n]
        
    def _format_docs_for_context(self, docs: List[LangchainDocument]) -> str:
        if not docs:
            return "No context provided"
        
        formated_parts = []
        for i, doc in enumerate(docs):
            source_path = doc.metadata.get('source', 'Unknown')
            file_name = Path(source_path).name
            page = doc.metadata.get('page', -1) + 1

            formated_parts.append(
                f"--- Document {i + 1} (Source: {file_name}, Page: {page}) ---\n"
                f"{doc.page_content.strip()}"
            )
        
        return "\n\n".join(formated_parts)

    def chat_stream(self, query: str, db: Session) -> Iterator[str]:
        response_text = ""

        try:
            if not query or not query.strip():
                yield "Please provide a valid question."
                return
            
            query = query.strip()

            if not self.retriever or not self.llm:
                yield "Error: System not ready."
                return
            
            retrieved_nodes = self.retriever.retrieve(query)
            initial_docs = [
                LangchainDocument(page_content=node.node.get_content(), metadata=node.node.metadata)
                for node in retrieved_nodes
            ]

            reranked_docs = self._rerank_and_filter_docs(query, initial_docs)

            if not reranked_docs:
                full_response_text = "I don't have enough information to answer this."
                yield full_response_text
                yield f"\n<|SOURCES|>{json.dumps([])}"
                return
            
            context = self._format_docs_for_context(docs=reranked_docs)
            prompt = self.prompt_template.format(context=context, question=query)

            for chunk in self.llm.stream(prompt):
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    response_text += content
                    yield content

            source = []
            sorry_message = "I don't have enough information to answer this."

            if sorry_message.lower() not in full_response_text.lower():
                added_source = set()
                for doc in reranked_docs:
                    raw_path = doc.metadata.get('source', 'Unknow')
                    file_name = Path(raw_path).name
                    page = doc.metadata.get('page', -1) + 1

                    if (file_name, page) not in added_source:
                        source.append({"filename": file_name, "page": page})
                        added_source.add((file_name, page))
                
            yield f"\n|<SOURCE>|{json.dumps(source)}"
                    
        except Exception as e:
            logger.error(f"Error in ask_stream: {e}", exc_info=True)
            yield f"An error occurred: {str(e)}"

