# 🔍 문서 검색 테스트 (RAG 기반)

## ✅ 실행 내용 요약

- HTML 문서를 불러와 벡터로 임베딩 후 벡터스토어 구축
- 문서마다 메타데이터(`subChapterId`, `theoryId`) 추가
- `queries.yaml` 내 쿼리로 관련 문서 검색 수행
- 결과는 YAML 및 Markdown 형식으로 저장

## RAG 세팅
```python
# 임베딩 객체 정의
embedding = OpenAIEmbeddings(
    model = "text-embedding-3-small",
    openai_api_key=API_KEY,
)
# Vectorstore
vectorstore = Chroma(
    collection_name="html_docs",
    persist_directory=vectordb_path,
    embedding_function=embedding,
)
# 문서로드 및 임베딩
for path in tqdm(os.listdir(base_path)):
    html_loader = UnstructuredHTMLLoader(
        file_path=os.path.join(base_path, path),
        mode="single",
    )
    documents = html_loader.load()
    for doc in documents:
        doc.metadata['theoryId'] = path.split('_')[1]
        doc.metadata['subChapterId'] = path.split('_')[0]
    vectorstore.add_documents(documents)

# 검색기 정의
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)
```
```python
# 검색 실행
docs = retriever.invoke(query)

# 생성 모델 결과
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    api_key=GEMINI_API_KEY,
)
for source in sources:
    content = get_target_source(source, max_length=2000)
    contents.append(content)

context = "\n".join([f"{'#'*10}\n{i+1}. {content}" for i, content in enumerate(contents)])

prompt = f"""
You are an expert in the field of computer science. Based on the following context, please answer the question:

Context:
{context}

Question: {query}

Answer:
"""
response = llm.invoke(prompt).content.strip()
```

## 🔎 사용한 질의

1. 뎅기열과 비슷한 매개체로 인한 감염병은?
2. 불명열 진단 순서를 설명하시오
3. 패혈증의 정의와 치료 접근법은?
4. 발열의 병태생리 과정을 설명하시오
5. 심부전으로 입원한 환자의 초기 평가 항목은?
6. 심부전으로 입원한 환자에게 처음 시행해야 할 처치는?

## 📋 Retriever 결과 요약
> 의료 관련 QA 플랫폼을 위한 정보 검색(Retrieval) 성능 평가 결과를 요약한 문서입니다. 각 쿼리(Query)에 대해 Retriever가 반환한 관련성 높은 상위 10개 문서를 정리하였습니다.


[결과 확인하기!](./query_log.md)
### 🧪 Query: **뎅기열과 비슷한 매개체로 인한 감염병은?**

| Rank | Source | 평가 |
|------|--------|------|
| 1 | `1643_3848_여행 관련 바이러스 감염.html` | ✅ 매우 관련 |
| 2 | `2522_5676_Leptospira interrogans.html` | ⚠️ 부분 관련 (매개체 감염이지만 세균성) |
| 3 | `2521_5659_Legionella pneumophila.html` | ❌ 비관련 (호흡기 병원균) |
| 4 | `1637_3860_골수염.html` | ❌ 비관련 |
| 5 | `2747_5639_염증의 양상.html` | ❌ 비관련 |
| 6 | `2525_5685_Rubella virus.html` | ⚠️ 부분 관련 (바이러스이지만 전파 경로 다름) |
| 7 | `1636_3826_발열, 불명열.html` | ⚠️ 일반적 관련 |
| 8 | `1638_3852_Healthcare-associated infections.html` | ❌ 비관련 |
| 9 | `2525_5689_Norovirus.html` | ❌ 비관련 (소화기 전파) |
| 10 | `1639_3828_피부연조직 감염.html` | ❌ 비관련 |

---

### 🧪 Query: **불명열 진단 순서를 설명하시오**

| Rank | Source | 평가 |
|------|--------|------|
| 1 | `1636_3826_발열, 불명열.html` | ✅ 매우 관련 |
| 2 | `2417_5489_근육 수축의 기계적 특성.html` | ❌ 비관련 |
| 3 | `1872_4389_진단서.html` | ❌ 비관련 |
| 4 | `1940_4489_호흡 보조 요법.html` | ❌ 비관련 |
| 5 | `2417_5490_Striated muscle의 구조적 특성 및 흥분 수축 연계과정.html` | ❌ 비관련 |
| 6 | `1940_5468_심화 1. 기계환기.html` | ❌ 비관련 |
| 7 | `1736_4031_난산.html` | ❌ 비관련 |
| 8 | `2488_5583_심장의 전기활동.html` | ❌ 비관련 |
| 9 | `1932_4492_COPD의 급성악화.html` | ❌ 비관련 |
| 10 | `1836_4280_진동과 방사선.html` | ❌ 비관련 |

