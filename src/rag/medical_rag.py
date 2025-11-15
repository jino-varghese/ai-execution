"""
Medical RAG (Retrieval Augmented Generation) System
Handles knowledge retrieval from medical literature, drug databases, and clinical trials.
"""

import os
from typing import List, Dict, Optional
import logging

# Vector database and embeddings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader, PDFLoader

logger = logging.getLogger(__name__)


class MedicalRAG:
    """
    RAG system for retrieving medical knowledge from various sources.
    """

    def __init__(self, config: Dict):
        """
        Initialize the Medical RAG system.

        Args:
            config: RAG configuration dictionary
        """
        self.config = config

        # Initialize embedding model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config['embedding_model']
        )

        # Initialize vector databases for different knowledge sources
        self.vector_stores = {}
        self._initialize_vector_stores()

        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config['chunk_size'],
            chunk_overlap=config['chunk_overlap'],
            length_function=len,
        )

        logger.info("Medical RAG system initialized successfully")

    def _initialize_vector_stores(self):
        """Initialize vector stores for each knowledge source"""

        for source_name, source_path in self.config['knowledge_sources'].items():
            persist_directory = f"./data/vector_db/{source_name}"

            # Create or load vector store
            try:
                self.vector_stores[source_name] = Chroma(
                    collection_name=source_name,
                    embedding_function=self.embeddings,
                    persist_directory=persist_directory
                )
                logger.info(f"Loaded vector store for {source_name}")
            except Exception as e:
                logger.warning(f"Could not load vector store for {source_name}: {e}")
                # Will be created when documents are indexed

    def index_documents(self, source_name: str, documents_path: str):
        """
        Index documents from a directory into the vector store.

        Args:
            source_name: Name of the knowledge source
            documents_path: Path to documents directory
        """
        logger.info(f"Indexing documents from {documents_path} for {source_name}")

        try:
            # Load documents
            loader = DirectoryLoader(
                documents_path,
                glob="**/*.{txt,pdf,md}",
                loader_cls=TextLoader,
                show_progress=True
            )
            documents = loader.load()

            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)

            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")

            # Create vector store
            persist_directory = f"./data/vector_db/{source_name}"
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                collection_name=source_name,
                persist_directory=persist_directory
            )

            self.vector_stores[source_name] = vector_store

            logger.info(f"Successfully indexed {source_name}")

        except Exception as e:
            logger.error(f"Error indexing documents for {source_name}: {e}")
            raise

    def retrieve(
        self,
        query: str,
        source_names: Optional[List[str]] = None,
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents based on query.

        Args:
            query: Search query
            source_names: List of source names to search (None = all sources)
            top_k: Number of results to return

        Returns:
            List of relevant documents with metadata
        """
        if top_k is None:
            top_k = self.config['top_k']

        if source_names is None:
            source_names = list(self.vector_stores.keys())

        all_results = []

        for source_name in source_names:
            if source_name not in self.vector_stores:
                logger.warning(f"Source {source_name} not found in vector stores")
                continue

            try:
                vector_store = self.vector_stores[source_name]
                results = vector_store.similarity_search_with_score(
                    query,
                    k=top_k
                )

                for doc, score in results:
                    # Only include results above similarity threshold
                    if score >= self.config['similarity_threshold']:
                        all_results.append({
                            'source': source_name,
                            'content': doc.page_content,
                            'metadata': doc.metadata,
                            'score': score
                        })

            except Exception as e:
                logger.error(f"Error retrieving from {source_name}: {e}")

        # Sort by score and return top_k
        all_results.sort(key=lambda x: x['score'], reverse=True)
        return all_results[:top_k]

    def search_drug_database(self, drug_name: str) -> Dict:
        """
        Search drug database for information about a specific drug.

        Args:
            drug_name: Name of the drug

        Returns:
            Drug information including interactions, contraindications, dosage
        """
        query = f"drug information for {drug_name} including contraindications, interactions, and dosage"

        results = self.retrieve(
            query=query,
            source_names=['drug_databases'],
            top_k=5
        )

        return {
            'drug_name': drug_name,
            'information': results
        }

    def search_clinical_trials(self, condition: str) -> List[Dict]:
        """
        Search for relevant clinical trials for a medical condition.

        Args:
            condition: Medical condition or disease

        Returns:
            List of relevant clinical trials
        """
        query = f"clinical trials for {condition}"

        results = self.retrieve(
            query=query,
            source_names=['clinical_trials'],
            top_k=10
        )

        return results

    def get_treatment_guidelines(self, diagnosis: str) -> List[Dict]:
        """
        Retrieve treatment guidelines for a specific diagnosis.

        Args:
            diagnosis: Medical diagnosis

        Returns:
            Relevant treatment guidelines
        """
        query = f"treatment guidelines and protocols for {diagnosis}"

        results = self.retrieve(
            query=query,
            source_names=['medical_literature', 'treatment_guidelines'],
            top_k=5
        )

        return results

    def search_medical_literature(self, topic: str) -> List[Dict]:
        """
        Search medical literature on a specific topic.

        Args:
            topic: Medical topic or research area

        Returns:
            Relevant medical literature and research papers
        """
        results = self.retrieve(
            query=topic,
            source_names=['medical_literature'],
            top_k=10
        )

        return results

    def hybrid_search(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Perform hybrid search across all knowledge sources with optional filters.

        Args:
            query: Search query
            filters: Optional metadata filters

        Returns:
            Comprehensive search results from all sources
        """
        results = self.retrieve(query=query)

        # Apply filters if provided
        if filters:
            filtered_results = []
            for result in results:
                match = True
                for key, value in filters.items():
                    if result['metadata'].get(key) != value:
                        match = False
                        break
                if match:
                    filtered_results.append(result)
            return filtered_results

        return results
