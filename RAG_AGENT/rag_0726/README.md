# Graph RAG 주식데이터 분석 시스템

그래프 기반 RAG(Retrieval-Augmented Generation) 시스템을 사용하여 주식 데이터를 분석하는 프로젝트입니다. 주식 종목 데이터를 그래프 형태로 구조화하고 임베딩을 활용해 유사도 기반 검색을 구현했습니다.

## 프로젝트 개요

- **데이터**: 850개 주식 종목 (종목코드, 종목명, 발행형태, 시장구분, 주식종류, 업종 분류)
- **기술 스택**: NetworkX, OpenAI Embeddings, scikit-learn
- **임베딩 모델**: text-embedding-3-small
- **그래프 구조**: 6,050개 노드, 413,221개 엣지
  - COMPANY 노드: 850개
  - RELATION 노드: 5,100개
  - CATEGORY 노드: 100개

## 목차

- 데이터 로드 및 초기 설정
- 필요한 라이브러리 임포트
- 그래프 구조 생성 함수
- 임베딩 생성 및 그래프 엣지 생성 함수
- 시스템 구축 및 저장
- 쿼리 테스트 및 결과 분석

## 1. 데이터 로드 및 초기 설정

먼저 OpenAI API를 사용하기 위해 API 키를 설정하고, 엑셀 파일에서 주식 데이터를 불러옵니다. 데이터에는 종목코드, 종목명, 발행형태, 시장구분, 주식종류, 그리고 업종 분류(대분류, 중분류, 소분류) 정보가 포함되어 있습니다.

```python
# API 키 설정 (보안을 위해 일부를 가렸습니다)
OPENAI_API_KEY = "sk-proj-8jw0i1Pn0RspqPQwNEFcIpQ7EVFXGyrO_S_..."
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# 파일에서 주식 데이터 로드
import pandas as pd
excel_file_path = r"C:\Users\Sese\Downloads\주식종목전체검색.xlsx"
df = pd.read_excel(excel_file_path)
print(f"데이터 로드 완료: {len(df)}개 종목")

# 업종 관련 데이터 처리
industry_cols = ['업종(대분류)', '업종(중분류)', '업종(소분류)']
for col in industry_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')
```

## 2. 필요한 라이브러리 임포트

그래프 기반 RAG 시스템을 구축하기 위해 다양한 라이브러리를 임포트합니다. NetworkX는 그래프 구조를 관리하고, OpenAI API를 통해 텍스트 임베딩을 생성하며, cosine_similarity를 통해 유사도를 계산합니다.

```python
import pandas as pd
import numpy as np
from openai import OpenAI
import networkx as nx
from typing import List, Dict, Tuple, Set
import pickle
import json
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import logging

client = OpenAI(api_key=OPENAI_API_KEY)
model_name: str = "text-embedding-3-small"
model_name = model_name
graph = nx.Graph()
embeddings = {}
text_to_key = {}
key_to_text = {}
company_data = {}
```

## 3. 그래프 구조 생성 함수

주식 데이터를 그래프 구조로 변환하는 함수를 정의합니다. 회사, 업종, 시장 등의 관계를 텍스트로 표현하고 키를 생성합니다.

