```python
OPENAI_API_KEY = ""
import os
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
import pandas as pd
excel_file_path = r"C:\Users\Sese\Downloads\주식종목전체검색.xlsx"
df = pd.read_excel(excel_file_path)
print(f"데이터 로드 완료: {len(df)}개 종목")

industry_cols = ['업종(대분류)', '업종(중분류)', '업종(소분류)']
for col in industry_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')

df
```

    데이터 로드 완료: 850개 종목
    




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>종목코드</th>
      <th>종목명</th>
      <th>발행형태</th>
      <th>시장구분</th>
      <th>주식종류</th>
      <th>업종(대분류)</th>
      <th>업종(중분류)</th>
      <th>업종(소분류)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>000080</td>
      <td>하이트진로</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td>필수소비재</td>
      <td>음식료 및 담배</td>
      <td>음료</td>
    </tr>
    <tr>
      <th>1</th>
      <td>000140</td>
      <td>하이트진로홀딩스</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td>필수소비재</td>
      <td>음식료 및 담배</td>
      <td>음료</td>
    </tr>
    <tr>
      <th>2</th>
      <td>000890</td>
      <td>보해양조</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td>필수소비재</td>
      <td>음식료 및 담배</td>
      <td>음료</td>
    </tr>
    <tr>
      <th>3</th>
      <td>001130</td>
      <td>대한제분</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td>필수소비재</td>
      <td>음식료 및 담배</td>
      <td>식료품</td>
    </tr>
    <tr>
      <th>4</th>
      <td>001680</td>
      <td>대상</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td>필수소비재</td>
      <td>음식료 및 담배</td>
      <td>식료품</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>845</th>
      <td>417310</td>
      <td>코람코더원위탁관리부동산투자회사</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>846</th>
      <td>432320</td>
      <td>케이비스타위탁관리부동산투자회사</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>847</th>
      <td>448730</td>
      <td>삼성에프엔위탁관리부동산투자회사</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>848</th>
      <td>451800</td>
      <td>한화위탁관리부동산투자회사</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <th>849</th>
      <td>481850</td>
      <td>신한글로벌액티브위탁관리부동산투자회사</td>
      <td>전자증권</td>
      <td>유가증권</td>
      <td>보통주</td>
      <td></td>
      <td></td>
      <td></td>
    </tr>
  </tbody>
</table>
<p>850 rows × 8 columns</p>
</div>




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


```python
"""전체 Graph RAG 시스템 구축"""
print("Graph RAG 시스템 구축 시작...")

texts, keys = build_graph_structure(df)
print(f"그래프 구조 생성 완료: {len(texts)}개 텍스트, {len(keys)}개 키")
for text, key in zip(texts[:5], keys[:5]):
    print(f"텍스트: {text}, 키: {key}")

# 텍스트-키 매핑 생성
for text, key in zip(texts, keys):
    text_to_key[text] = key
    key_to_text[key] = text

```

    Graph RAG 시스템 구축 시작...
    그래프 구조 생성 완료: 11050개 텍스트, 11050개 키
    텍스트: 하이트진로 (000080), 키: COMPANY_하이트진로
    텍스트: 하이트진로은 필수소비재 대분류 업종에 속합니다, 키: RELATION_하이트진로_MAJOR_필수소비재
    텍스트: 하이트진로은 음식료 및 담배 중분류 업종에 속합니다, 키: RELATION_하이트진로_MID_음식료 및 담배
    텍스트: 하이트진로은 음료 소분류 업종에 속합니다, 키: RELATION_하이트진로_SMALL_음료
    텍스트: 하이트진로은 유가증권 시장에 상장되어 있습니다, 키: RELATION_하이트진로_MARKET_유가증권
    


```python
# 3. 임베딩 생성
print("임베딩 생성 시작...")
embeddings_list = create_embeddings(texts)

# 4. 임베딩 딕셔너리 생성
for key, embedding in zip(keys, embeddings_list):
    embeddings[key] = embedding

# 5. 그래프 엣지 생성
similarity_threshold = 0.7
build_graph_edges(similarity_threshold)
print("Graph RAG 시스템 구축 완료!")

```

    임베딩 생성 시작...
    임베딩 생성 진행: 1000/11050
    임베딩 생성 진행: 2000/11050
    임베딩 생성 진행: 3000/11050
    임베딩 생성 진행: 4000/11050
    임베딩 생성 진행: 5000/11050
    임베딩 생성 진행: 6000/11050
    임베딩 생성 진행: 7000/11050
    임베딩 생성 진행: 8000/11050
    임베딩 생성 진행: 9000/11050
    임베딩 생성 진행: 10000/11050
    임베딩 생성 진행: 11000/11050
    임베딩 생성 진행: 11050/11050
    그래프 엣지 생성 시작...
    그래프 엣지 생성 완료: 413416개 엣지
    Graph RAG 시스템 구축 완료!
    


