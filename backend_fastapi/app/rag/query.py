from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema.retriever import BaseRetriever
from langchain.schema.document import Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from typing import List, Dict, Any
from app.db.client import chroma_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChromaRetriever(BaseRetriever):
    """Custom retriever for ChromaDB integration with LangChain"""
    
    def __init__(self, chroma_client, k: int = 5):
        super().__init__()
        self.chroma_client = chroma_client
        self.k = k
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Retrieve relevant documents from ChromaDB"""
        try:
            results = self.chroma_client.query_documents(query, n_results=self.k)
            
            if not results or not results.get('documents'):
                return []
            
            documents = []
            for i, doc_text in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                documents.append(Document(
                    page_content=doc_text,
                    metadata=metadata
                ))
            
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

class RAGQueryEngine:
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self.retriever = None
        self.qa_chain = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LLM, embeddings, and retriever"""
        try:
            # Initialize Ollama LLM
            self.llm = OllamaLLM(
                base_url=settings.ollama_url,
                model=settings.ollama_model,
                temperature=0.7
            )
            
            # Initialize Ollama embeddings
            self.embeddings = OllamaEmbeddings(
                base_url=settings.ollama_url,
                model=settings.ollama_model
            )
            
            # Initialize retriever
            self.retriever = ChromaRetriever(chroma_client, k=5)
            
            # Create QA chain
            self._create_qa_chain()
            
            logger.info("RAG components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG components: {e}")
            raise
    
    def _create_qa_chain(self):
        """Create the RetrievalQA chain with custom prompt"""
        
        # Custom prompt template for Airbnb customer service
        prompt_template = """
        You are a helpful customer service assistant for an Airbnb-style accommodation platform. 
        Use the following context to answer the user's question in a friendly, professional manner.
        
        Context: {context}
        
        Question: {question}
        
        Guidelines:
        - Be helpful and empathetic
        - Provide specific, actionable advice when possible
        - If you don't know something, acknowledge it and suggest next steps
        - Keep responses concise but comprehensive
        - Use a warm, professional tone
        
        Answer:
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    def query(self, question: str, user_id: str = None) -> Dict[str, Any]:
        """Process a query through the RAG pipeline"""
        try:
            if not self.qa_chain:
                raise Exception("QA chain not initialized")
            
            # Execute the query
            result = self.qa_chain({"query": question})
            
            # Extract response and sources
            response = result.get("result", "I'm sorry, I couldn't generate a response.")
            source_documents = result.get("source_documents", [])
            
            # Format sources for response
            sources = []
            for doc in source_documents:
                sources.append({
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                })
            
            return {
                "response": response,
                "sources": sources,
                "user_id": user_id,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": "I'm sorry, I'm experiencing technical difficulties. Please try again later.",
                "sources": [],
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of RAG components"""
        try:
            # Test query to check if everything is working
            test_result = self.query("Hello, how can you help me?")
            
            return {
                "status": "healthy",
                "llm_model": settings.ollama_model,
                "ollama_url": settings.ollama_url,
                "test_query_successful": test_result.get("status") == "success"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global query engine instance
rag_query_engine = RAGQueryEngine()