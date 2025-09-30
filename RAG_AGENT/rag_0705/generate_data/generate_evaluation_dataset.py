import json
import os
import random
import time
import argparse

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

import os
from dotenv import load_dotenv
load_dotenv()


# ----------- Argument Parsing ------------
parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=True, help="Start index of documents to process")
parser.add_argument("--end", type=int, required=True, help="End index of documents to process (exclusive)")
parser.add_argument("--api_key", type=str, required=True, help="API key to use for this instance")
parser.add_argument("--output_file", type=str, required=True, help="Output file path (.jsonl)")
args = parser.parse_args()

# Set API key for Google Generative AI dynamically
os.environ["GOOGLE_API_KEY"] = args.api_key

for i in os.environ:
    if "API_KEY" in i or "LANGSMITH" in i:
        print(f"{i} = {os.environ[i]}")


# ----------- Initialization ------------
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
output_parser = JsonOutputParser()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

PERSIST_DIRECTORY = r"C:\Users\Sese\AI_Study_Record\RAG_AGENT\rag_0705\chroma_db"
COLLECTION_NAME = "html_docs"
db = Chroma(
    persist_directory=PERSIST_DIRECTORY,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME,
)

# ----------- QA Generation Functions ------------

def generate_single_doc_qa(doc_id, doc_content, doc_metadata):
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert in generating concise question-answer pairs from text."),
        ("human", r"""
Given the following document content, generate ONE question and its corresponding short, factual answer.
The answer must be directly extractable from the provided document.
The question should be a single-document query.

Provide the output in JSON format: {{"query": "YOUR_QUESTION", "answer": "YOUR_ANSWER"}}
You must not include any additional text or explanations.

Document Content:
'''
{doc_content}
'''
""")
    ])
    chain = prompt_template | llm | output_parser

    try:
        for retry in range(5):
            try:
                response = chain.invoke({"doc_content": doc_content})
                break
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    print(f"429 오류 발생, 10초 후 재시도합니다... ({retry+1}/5)")
                    time.sleep(10)
                else:
                    raise
        if isinstance(response, dict):
            qa_pair = response
        else:
            qa_pair = json.loads(response)

        qa_pair["relevant_ids"] = [doc_id]
        qa_pair["relevant_docs_metadata"] = [doc_metadata]
        return qa_pair
    except Exception as e:
        print(f"단일 문서 QA 생성 실패: {e}")
        return None


def generate_multi_doc_qa(doc_ids, doc_contents, doc_metadatas):
    combined_text = "\n---\n".join(doc_contents)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an expert in generating concise question-answer pairs that require combining information from multiple documents."),
        ("human", """
Given the following document contents, generate ONE question and its corresponding short, factual answer.
The answer must be directly extractable by combining information from at least two of the provided documents.
The question should be a multi-document query.
Provide the output in JSON format: {{"query": "YOUR_QUESTION", "answer": "YOUR_ANSWER"}}
You must not include any additional text or explanations.

Document Contents:
'''
{combined_text}
'''
""")
    ])
    chain = prompt_template | llm | output_parser

    try:
        for retry in range(5):
            try:
                response = chain.invoke({"combined_text": combined_text})
                break
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    print(f"429 오류 발생, 10초 후 재시도합니다... ({retry+1}/5)")
                    time.sleep(10)
                else:
                    raise
        if isinstance(response, dict):
            qa_pair = response
        else:
            qa_pair = json.loads(response)

        qa_pair["relevant_ids"] = doc_ids
        qa_pair["relevant_docs_metadata"] = doc_metadatas
        return qa_pair
    except Exception as e:
        print(f"다중 문서 QA 생성 실패: {e}")
        return None

# ----------- Main Logic ------------

def build_evaluation_dataset(start_idx, end_idx, output_path):
    try:
        data = db.get(include=['documents', 'metadatas'])
        all_ids = data['ids'][start_idx:end_idx]
        all_documents = data['documents'][start_idx:end_idx]
        all_metadatas = data['metadatas'][start_idx:end_idx]
        print(f"[{start_idx}:{end_idx}] 총 {len(all_documents)}개의 문서 로드 완료.")
    except Exception as e:
        print(f"Chroma DB 접근 실패: {e}")
        return

    id_to_content = {all_ids[i]: all_documents[i] for i in range(len(all_ids))}
    id_to_metadata = {all_ids[i]: all_metadatas[i] for i in range(len(all_ids))}

    with open(output_path, 'w', encoding='utf-8') as f_out:
        # 단일 문서 QA
        print("단일 문서 QA 생성 중...")
        single_count = 0
        for doc_id in all_ids:
            qa = generate_single_doc_qa(doc_id, id_to_content[doc_id], id_to_metadata[doc_id])
            if qa:
                json.dump(qa, f_out, ensure_ascii=False)
                f_out.write('\n')
                f_out.flush()
                single_count += 1
        print(f"단일 문서 QA 생성 완료: {single_count}개")

        # 다중 문서 QA
        print("다중 문서 QA 생성 중...")
        multi_count = 0
        num_multi_doc_queries = min(50, len(all_ids) // 2)

        for _ in range(num_multi_doc_queries):
            num_docs = random.choice([2, 3])
            if len(all_ids) < num_docs:
                continue
            selected_ids = random.sample(all_ids, num_docs)
            contents = [id_to_content[i] for i in selected_ids]
            metas = [id_to_metadata[i] for i in selected_ids]
            qa = generate_multi_doc_qa(selected_ids, contents, metas)
            if qa:
                json.dump(qa, f_out, ensure_ascii=False)
                f_out.write('\n')
                f_out.flush()
                multi_count += 1
        print(f"다중 문서 QA 생성 완료: {multi_count}개")

    print(f"총 {single_count + multi_count}개 QA 쌍을 '{output_path}'에 저장했습니다.")

# ----------- Entry Point ------------
if __name__ == "__main__":
    build_evaluation_dataset(args.start, args.end, args.output_file)
