import sqlite3
import json
from langchain_chroma import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Chroma 벡터스토어 로딩
vectorstore = Chroma(
    collection_name="html_docs",
    persist_directory=r"C:\Users\Sese\AI_Study_Record\RAG_AGENT\rag_0608\chroma_db",
    embedding_function=HuggingFaceEmbeddings()
)

# 벡터 + 텍스트 + 메타데이터 추출
data = vectorstore.get(include=["documents", "embeddings"])
texts = data["documents"]
embeddings = data["embeddings"]

# 새 SQLite DB 생성
conn = sqlite3.connect("documents.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS documents")
cursor.execute("""
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    embedding TEXT
)
""")

# 데이터 삽입
# 데이터 삽입
records = [(text, json.dumps(embedding.tolist())) for text, embedding in zip(texts, embeddings)]
cursor.executemany("INSERT INTO documents (text, embedding) VALUES (?, ?)", records)
conn.commit()
conn.close()

print(f"✅ 총 {len(records)}개의 문서를 documents.db에 저장 완료")