```python
def build_graph_structure(data: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """그래프 구조 및 텍스트 생성"""
    company_texts = []
    company_keys = []
    
    for _, row in data.iterrows():
        company_code = row['종목코드']
        company_name = row['종목명']
        
        # 회사 데이터 저장
        company_data[company_name] = {
            '종목코드': company_code,
            '종목명': company_name,
            '발행형태': row['발행형태'],
            '시장구분': row['시장구분'],
            '주식종류': row['주식종류'],
            '업종(대분류)': row['업종(대분류)'],
            '업종(중분류)': row['업종(중분류)'],
            '업종(소분류)': row['업종(소분류)']
        }
        
        # 회사 자체 노드
        company_texts.append(f"{company_name} ({company_code})")
        company_keys.append(f"COMPANY_{company_name}")
        
        # 업종 정보
        major_industry = row['업종(대분류)']
        mid_industry = row['업종(중분류)']
        small_industry = row['업종(소분류)']
        market = row['시장구분']
        issue_type = row['발행형태']
        stock_type = row['주식종류']
        
        # 구조화된 관계 텍스트들 - 한국어 자연어로 구성
        relation_texts = [
            f"{company_name}은 {major_industry} 대분류 업종에 속합니다",
            f"{company_name}은 {mid_industry} 중분류 업종에 속합니다", 
            f"{company_name}은 {small_industry} 소분류 업종에 속합니다",
            f"{company_name}은 {market} 시장에 상장되어 있습니다",
            f"{company_name}의 발행형태는 {issue_type}입니다",
            f"{company_name}의 주식종류는 {stock_type}입니다"
        ]
        
        # 카테고리 텍스트들
        category_texts = [
            f"{major_industry} 대분류 업종",
            f"{mid_industry} 중분류 업종", 
            f"{small_industry} 소분류 업종",
            f"{market} 시장",
            f"{issue_type} 발행형태",
            f"{stock_type} 주식종류"
        ]
        
        company_texts.extend(relation_texts + category_texts)
        
        # 키 생성
        relation_keys = [
            f"RELATION_{company_name}_MAJOR_{major_industry}",
            f"RELATION_{company_name}_MID_{mid_industry}",
            f"RELATION_{company_name}_SMALL_{small_industry}",
            f"RELATION_{company_name}_MARKET_{market}",
            f"RELATION_{company_name}_ISSUE_{issue_type}",
            f"RELATION_{company_name}_STOCK_{stock_type}"
        ]
        
        category_keys = [
            f"CATEGORY_MAJOR_{major_industry}",
            f"CATEGORY_MID_{mid_industry}",
            f"CATEGORY_SMALL_{small_industry}",
            f"CATEGORY_MARKET_{market}",
            f"CATEGORY_ISSUE_{issue_type}",
            f"CATEGORY_STOCK_{stock_type}"
        ]
        
        company_keys.extend(relation_keys + category_keys)
    
    return company_texts, company_keys
```

## 4. 임베딩 생성 및 그래프 엣지 생성 함수

텍스트 데이터를 OpenAI API를 통해 임베딩으로 변환하고, 이를 기반으로 그래프의 엣지(연결)를 생성하는 함수를 정의합니다.

```python
def create_embeddings(texts: List[str], batch_size: int = 1000) -> List[List[float]]:
    """OpenAI API를 사용해 텍스트 임베딩 생성"""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            input=batch,
            model=model_name
        )
        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)
        print(f"임베딩 생성 진행: {min(i + batch_size, len(texts))}/{len(texts)}")

    return embeddings
    

def build_graph_edges(similarity_threshold: float = 0.7):
    """임베딩 유사도를 기반으로 그래프 엣지 생성"""
    print("그래프 엣지 생성 시작...")
    
    # 노드 추가
    for key in key_to_text.keys():
        graph.add_node(key, text=key_to_text[key])
    
    # 임베딩 배열로 변환
    keys = list(embeddings.keys())
    embedding_matrix = np.array([embeddings[key] for key in keys])
    
    # 유사도 계산
    similarity_matrix = cosine_similarity(embedding_matrix)
    
    # 엣지 추가
    edge_count = 0
    for i, key1 in enumerate(keys):
        for j, key2 in enumerate(keys[i+1:], i+1):
            similarity = similarity_matrix[i][j]
            
            # 임계값 이상의 유사도를 가진 노드들을 연결
            if similarity >= similarity_threshold:
                graph.add_edge(key1, key2, weight=similarity)
                edge_count += 1
            
            # 명시적 관계도 추가 (같은 회사의 다른 속성들)
            if (key1.startswith("COMPANY_") and key2.startswith("RELATION_") and 
                key1.split("_", 1)[1] in key2):
                graph.add_edge(key1, key2, weight=1.0, relation_type="company_attribute")
                edge_count += 1
    
    print(f"그래프 엣지 생성 완료: {edge_count}개 엣지")
```

## 5. 시스템 구축 및 저장

앞서 정의한 함수들을 사용하여 실제로 그래프 RAG 시스템을 구축하고 저장합니다.

