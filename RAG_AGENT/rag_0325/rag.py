import os, sys
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.retrievers.ensemble import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_openai import OpenAIEmbeddings
from langchain_community.callbacks.manager import get_openai_callback

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma

class RetrievalChain():
    
    def __init__(self, **kwargs) -> None:
        
        self.source_url = kwargs.get("source_url", [])
        self.k = kwargs.get("k", 5)
        self.embedding_model = kwargs.get("embedding_model", "text-embedding-3-small")
        self.persist_directory = kwargs.get("persist_directory", "None")
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.split_docs = None
        
    """def load_documents(self, source_uris: List[str]) -> List[Document]:
        docs = []
        for source_uri in source_uris:
            if not os.path.exists(source_uri):
                print(f"File not found: {source_uri}")
                continue
                
            print(f"Loading PDF: {source_uri}")
            loader = PDFPlumberLoader(source_uri)
            docs.extend(loader.load())
        
        return docs """

    def load_documents(self, source_uris: List[str]) -> List[Document]:
        docs = []
        for source_uri in source_uris:
            if not os.path.exists(source_uri):
                print(f"File not found: {source_uri}")
                continue
                
            print(f"Loading HTML: {source_uri}")
            loader = UnstructuredHTMLLoader(source_uri)
            docs.extend(loader.load())
        
        return docs

       
    def create_text_splitter(self) -> RecursiveCharacterTextSplitter:
        return RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=50
        )
    
    def split_documents(self, docs: List[Document], text_splitter: Any) -> List[Document]:
        return text_splitter.split_documents(docs)
    
    def create_embedding(self) -> Any:

        return OpenAIEmbeddings(model=self.embedding_model)
    
    def create_vectorstore(self, split_docs: List[Document]) -> Any:
        if not split_docs:
            raise ValueError("No split documents available.")
            
        if self.persist_directory:
            os.makedirs(self.persist_directory, exist_ok=True)
            
            if os.path.exists(self.persist_directory) and any(os.listdir(self.persist_directory)):
                print(f"Loading existing vector store: {self.persist_directory}")

                return Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.create_embedding()
                )
        
        print("Creating new vector store...")

        with get_openai_callback() as cb:

            vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=self.create_embedding(),
                persist_directory=self.persist_directory
            )
            # 어차피 chat_model에서만 출력가능

        return vectorstore 
       
    def create_semantic_retriever(self, vectorstore: Any) -> BaseRetriever:
        return vectorstore.as_retriever(
            search_kwargs={"k": self.k}
        )
    
    def create_keyword_retriever(self, split_docs: List[Document]) -> BaseRetriever:
        return BM25Retriever.from_documents(split_docs, k=self.k)
    
    def create_hybrid_retriever(self, split_docs: List[Document], vectorstore: Any) -> BaseRetriever:
        bm25_retriever = self.create_keyword_retriever(split_docs)
        dense_retriever = self.create_semantic_retriever(vectorstore)
        
        return EnsembleRetriever(
            retrievers=[bm25_retriever, dense_retriever],
            weights=[0.5, 0.5]
        )
    
    def create_retrievers(self, split_docs: List[Document]) -> Dict[str, BaseRetriever]:
        self.embeddings = self.create_embedding()
        self.vectorstore = self.create_vectorstore(split_docs)
        
        return {
            "semantic": self.create_semantic_retriever(self.vectorstore),
            "keyword": self.create_keyword_retriever(split_docs),
            "hybrid": self.create_hybrid_retriever(split_docs, self.vectorstore)
        }
    
    def initialize(self) -> "RetrievalChain":
        docs = self.load_documents(self.source_url)
        if not docs:
            print("No documents found. Exiting.")
            return self

        text_splitter = self.create_text_splitter()
        self.split_docs = self.split_documents(docs, text_splitter)
        
        self.retrievers = self.create_retrievers(self.split_docs)
        print("Retrievers initialized.")
        return self
        
    
    def search_semantic(self, query:str, k:Optional[int]=None) -> List[Document]:
        if not hasattr(self, "retrievers") or self.retrievers is None:
            raise ValueError("Retrievers not initialized. Please call initialize() first.")
    
        k = k or self.k
        retriever = self.retrievers["semantic"]
        retriever.search_kwargs['k'] = k
        
        return retriever.get_relevant_documents(query)
    
    def search_keyword(self, query:str, k:Optional[int]=None) -> List[Document]:
        if not hasattr(self, "retrievers") or self.retrievers is None:
            raise ValueError("Retrievers not initialized. Please call initialize() first.")
        return self.retrievers['keyword'].get_relevant_documents(query)
    
    def search_hybrid(self, query:str, k:Optional[int]=None) -> List[Document]:
        if not hasattr(self, "retrievers") or self.retrievers is None:
            raise ValueError("Retrievers not initialized. Please call initialize() first.")
        return self.retrievers['hybrid'].get_relevant_documents(query)
    
    def search(self, query:str, k:Optional[int]=None) -> List[Document]:
        return self.search_semantic(query,k)