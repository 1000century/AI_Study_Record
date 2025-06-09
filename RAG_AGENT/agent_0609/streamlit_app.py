# streamlit_app.py
import streamlit as st
from pdf_tools import open_pdf, get_page_content, add_toc_entry, get_toc, save_doc, PDFDocument, pdf_documents
import tempfile
from openai import OpenAI
import os
import json
import logging
import uuid

# 🔹 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(page_title="PDF TOC Generator", layout="centered")
st.title("📄 GPT 기반 PDF 목차 추가")

# 세션 초기화
st.session_state.setdefault("doc_id", None)
st.session_state.setdefault("file_path", None)

# 🔹 1. PDF 업로드
uploaded_file = st.file_uploader("PDF 파일 업로드", type=["pdf"])
if uploaded_file and st.session_state.file_path is None:
    os.makedirs("uploaded_pdfs", exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
    save_path = os.path.join("uploaded_pdfs", unique_filename)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    tmp_path = save_path
    logger.info(f"PDF uploaded: {tmp_path}")
    result = open_pdf(tmp_path)
    if result["status"] == "success":
        st.session_state.doc_id = result["doc_id"]
        st.session_state.file_path = tmp_path
        logger.info(f"PDF opened successfully: doc_id={result['doc_id']}, pages={result['page_count']}")
        st.success(f"PDF 열기 완료! 총 {result['page_count']} 페이지")
    else:
        logger.error(f"Failed to open PDF: {result['message']}")
        st.error(result["message"])

doc_id = st.session_state.doc_id

if doc_id:
    st.divider()
    st.header("🧠 GPT에게 자연어 명령으로 목차 추가시키기")

    user_cmd = st.text_input("예: '5페이지에 서론 추가해줘'", key="natural_input")
    if st.button("GPT에게 명령 실행"):
        logger.info(f"User GPT command input: {user_cmd}")
        logger.info(f"Using doc_id: {doc_id}")
        prompt = f"""
다음은 사용자의 지시입니다. 적절히 해석하여 add_toc_entry(doc_id, level, title, page)를 호출하십시오.

- 항상 level=1로 처리하세요.
- title은 20자 이내로 요약된 제목으로 만들어주세요.
- 반드시 정수 페이지 번호가 포함되어야 합니다.

사용자 입력: {user_cmd}
doc_id는 "{doc_id}"입니다.
"""
        tools = [{
            "type": "function",
            "name": "add_toc_entry",
            "description": "PDF에 목차 항목을 추가합니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "level": {"type": "integer"},
                    "title": {"type": "string"},
                    "page": {"type": "integer"},
                },
                "required": ["doc_id", "level", "title", "page"]
            }
        }]
        response = client.responses.create(
            model="gpt-4o",
            input=[{"role": "user", "content": prompt}],
            tools=tools
        )

        tool_call = response.output[0]
        if tool_call.name == 'add_toc_entry':
            logger.info("GPT parsed TOC addition command successfully.")
            st.write("GPT가 명령을 이해했습니다. 실행 중...")
            args = json.loads(tool_call.arguments)
            logger.info(f"TOC Entry args: {args}")
            result = add_toc_entry(**args)
            if result["status"] == "success":
                st.success(f"추가 완료: {args['title']} (p.{args['page']})")
            else:
                logger.error(f"Failed to add TOC: {result['message']}")
                st.error(result["message"])
        else:
            logger.warning("GPT failed to parse the command.")
            st.warning("GPT가 명령을 이해하지 못했어요.")

    st.divider()
    st.header("🤖 페이지 읽기")

    page_num = st.number_input("페이지 번호 선택", min_value=1, step=1)
    if st.button("페이지 읽기"):
        logger.info(f"User requested OCR for page {page_num}")
        with st.spinner("페이지 내용 OCR 중..."):
            result = get_page_content(doc_id, page_num, use_ocr=True)
        if result["status"] == "success":
            content = result["content"]
            logger.info(f"OCR success on page {page_num}")
            st.success(f"페이지 내용: {content}")
        else:
            logger.error(f"OCR failed on page {page_num}: {result['message']}")
            st.error(result["message"])

    st.divider()
    st.header("📑 현재 목차 보기")
    toc_result = get_toc(doc_id)
    if toc_result["status"] == "success":
        logger.info("TOC retrieved successfully.")
        for entry in toc_result["toc"]:
            st.markdown(f"- Level {entry[0]} | Page {entry[2]} | **{entry[1]}**")
    else:
        logger.error("Failed to retrieve TOC.")
        st.error("TOC를 불러오는 데 실패했습니다.")

    # ✅ 최종 PDF 다운로드 버튼
    if st.session_state.file_path and os.path.exists(st.session_state.file_path):
        
        download_name = os.path.basename(st.session_state.file_path)
        
        # PDF 저장 후 다운로드 버튼
        st.divider()
        st.header("📥 수정된 PDF 다운로드")

        if st.button("📁 PDF 저장 및 다운로드 준비"):
            # 1. 저장 실행
            message = save_doc(doc_id)
            save_path = message["file_path"]
            
            if not save_path.endswith(".pdf"):
                save_path += ".pdf"

            download_name = f"modified_{os.path.basename(save_path)}"
            logger.info(f"Document saved successfully: {download_name}")

            # 2. 파일 열기 → 메모리에 읽어두기
            with open(save_path, "rb") as f:
                file_bytes = f.read()

            # 3. 다운로드 버튼 출력 (메모리에서 바로 다운로드)
            st.download_button(
                label="📥 다운로드 시작",
                data=file_bytes,
                file_name=download_name,
                mime="application/pdf"
            )



    # ✅ 현재 PDF 상태 표시
    st.divider()
    st.subheader("📌 현재 세션 상태")

    file_name = os.path.basename(st.session_state.file_path) if st.session_state.file_path else "없음"
    st.markdown(f"""
    - **파일명**: `{file_name}`
    - **doc_id**: `{doc_id}`
    - **현재 목차 개수**: `{len(get_toc(doc_id).get('toc', []))}`
    """)