```python
# 텍스트 및 키 생성
texts, keys = build_graph_structure(df)
print(f"그래프 구조 생성 완료: {len(texts)}개 텍스트, {len(keys)}개 키")
# 출력: 그래프 구조 생성 완료: 11050개 텍스트, 11050개 키

# 텍스트-키 매핑 생성
for text, key in zip(texts, keys):
    text_to_key[text] = key
    key_to_text[key] = text

# 임베딩 생성
print("임베딩 생성 시작...")
embeddings_list = create_embeddings(texts)

# 임베딩 딕셔너리 생성
for key, embedding in zip(keys, embeddings_list):
    embeddings[key] = embedding

# 그래프 엣지 생성
similarity_threshold = 0.7
build_graph_edges(similarity_threshold)
print("Graph RAG 시스템 구축 완료!")

# 시스템 저장
save_path = "graph_rag_system.pkl"
save_data = {
    'graph': graph,
    'embeddings': embeddings,
    'text_to_key': text_to_key,
    'key_to_text': key_to_text,
    'company_data': company_data,
    'model_name': model_name
}

with open(save_path, 'wb') as f:
    pickle.dump(save_data, f)

# 저장된 시스템 로드
with open(save_path, 'rb') as f:
    save_data = pickle.load(f)

graph = save_data['graph']
embeddings = save_data['embeddings']
text_to_key = save_data['text_to_key']
key_to_text = save_data['key_to_text']
company_data = save_data['company_data']
model_name = save_data['model_name']
```

## 6. 쿼리 기능 구현

그래프 RAG 시스템에 쿼리를 넣어 결과를 얻는 함수를 구현합니다.

```python
def query(query_text: str, top_k: int = 5, embeddings = embeddings) -> List[Dict]:
    """쿼리에 대한 응답 생성"""
    # 쿼리 임베딩 생성
    query_embedding = create_embeddings([query_text])[0]
    
    # 모든 노드와의 유사도 계산
    similarities = []
    for key, embedding in embeddings.items():
        similarity = cosine_similarity([query_embedding], [embedding])[0][0]
        similarities.append((key, similarity))
    
    # 상위 k개 노드 선택
    top_nodes = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
    
    # 선택된 노드들의 그래프 서브셋 추출
    selected_keys = [node[0] for node in top_nodes]
    subgraph = graph.subgraph(selected_keys)
    
    # 결과 구성
    results = []
    for key, similarity in top_nodes:
        node_info = {
            'key': key,
            'text': key_to_text[key],
            'similarity': similarity,
            'neighbors': list(subgraph.neighbors(key)) if key in subgraph else [],
            'node_type': key.split('_')[0]
        }
        
        # 회사 정보인 경우 추가 데이터 포함
        if key.startswith('COMPANY_'):
            company_name = key.replace('COMPANY_', '')
            if company_name in company_data:
                node_info['company_data'] = company_data[company_name]
        
        results.append(node_info)
    
    return results
```

## 7. 쿼리 테스트 및 결과 분석

다양한 쿼리를 넣어 시스템의 응답을 테스트합니다.

### 7.1 회사명 변형 쿼리 테스트

시스템이 오타나 변형된 회사명에도 올바른 회사를 찾아내는지 테스트합니다.

```python
for query_text in ["CJ 시푸드", 'cj시푸드','cjseafood']:
    print(f"\n쿼리: {query_text}")
    results = query(query_text, top_k=5)
    for result in results:
        print(f"텍스트: {result['text']}, 유사도: {result['similarity']:.4f}")
```

**실행 결과 예시:**
```
쿼리: CJ 시푸드
키: COMPANY_CJ씨푸드, 텍스트: CJ씨푸드 (011150), 유사도: 0.5857
회사 정보: {'종목코드': '011150', '종목명': 'CJ씨푸드', '발행형태': '전자증권',
'시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '필수소비재',
'업종(중분류)': '음식료 및 담배', '업종(소분류)': '식료품'}
```

### 7.2 삼성전자 쿼리 테스트

```python
query_text = "삼성전자"
results = query(query_text, top_k=5)
for result in results:
    print(f"텍스트: {result['text']}, 유사도: {result['similarity']:.4f}")
```