```python
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
    

"""저장된 시스템 로드"""
with open(save_path, 'rb') as f:
    save_data = pickle.load(f)

graph = save_data['graph']
embeddings = save_data['embeddings']
text_to_key = save_data['text_to_key']
key_to_text = save_data['key_to_text']
company_data = save_data['company_data']
model_name = save_data['model_name']

print(f"시스템이 {save_path}에서 로드되었습니다.")

```

    시스템이 graph_rag_system.pkl에서 로드되었습니다.
    

## 쿼리 넣어서 응답 확인하기


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


```python
for query_text in ["CJ 시푸드", 'cj시푸드','cjseafood','CJ시뿌드','CJ시뿌뜨', '시제이시푸드','시제이씨뿌드','씨제이시푸드']:
    print(f"\n쿼리: {query_text}")
    results = query(query_text, top_k=5)
    for result in results:
        print(f"키: {result['key']}, 텍스트: {result['text']}, 유사도: {result['similarity']:.4f}")
        if 'company_data' in result:
            print(f"회사 정보: {result['company_data']}")
        print(f"이웃 노드: {result['neighbors']}")
        print(f"노드 타입: {result['node_type']}\n")
```

    
    쿼리: CJ 시푸드
    임베딩 생성 진행: 1/1
    키: COMPANY_CJ씨푸드, 텍스트: CJ씨푸드 (011150), 유사도: 0.5857
    회사 정보: {'종목코드': '011150', '종목명': 'CJ씨푸드', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '필수소비재', '업종(중분류)': '음식료 및 담배', '업종(소분류)': '식료품'}
    이웃 노드: ['RELATION_CJ씨푸드_MAJOR_필수소비재', 'RELATION_CJ씨푸드_MID_음식료 및 담배', 'RELATION_CJ씨푸드_SMALL_식료품', 'RELATION_CJ씨푸드_STOCK_보통주']
    노드 타입: COMPANY
    
    키: RELATION_CJ씨푸드_MID_음식료 및 담배, 텍스트: CJ씨푸드은 음식료 및 담배 중분류 업종에 속합니다, 유사도: 0.5254
    이웃 노드: ['COMPANY_CJ씨푸드', 'RELATION_CJ씨푸드_SMALL_식료품']
    노드 타입: RELATION
    
    키: RELATION_CJ씨푸드_MAJOR_필수소비재, 텍스트: CJ씨푸드은 필수소비재 대분류 업종에 속합니다, 유사도: 0.5144
    이웃 노드: ['COMPANY_CJ씨푸드', 'RELATION_CJ씨푸드_SMALL_식료품']
    노드 타입: RELATION
    
    키: RELATION_CJ씨푸드_STOCK_보통주, 텍스트: CJ씨푸드의 주식종류는 보통주입니다, 유사도: 0.5132
    이웃 노드: ['COMPANY_CJ씨푸드']
    노드 타입: RELATION
    
    키: RELATION_CJ씨푸드_SMALL_식료품, 텍스트: CJ씨푸드은 식료품 소분류 업종에 속합니다, 유사도: 0.5115
    이웃 노드: ['COMPANY_CJ씨푸드', 'RELATION_CJ씨푸드_MAJOR_필수소비재', 'RELATION_CJ씨푸드_MID_음식료 및 담배']
    노드 타입: RELATION
    

