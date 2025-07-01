from rag.base import RetrievalChain
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from operator import itemgetter
from langchain_openai import ChatOpenAI


class ChromaRetrievalChain(RetrievalChain):
    def __init__(self, persist_directory: str, **kwargs):
        super().__init__(**kwargs)
        self.persist_directory = persist_directory
        self.k = kwargs.get("k", 5)

    def load_documents(self, source_uris):
        return []  # 무시됨

    def create_text_splitter(self):
        return None  # 무시됨

    def create_vectorstore(self, split_docs=None):
        print(f"[DEBUG] Loading Chroma from: {self.persist_directory}")
        vectorstore = Chroma(
            collection_name="html_docs",
            persist_directory=self.persist_directory,
            embedding_function=self.create_embedding()
        )
        print(f"[DEBUG] Vectorstore collection size: {len(vectorstore.get()["documents"])}")
        return vectorstore


    def create_chain(self):
        self.vectorstore = self.create_vectorstore()
        self.retriever = self.create_retriever(self.vectorstore)
        model = self.create_model()
        prompt = self.create_prompt()

        self.chain = (
            {
                "question": itemgetter("question"),
                "context": itemgetter("context"),
                "chat_history": itemgetter("chat_history"),
            }
            | prompt
            | model
            | StrOutputParser()
        )
        return self