---

### 🧪 Query: **패혈증의 정의와 치료 접근법은?**

| Rank | Source | 평가 |
|------|--------|------|
| 1 | `3442_5477_관절염의 개요.html` | ❌ 비관련 |
| 2 | `1912_4464_빈혈의 접근.html` | ❌ 비관련 |
| 3 | `1669_3904_결정 유발 관절염.html` | ❌ 비관련 |
| 4 | `1654_3887_당뇨의 만성 합병증.html` | ❌ 비관련 |
| 5 | `1937_4505_폐색전증.html` | ❌ 비관련 |
| 6 | `2489_5586_혈액응고.html` | ⚠️ 약간 관련 (혈역학적 문제 일부 연관) |
| 7 | `1909_4454_종양의 치료.html` | ❌ 비관련 |
| 8 | `1767_4108_수분 및 전해질 평형.html` | ⚠️ 간접 관련 |
| 9 | `1721_4024_자궁근종.html` | ❌ 비관련 |
| 10 | `1790_4139_만성 C형 간염.html` | ❌ 비관련 |

---

### 🧪 Query: **발열의 병태생리 과정을 설명하시오**

| Rank | Source | 평가 |
|------|--------|------|
| 1 | `1754_4059_가와사키병.html` | ⚠️ 부분 관련 (발열 포함 질환) |
| 2 | `1740_4032_다태임신.html` | ❌ 비관련 |
| 3 | `1910_4455_신생물딸림증후군.html` | ⚠️ 간접 관련 |
| 4 | `1910_4458_종양용해증후군.html` | ⚠️ 간접 관련 |
| 5 | `1752_4094_청색증 선천 심질환.html` | ❌ 비관련 |
| 6 | `1748_4048_기타 내·외과적 합병증.html` | ❌ 비관련 |
| 7 | `1923_4460_다발골수종 및 기타 혈액암.html` | ⚠️ 발열 유발 질환이지만 병태생리 설명 부족 |
| 8 | `1734_4038_기형학.html` | ❌ 비관련 |
| 9 | `1636_3826_발열, 불명열.html` | ✅ 직접 관련 |
| 10 | `2745_5655_임신영양막병.html` | ❌ 비관련 |

---

### 🧪 Query: **심부전으로 입원한 환자의 초기 평가 항목은?**

| Rank | Source | 평가 |
|------|--------|------|
| 1 | `1800_4195_심부전 원인, 증상, 진단.html` | ✅ 매우 관련 |
| 2 | `1888_4435_정신과적 평가.html` | ❌ 비관련 |
| 3 | `1696_3954_외상의 응급처치.html` | ❌ 비관련 |
| 4 | `1800_4194_심부전 개요.html` | ✅ 관련 |
| 5 | `1797_4199_심혈관계 검사.html` | ✅ 관련 |
| 6 | `1652_3896_부신 우연종.html` | ❌ 비관련 |
| 7 | `1843_4276_의료의 질.html` | ❌ 비관련 |
| 8 | `1800_4196_심부전 치료.html` | ⚠️ 관련 (진단보단 치료 중심) |
| 9 | `1862_4330_선택적 수술에 대한 반응.html` | ❌ 비관련 |
| 10 | `1843_4275_병원관리.html` | ❌ 비관련 |

---

### 🧪 Query: **심부전으로 입원한 환자에게 처음 시행해야 할 처치는?**

| Rank | Source | 평가 |
|------|--------|------|
| 1 | `2440_4450_지역사회정신의학.html` | ❌ 비관련 |
| 2 | `1868_4327_뱀물림과 동물물림.html` | ❌ 비관련 |
| 3 | `1864_4329_수술 전 처치.html` | ❌ 비관련 |
| 4 | `1813_4219_만성 신부전의 치료.html` | ❌ 비관련 |
| 5 | `1800_4195_심부전 원인, 증상, 진단.html` | ✅ 관련 |
| 6 | `1882_4401_헌혈자 관리.html` | ❌ 비관련 |
| 7 | `1696_3952_심폐소생술.html` | ⚠️ 응급 처치 관련 (상황에 따라 유용) |
| 8 | `1872_4390_처방전.html` | ❌ 비관련 |
| 9 | `1652_3896_부신 우연종.html` | ❌ 비관련 |
| 10 | `1638_3852_Healthcare-associated infections.html` | ❌ 비관련 |



## 📋 Generator 결과
[결과 확인하기!](./query_log_llm.md)
