import logging
from flask import Flask, render_template_string, redirect, url_for, request, session
import os
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key'

folder_path = "html_files"
docs = []
vectorstore = None

# 문서 로딩 및 임베딩
def load_documents(api_key):
    global docs, vectorstore
    docs.clear()
    documents = []

    logger.info("OpenAI API 키 설정됨")
    logger.info(f"폴더 내 HTML 파일 로드 중: {folder_path}")

    for idx,file_name in enumerate(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, file_name)
        if idx %100==0:
            logger.info(f"{idx} 파일 로딩: {file_path}")

        loader = UnstructuredHTMLLoader(file_path)
        data = loader.load()

        chap = data[0].page_content.split('\n')[0].split('##')[0]
        remove_first_line = '\n'.join(data[0].page_content.split('\n')[1:])
        final_content = f"단원명: {chap}\n\n{remove_first_line}"

        docs.append({"filename": file_name, "content": final_content})
        documents.append(Document(page_content=final_content, metadata={"filename": file_name}))

    logger.info(f"총 로딩된 문서 수: {len(documents)}")

    embedding = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=api_key)
    vectorstore = Chroma(
        collection_name="medical",
        embedding_function=embedding,
        persist_directory="chroma_db"
    )

    all_ids = vectorstore.get().get('ids', [])
    if all_ids:
        logger.info(f"기존 문서 ID {len(all_ids)}개 삭제")
        vectorstore.delete(ids=all_ids)

    logger.info("문서 벡터 임베딩 및 저장 중...")
    for i in range(0, len(documents), 100):
        vectorstore.add_documents(documents[i:i + 100])
        logger.info(f"문서 {i + 1}~{min(i + 100, len(documents))} 저장 완료")

    logger.info("문서 임베딩 완료 및 저장 완료!")

# 홈 페이지
@app.route('/', methods=['GET', 'POST'])
def show_docs():
    if request.method == 'POST':
        session['api_key'] = request.form['api_key']
        load_documents(session['api_key'])
        return redirect(url_for('show_docs'))

    api_key = session.get('api_key')
    html = """
    <html><head><title>문서 보기</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .doc-link { margin-bottom: 10px; }
    </style></head>
    <body>
    <h1>문서 목록</h1>
    {% if not api_key %}
        <form method="post">
            <label>OpenAI API 키 입력:</label><br>
            <input type="password" name="api_key" required>
            <button type="submit">적용</button>
        </form>
    {% else %}
        <form action="{{ url_for('search') }}" method="get">
            <input type="text" name="query" placeholder="검색어 입력" required>
            <button type="submit">검색</button>
        </form>
        <ul>
        {% for doc in docs %}
            <li class="doc-link">
                <a href="{{ url_for('view_doc', doc_id=loop.index0) }}">
                    문서 {{ loop.index }}: {{ doc.filename }}
                </a>
            </li>
        {% endfor %}
        </ul>
    {% endif %}
    </body></html>
    """
    return render_template_string(html, docs=docs, api_key=api_key)

# 문서 상세 보기
@app.route('/doc/<int:doc_id>')
def view_doc(doc_id):
    if doc_id < 0 or doc_id >= len(docs):
        return "문서를 찾을 수 없습니다.", 404

    doc = docs[doc_id]
    html = """
    <html><head><title>문서 상세</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .content { white-space: pre-wrap; }
        a { display: inline-block; margin-bottom: 20px; }
    </style></head>
    <body>
    <a href="{{ url_for('show_docs') }}">← 문서 목록으로 돌아가기</a>
    <h2>문서 {{ doc_id + 1 }}: {{ doc.filename }}</h2>
    <div class="content">{{ doc.content }}</div>
    </body></html>
    """
    return render_template_string(html, doc=doc, doc_id=doc_id)

# 검색 기능
@app.route('/search')
def search():
    query = request.args.get('query', '')
    api_key = session.get('api_key')

    if not query or not vectorstore or not api_key:
        return redirect(url_for('show_docs'))

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    results = retriever.invoke(query)

    logger.info(f"검색 수행: \"{query}\" → 결과 {len(results)}건")

    html = """
    <html><head><title>검색 결과</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .content { white-space: pre-wrap; margin-bottom: 30px; }
        a { display: inline-block; margin-bottom: 10px; }
    </style></head>
    <body>
    <a href="{{ url_for('show_docs') }}">← 문서 목록으로 돌아가기</a>
    <h2>검색 결과: "{{ query }}"</h2>
    {% for res in results %}
        <div class="content">
            {{ res.page_content }}
            {% if res.metadata.filename %}
                <br><a href="{{ url_for('view_original') }}?filename={{ res.metadata.filename }}">
                    → 원본 HTML 보기 ({{ res.metadata.filename }})
                </a>
            {% endif %}
        </div>
        <hr>
    {% endfor %}
    </body></html>
    """
    return render_template_string(html, results=results, query=query)

# 원본 HTML 보기 (iframe 없이 직접 렌더링)
@app.route('/original')
def view_original():
    filename = request.args.get("filename")
    if not filename:
        return "파일명이 지정되지 않았습니다.", 400

    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        return "원본 파일을 찾을 수 없습니다.", 404

    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    return render_template_string(f"""
    <html><head>
        <title>원본 HTML</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; padding: 20px; }}
        </style>
    </head>
    <body>
        <a href="{{{{ url_for('show_docs') }}}}">← 문서 목록</a><br>
        <a href="{{{{ url_for('search', query='') }}}}">← 검색 결과로 돌아가기</a>
        <h2>파일: {filename}</h2>
        <hr>
        {{% raw %}}
        {html_content}
        {{% endraw %}}
    </body></html>
    """)
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
