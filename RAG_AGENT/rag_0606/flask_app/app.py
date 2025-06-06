from flask import Flask, request, render_template, send_from_directory, abort
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
import os, dotenv, json
from datetime import datetime

# ✅ 환경 변수 로드
dotenv.load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Flask 앱 초기화
app = Flask(__name__)

# ✅ 벡터 DB 및 LLM 설정
embedding = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=API_KEY,
)

vectordb_path = os.getenv("VECTORDB_PATH", "vectordb")

vectorstore = Chroma(
    collection_name="html_docs",
    persist_directory=vectordb_path,
    embedding_function=embedding,
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    api_key=GEMINI_API_KEY,
)

# ✅ 파일 서빙을 위한 루트 경로
LOCAL_FILE_BASE = os.getenv("LOCAL_FILE_BASE", "")

# ✅ 로그 저장 위치
LOG_PATH = os.getenv("LOG_PATH", "query_log.json")

# ✅ 문서 context 출력 + 링크 생성
def get_context(docs, max_length=2000):
    context_chunks = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        content = doc.page_content[:max_length]
        filename = os.path.basename(source)

        try:
            relative_path = os.path.relpath(source, LOCAL_FILE_BASE)
            url = f"/view/{relative_path.replace(os.sep, '/')}"
            link = f'<a href="{url}" target="_blank">{filename}</a>'
        except Exception:
            link = filename

        context_chunks.append(
            f"<b>{i+1}. {link}</b><br><div style='white-space:pre-wrap'>{content}</div><hr>"
        )
    return "\n".join(context_chunks)

# ✅ 메인 페이지 (질의 입력)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        query = request.form["query"]
        docs = retriever.invoke(query)
        context_text = get_context(docs)

        context_only = "\n".join([doc.page_content[:2000] for doc in docs])
        prompt = f"""
You are an expert in the field of computer science. Based on the following context, please answer the question:

Context:
{context_only}

Question: {query}

Answer:
"""
        answer = llm.invoke(prompt).content.strip()

        # ✅ 로그 저장
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "answer": answer,
            "context": context_text,
        }
        save_log(log_entry)

        return render_template("result.html", query=query, context=context_text, answer=answer)

    return render_template("index.html")

# ✅ 기록 보기
@app.route("/history")
def history():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    else:
        log_data = []
    return render_template("history.html", logs=reversed(log_data))

# ✅ 로컬 HTML 파일 서빙
@app.route("/view/<path:subpath>")
def view_local_file(subpath):
    try:
        return send_from_directory(LOCAL_FILE_BASE, subpath)
    except FileNotFoundError:
        return abort(404)

# ✅ 로그 저장 함수
def save_log(entry):
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ 실행
if __name__ == "__main__":
    app.run(debug=True)