```python
print("쿼리 예시: '삼성전자'에 대한 응답 생성")
query_text = "삼성전자"
results = query(query_text, top_k=5)
for result in results:
    print(f"키: {result['key']}, 텍스트: {result['text']}, 유사도: {result['similarity']:.4f}")
    if 'company_data' in result:
        print(f"회사 정보: {result['company_data']}")
    print(f"이웃 노드: {result['neighbors']}")
    print(f"노드 타입: {result['node_type']}\n")
```

    쿼리 예시: '삼성전자'에 대한 응답 생성
    임베딩 생성 진행: 1/1
    키: COMPANY_삼성전자, 텍스트: 삼성전자 (005930), 유사도: 0.7921
    회사 정보: {'종목코드': '005930', '종목명': '삼성전자', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': 'IT', '업종(중분류)': '반도체', '업종(소분류)': '반도체 및 관련장비'}
    이웃 노드: ['RELATION_삼성전자_MAJOR_IT', 'RELATION_삼성전자_MARKET_유가증권', 'RELATION_삼성전자_ISSUE_전자증권', 'COMPANY_삼성전기']
    노드 타입: COMPANY
    
    키: RELATION_삼성전자_MAJOR_IT, 텍스트: 삼성전자은 IT 대분류 업종에 속합니다, 유사도: 0.6291
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: RELATION
    
    키: RELATION_삼성전자_ISSUE_전자증권, 텍스트: 삼성전자의 발행형태는 전자증권입니다, 유사도: 0.6250
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: RELATION
    
    키: RELATION_삼성전자_MARKET_유가증권, 텍스트: 삼성전자은 유가증권 시장에 상장되어 있습니다, 유사도: 0.6188
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: RELATION
    
    키: COMPANY_삼성전기, 텍스트: 삼성전기 (009150), 유사도: 0.6171
    회사 정보: {'종목코드': '009150', '종목명': '삼성전기', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': 'IT', '업종(중분류)': '하드웨어', '업종(소분류)': '전자 장비 및 기기'}
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: COMPANY
    
    


```python
results = query("제약 업종의 회사들은?", top_k=5)

for result in results:
    print(f"유사도: {result['similarity']:.3f}")
    print(f"텍스트: {result['text']}")
    print(f"타입: {result['node_type']}")
    if 'company_data' in result:
        print(f"회사 정보: {result['company_data']}")
    print("-" * 50)
```

    임베딩 생성 진행: 1/1
    유사도: 0.566
    텍스트: 제약 소분류 업종
    타입: CATEGORY
    --------------------------------------------------
    유사도: 0.512
    텍스트: 제일약품(신설)은 제약 소분류 업종에 속합니다
    타입: RELATION
    --------------------------------------------------
    유사도: 0.479
    텍스트: 제일약품(신설)은 제약 및 바이오 중분류 업종에 속합니다
    타입: RELATION
    --------------------------------------------------
    유사도: 0.479
    텍스트: 제일약품(신설)은 의료 대분류 업종에 속합니다
    타입: RELATION
    --------------------------------------------------
    유사도: 0.477
    텍스트: 일양약품은 제약 소분류 업종에 속합니다
    타입: RELATION
    --------------------------------------------------
    


```python
queries = [
# 회사 정보 조회 관련 쿼리:
"삼성전자의 정보는?",
"005930 종목코드를 가진 회사는?",
"하이트진로는 어떤 회사인가요?",
"SK하이닉스에 대해 알려줘",
"현대차의 업종은?",
# 업종별 회사 검색 관련 쿼리:",
"식료품 소분류 업종의 회사들은?",
"음식료 및 담배 중분류 업종에는 어떤 회사들이 있나요?",
"IT 대분류 업종의 대표적인 회사들을 알려줘",
"건설 업종에 속하는 기업은?",
"자동차 관련 회사들을 찾아줘",
# 속성 기반 필터링 및 관계 탐색 쿼리:",
"유가증권 시장에 상장된 회사 목록은?",
"전자증권 발행 형태를 가진 회사들은?",
"보통주 주식종류를 가진 회사들을 보여줘",
"필수소비재 업종에 속하면서 유가증권 시장에 있는 회사들은?",
"삼성전자와 비슷한 업종의 회사들은?",
"",
# 오타/변형 허용 쿼리 (시스템의 임베딩 처리 능력 확인):",
"삼송전자 정보",
"씨제이씨푸드",
"하이뜨진로",
]
all_results = []
for query_text in queries:
    print(f"\n쿼리: {query_text}")
    try:
        results = query(query_text, top_k=5)
        for result in results:
            print(f"키: {result['key']}, 텍스트: {result['text']}, 유사도: {result['similarity']:.4f}")
            if 'company_data' in result:
                print(f"회사 정보: {result['company_data']}")
            print(f"이웃 노드: {result['neighbors']}")
            print(f"노드 타입: {result['node_type']}\n")

        all_results.append({
            'query': query_text,
            'results': results
        })
    except Exception as e:
        print(f"쿼리 '{query_text}' 처리 중 오류 발생: {e}")

```

    
    쿼리: 삼성전자의 정보는?
    임베딩 생성 진행: 1/1
    키: COMPANY_삼성전자, 텍스트: 삼성전자 (005930), 유사도: 0.6353
    회사 정보: {'종목코드': '005930', '종목명': '삼성전자', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': 'IT', '업종(중분류)': '반도체', '업종(소분류)': '반도체 및 관련장비'}
    이웃 노드: ['RELATION_삼성전자_MAJOR_IT', 'RELATION_삼성전자_SMALL_반도체 및 관련장비', 'RELATION_삼성전자_MARKET_유가증권', 'RELATION_삼성전자_ISSUE_전자증권']
    노드 타입: COMPANY
    
    키: RELATION_삼성전자_ISSUE_전자증권, 텍스트: 삼성전자의 발행형태는 전자증권입니다, 유사도: 0.6087
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: RELATION
    
    키: RELATION_삼성전자_MAJOR_IT, 텍스트: 삼성전자은 IT 대분류 업종에 속합니다, 유사도: 0.5928
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: RELATION
    
    키: RELATION_삼성전자_MARKET_유가증권, 텍스트: 삼성전자은 유가증권 시장에 상장되어 있습니다, 유사도: 0.5499
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: RELATION
    
    키: RELATION_삼성전자_SMALL_반도체 및 관련장비, 텍스트: 삼성전자은 반도체 및 관련장비 소분류 업종에 속합니다, 유사도: 0.5436
    이웃 노드: ['COMPANY_삼성전자']
    노드 타입: RELATION
    
    
    쿼리: 005930 종목코드를 가진 회사는?
    임베딩 생성 진행: 1/1
    키: COMPANY_삼성전자, 텍스트: 삼성전자 (005930), 유사도: 0.5007
    회사 정보: {'종목코드': '005930', '종목명': '삼성전자', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': 'IT', '업종(중분류)': '반도체', '업종(소분류)': '반도체 및 관련장비'}
    이웃 노드: []
    노드 타입: COMPANY
    
    키: COMPANY_SKC, 텍스트: SKC (011790), 유사도: 0.4841
    회사 정보: {'종목코드': '011790', '종목명': 'SKC', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '소재', '업종(중분류)': '소재', '업종(소분류)': '화학'}
    이웃 노드: []
    노드 타입: COMPANY
    
    키: COMPANY_상상인증권, 텍스트: 상상인증권 (001290), 유사도: 0.4836
    회사 정보: {'종목코드': '001290', '종목명': '상상인증권', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '금융', '업종(중분류)': '증권', '업종(소분류)': '증권'}
    이웃 노드: []
    노드 타입: COMPANY
    
    키: COMPANY_성창기업지주, 텍스트: 성창기업지주 (000180), 유사도: 0.4808
    회사 정보: {'종목코드': '000180', '종목명': '성창기업지주', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '소재', '업종(중분류)': '소재', '업종(소분류)': '종이 및 목재'}
    이웃 노드: []
    노드 타입: COMPANY
    
    키: COMPANY_한성기업, 텍스트: 한성기업 (003680), 유사도: 0.4734
    회사 정보: {'종목코드': '003680', '종목명': '한성기업', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '필수소비재', '업종(중분류)': '음식료 및 담배', '업종(소분류)': '식료품'}
    이웃 노드: []
    노드 타입: COMPANY
    
    
    쿼리: 하이트진로는 어떤 회사인가요?
    임베딩 생성 진행: 1/1
    키: COMPANY_하이트진로, 텍스트: 하이트진로 (000080), 유사도: 0.7572
    회사 정보: {'종목코드': '000080', '종목명': '하이트진로', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '필수소비재', '업종(중분류)': '음식료 및 담배', '업종(소분류)': '음료'}
    이웃 노드: ['RELATION_하이트진로_MID_음식료 및 담배', 'RELATION_하이트진로_ISSUE_전자증권', 'COMPANY_하이트진로홀딩스', 'RELATION_하이트진로홀딩스_MID_음식료 및 담배']
    노드 타입: COMPANY
    
    키: COMPANY_하이트진로홀딩스, 텍스트: 하이트진로홀딩스 (000140), 유사도: 0.6855
    회사 정보: {'종목코드': '000140', '종목명': '하이트진로홀딩스', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '필수소비재', '업종(중분류)': '음식료 및 담배', '업종(소분류)': '음료'}
    이웃 노드: ['COMPANY_하이트진로', 'RELATION_하이트진로홀딩스_MID_음식료 및 담배']
    노드 타입: COMPANY
    
    키: RELATION_하이트진로_MID_음식료 및 담배, 텍스트: 하이트진로은 음식료 및 담배 중분류 업종에 속합니다, 유사도: 0.5772
    이웃 노드: ['COMPANY_하이트진로', 'RELATION_하이트진로홀딩스_MID_음식료 및 담배']
    노드 타입: RELATION
    
    키: RELATION_하이트진로홀딩스_MID_음식료 및 담배, 텍스트: 하이트진로홀딩스은 음식료 및 담배 중분류 업종에 속합니다, 유사도: 0.5444
    이웃 노드: ['COMPANY_하이트진로', 'RELATION_하이트진로_MID_음식료 및 담배', 'COMPANY_하이트진로홀딩스']
    노드 타입: RELATION
    
    키: RELATION_하이트진로_ISSUE_전자증권, 텍스트: 하이트진로의 발행형태는 전자증권입니다, 유사도: 0.5272
    이웃 노드: ['COMPANY_하이트진로']
    노드 타입: RELATION
    
    
    쿼리: SK하이닉스에 대해 알려줘
    임베딩 생성 진행: 1/1
    키: COMPANY_에스케이하이닉스, 텍스트: 에스케이하이닉스 (000660), 유사도: 0.4460
    회사 정보: {'종목코드': '000660', '종목명': '에스케이하이닉스', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': 'IT', '업종(중분류)': '반도체', '업종(소분류)': '반도체 및 관련장비'}
    이웃 노드: ['RELATION_에스케이하이닉스_MAJOR_IT']
    노드 타입: COMPANY
    
    키: RELATION_에스케이하이닉스_MAJOR_IT, 텍스트: 에스케이하이닉스은 IT 대분류 업종에 속합니다, 유사도: 0.4233
    이웃 노드: ['COMPANY_에스케이하이닉스']
    노드 타입: RELATION
    
    키: RELATION_한미사이언스_MAJOR_의료, 텍스트: 한미사이언스은 의료 대분류 업종에 속합니다, 유사도: 0.4199
    이웃 노드: []
    노드 타입: RELATION
    
    키: COMPANY_에스케이이터닉스, 텍스트: 에스케이이터닉스 (475150), 유사도: 0.4185
    회사 정보: {'종목코드': '475150', '종목명': '에스케이이터닉스', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '에너지', '업종(중분류)': '에너지', '업종(소분류)': '에너지 시설 및 서비스'}
    이웃 노드: []
    노드 타입: COMPANY
    
    키: COMPANY_자이에스앤디(주), 텍스트: 자이에스앤디(주) (317400), 유사도: 0.4055
    회사 정보: {'종목코드': '317400', '종목명': '자이에스앤디(주)', '발행형태': '전자증권', '시장구분': '유가증권', '주식종류': '보통주', '업종(대분류)': '산업재', '업종(중분류)': '자본재', '업종(소분류)': '건설'}
    이웃 노드: []
    노드 타입: COMPANY
    
    
    쿼리: 현대차의 업종은?
    임베딩 생성 진행: 1/1
    키: RELATION_현대제철_MAJOR_소재, 텍스트: 현대제철은 소재 대분류 업종에 속합니다, 유사도: 0.6293
    이웃 노드: ['RELATION_현대제철_MID_소재']
    노드 타입: RELATION
    
    키: RELATION_현대자동차_SMALL_자동차, 텍스트: 현대자동차은 자동차 소분류 업종에 속합니다, 유사도: 0.6166
    이웃 노드: ['RELATION_현대자동차_MAJOR_경기소비재']
    노드 타입: RELATION
    
    키: RELATION_현대제철_MID_소재, 텍스트: 현대제철은 소재 중분류 업종에 속합니다, 유사도: 0.6164
    이웃 노드: ['RELATION_현대제철_MAJOR_소재']
    노드 타입: RELATION
    
    키: RELATION_현대차증권_SMALL_증권, 텍스트: 현대차증권은 증권 소분류 업종에 속합니다, 유사도: 0.6003
    이웃 노드: []
    노드 타입: RELATION
    
    키: RELATION_현대자동차_MAJOR_경기소비재, 텍스트: 현대자동차은 경기소비재 대분류 업종에 속합니다, 유사도: 0.5933
    이웃 노드: ['RELATION_현대자동차_SMALL_자동차']
    노드 타입: RELATION

    


```python

```

    쿼리 결과가 'my_query_results.html' 파일로 성공적으로 저장되었습니다.
    


```python
def get_company_by_industry(industry: str, industry_level: str = "소분류") -> List[str]:
    """특정 업종의 회사들 반환"""
    companies = []
    level_map = {
        "대분류": "업종(대분류)",
        "중분류": "업종(중분류)", 
        "소분류": "업종(소분류)"
    }
    
    column = level_map.get(industry_level, "업종(소분류)")
    
    for company_name, data in company_data.items():
        if data[column] == industry:
            companies.append(company_name)
    
    return companies


```


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

    total_nodes: 6050
    total_edges: 413221
    node_types: defaultdict(<class 'int'>, {'COMPANY': 850, 'RELATION': 5100, 'CATEGORY': 100})
    avg_degree: 136.6019834710744
    connected_components: 7
    


```python

```
