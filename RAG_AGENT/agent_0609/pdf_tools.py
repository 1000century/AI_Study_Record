# pdf_tools.py

import fitz  # PyMuPDF
import easyocr
import uuid
import os
import logging
import numpy as np
from PIL import Image
import io
from typing import Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_ocr_reader = None
pdf_documents = {}

def get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(['ko', 'en'])
    return _ocr_reader

class PDFDocument:
    def __init__(self, file_path: str):
        self.doc = fitz.open(file_path)
        self.file_path = file_path
        self.metadata = self.doc.metadata
        self.page_count = len(self.doc)

    def get_toc(self):
        return self.doc.get_toc()

    def add_toc_entry(self, level: int, title: str, page: int):
        toc = self.doc.get_toc()  # ✅ 항상 최신 TOC 기준으로 동작
        toc.append([level, title, page])
        toc.sort(key=lambda x: x[2])  # 페이지 기준 정렬
        self.doc.set_toc(toc)

    def get_page(self, page_num: int):
        if 1 <= page_num <= self.page_count:
            return self.doc[page_num - 1]
        raise ValueError("Invalid page number")

    def page_to_image(self, page):
        pix = page.get_pixmap(dpi=300)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        return np.array(img)

    def get_page_text(self, page_num: int, use_ocr: bool = False) -> str:
        page = self.get_page(page_num)
        text = page.get_text()
        if text.strip() and not use_ocr:
            return text
        img = self.page_to_image(page)
        result = get_ocr_reader().readtext(img)
        return " ".join([r[1] for r in result])

    def save_diff(self, output_path=None) -> str:
        if output_path is None:
            output_path = self.file_path.replace('.pdf', '_diff.pdf')
        output_path = output_path[:-4]+'_diff.pdf'
        self.doc.save(output_path)
        return output_path
    
    # def save_incrementally(self, output_path: str):
    #     self.doc.save(output_path, incremental=False, encryption=fitz.PDF_ENCRYPT_KEEP)

    def close(self):
        self.doc.close()

def open_pdf(file_path: str) -> Dict:
    logger.info(f'[함수 open_pdf] {file_path} 열기 시도')
    for doc_id, doc in pdf_documents.items():
        logger.info(f'[함수 open_pdf] 현재 열려있는 문서: {doc_id}, 페이지 수: {doc.page_count}')
    if not os.path.exists(file_path):
        return {"status": "error", "message": "File not found."}
    doc_id = str(uuid.uuid4())
    pdf_documents[doc_id] = PDFDocument(file_path)
    return {
        "status": "success",
        "doc_id": doc_id,
        "page_count": pdf_documents[doc_id].page_count,
    }

def get_page_content(doc_id: str, page_num: int, use_ocr: bool = True) -> Dict:
    doc = pdf_documents.get(doc_id)
    if not doc:
        return {"status": "error", "message": "Invalid doc_id"}
    try:
        content = doc.get_page_text(page_num, use_ocr)
        return {"status": "success", "content": content}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def add_toc_entry(doc_id: str, level: int, title: str, page: int) -> Dict:
    logger.info(f'[함수 add_toc_entry] 현재 열려있는 문서 개수 {len(pdf_documents)}개')
    for doc_id, doc in pdf_documents.items():
        logger.info(f'[함수 add_toc_entry] 문서 ID: {doc_id}, 페이지 수: {doc.page_count}')
    doc = pdf_documents.get(doc_id)
    if not doc:
        return {"status": "error", "message": "Invalid doc_id"}
    try:
        doc.add_toc_entry(level, title, page)
        doc.save_diff(output_path = None)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_toc(doc_id: str) -> Dict:
    doc = pdf_documents.get(doc_id)
    if not doc:
        return {"status": "error", "message": "Invalid doc_id"}
    return {"status": "success", "toc": doc.get_toc()}

def save_doc(doc_id: str) -> Dict:
    doc = pdf_documents.get(doc_id)
    if not doc:
        return {"status": "error", "message": "Invalid doc_id"}
    try:
        save_path = doc.save_diff(output_path=None)
        return {"status": "success", "file_path": save_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}