**실행 결과:**
```
키: COMPANY_삼성전자, 텍스트: 삼성전자 (005930), 유사도: 0.7921
회사 정보: {'종목코드': '005930', '종목명': '삼성전자', '발행형태': '전자증권',
'시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': 'IT',
'업종(중분류)': '반도체', '업종(소분류)': '반도체 및 관련장비'}
이웃 노드: ['RELATION_삼성전자_MAJOR_IT', 'RELATION_삼성전자_MARKET_유가증권',
'RELATION_삼성전자_ISSUE_전자증권', 'COMPANY_삼성전기']
```

### 7.3 업종별 회사 검색

```python
results = query("제약 업종의 회사들은?", top_k=5)
for result in results:
    print(f"유사도: {result['similarity']:.3f}")
    print(f"텍스트: {result['text']}")
    print(f"타입: {result['node_type']}")
```

**실행 결과:**
```
유사도: 0.566
텍스트: 제약 소분류 업종
타입: CATEGORY

유사도: 0.512
텍스트: 제일약품(신설)은 제약 소분류 업종에 속합니다
타입: RELATION

유사도: 0.477
텍스트: 일양약품은 제약 소분류 업종에 속합니다
타입: RELATION
```

## 8. 그래프 구조 분석

생성된 그래프의 구조를 분석하여 통계적인 정보를 확인합니다.

```python
"""그래프 구조 분석"""
analysis = {
    'total_nodes': graph.number_of_nodes(),
    'total_edges': graph.number_of_edges(),
    'node_types': defaultdict(int),
    'avg_degree': np.mean([degree for node, degree in graph.degree()]),
    'connected_components': nx.number_connected_components(graph)
}

for node in graph.nodes():
    node_type = node.split('_')[0]
    analysis['node_types'][node_type] += 1

for key, value in analysis.items():
    print(f"{key}: {value}")
```

**실행 결과:**
```
total_nodes: 6050
total_edges: 413221
node_types: defaultdict(<class 'int'>, {'COMPANY': 850, 'RELATION': 5100, 'CATEGORY': 100})
avg_degree: 136.60
connected_components: 7
```

## 9. 주요 기능 및 특징

### 9.1 오타 처리 강건성
임베딩 기반 유사도 검색으로 다양한 형태의 회사명 변형을 처리합니다:
- "CJ 시푸드", "cj시푸드", "cjseafood" → CJ씨푸드 정확히 검색
- "삼송전자" → 삼성전자 검색 가능

### 9.2 그래프 기반 관계 탐색
- 회사와 업종, 시장 정보를 그래프로 연결
- 노드 간 이웃 관계를 통한 관련 정보 확인
- 유사도 임계값(0.7)으로 의미있는 연결만 유지

### 9.3 다양한 쿼리 유형 지원
- 회사 정보 조회: "삼성전자의 정보는?"
- 종목코드 검색: "005930 종목코드를 가진 회사는?"
- 업종별 검색: "제약 업종의 회사들은?"
- 속성 기반 필터링: "유가증권 시장에 상장된 회사 목록은?"

## 10. 시스템 성능 지표

| 지표 | 값 |
|------|-----|
| 총 종목 수 | 850개 |
| 총 노드 수 | 6,050개 |
| 총 엣지 수 | 413,221개 |
| 평균 연결도 | 136.60 |
| 연결 컴포넌트 | 7개 |
| 임베딩 차원 | 1536 (text-embedding-3-small) |

## 결론

이 프로젝트를 통해 주식 데이터를 그래프 구조로 모델링하고, 텍스트 임베딩을 활용한 유사도 기반의 검색 시스템을 구현했습니다.

**주요 성과:**
- ✅ 850개 종목 데이터의 그래프 기반 구조화
- ✅ OpenAI Embeddings를 활용한 의미론적 검색
- ✅ 오타 및 변형 쿼리에 강건한 검색 시스템
- ✅ 관계 기반 탐색을 통한 맥락적 정보 제공

이러한 그래프 기반 RAG 시스템은 복잡한 관계가 있는 데이터에서 보다 정확하고 맥락이 풍부한 검색 결과를 제공할 수 있습니다.
