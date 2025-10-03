# Agent 흐름 문서

## 개요

이 문서는 Rumor Verification 시스템의 **AI Agent 내부 작동 방식과 의사결정 흐름**을 설명합니다. 시스템은 3개의 독립적인 AI Agent로 구성되어 있으며, 각 Agent는 특정 역할과 판단 기준을 가지고 자율적으로 작동합니다.

---

## Agent 아키텍처

```
User Query
    ↓
┌─────────────────────────────┐
│ 1. CompanyExtractor Agent   │ ← LLM: Clova HCX-007 / Gemini
│    (회사명 추출 및 정규화)    │
└─────────────────────────────┘
    ↓ company_name or null
    ↓
┌─────────────────────────────┐
│ NewsSearcher                │ ← Agent 아님 (Naver API)
│ (뉴스 검색)                  │
└─────────────────────────────┘
    ↓ news_items
    ↓
┌─────────────────────────────┐
│ 2. AIAnalyzer Agent (1단계) │ ← LLM: Google Gemini
│    _analyze_news_details()  │
│    (뉴스별 신뢰성 분석)      │
└─────────────────────────────┘
    ↓ 신뢰성 분석 결과
    ↓
┌─────────────────────────────┐
│ 3. AIAnalyzer Agent (2단계) │ ← LLM: Google Gemini
│    verify_rumor()           │
│    (종합 루머 검증)          │
└─────────────────────────────┘
    ↓ 최종 검증 결과
    ↓
┌─────────────────────────────┐
│ ResultStorage               │ ← Agent 아님 (저장 로직)
└─────────────────────────────┘
```

---

## 1. CompanyExtractor Agent

**역할**: 사용자 자연어 쿼리에서 회사명을 추출하고 정규화

### 입력
```python
query: "삼전 자사주 매입했다는 거 사실이야?"
```

### Agent 설정
- **LLM**: Clova HCX-007 (백업: Google Gemini)
- **Temperature**: 0.1 (정확성 우선)
- **출력 형식**: JSON (`{"company_name": "..."}`)

### 프롬프트 전략 (company_extractor.py:41-72)

```
당신은 정보 추출 어시스턴트입니다.
사용자의 질문에서 'company_name' 정보만 추출하는 것이 당신의 임무입니다.

# 회사명 정규화 규칙
- "lg엔솔", "엘지엔솔" → "LG에너지솔루션"
- "카카오뱅크" → "카카오뱅크"
- "삼전" → "삼성전자"
- "현대차" → "현대자동차"
- 기타 줄임말은 가장 일반적인 정식 회사명으로 변환
```

### Agent의 자율 판단 포인트

1. **회사명 존재 여부 판단**
   - 회사명이 명확하지 않으면 → `null` 반환
   - 예: "주식 투자 방법이 궁금해" → `{"company_name": null}`

2. **정규화 규칙 적용**
   - "삼전" → AI가 "삼성전자"로 매핑 결정
   - "lg엔솔" → "LG에너지솔루션"

3. **에러 처리**
   - Clova API 실패 시 → 자동으로 Gemini로 전환
   - JSON 파싱 실패 시 → `None` 반환

### 출력
```python
company_name: "삼성전자"  # 정규화된 회사명
# or
company_name: None  # 추출 실패
```

### 코드 위치
- `src/company_extractor.py:37-84`
- 호출: `main.py:100`

---

## 2. AIAnalyzer Agent (1단계) - 뉴스 신뢰성 분석

**역할**: 개별 뉴스의 신뢰성을 루머 검증 관점에서 평가

### 입력
```
news_list = """
1. 제목: 삼성전자, 5000억원 자사주 매입 결정
   내용: 삼성전자가 주주가치 제고를 위해...
   날짜: 2025-01-31 12:00

2. 제목: 삼성 자사주 매입 소식에 주가 상승
   내용: 증권가에서는...
   날짜: 2025-01-31 11:30
"""
```

### Agent 설정
- **LLM**: Google Gemini 2.0 Flash
- **Temperature**: 0.3 (config/settings.py)
- **프롬프트**: 하드코딩 (ai_analyzer.py:85-93)

### 프롬프트 전략

```
다음 뉴스들을 각각 루머 검증 관점에서 분석해서 간단히 정리해주세요:

{news_list}

각 뉴스별로 다음 형식으로:
1. [뉴스 제목 요약] → 신뢰도: 높음/보통/낮음,
   출처: 공식/언론/개인/커뮤니티,
   검증: 검증됨/부분검증/미검증/의심
```

### Agent의 자율 판단 기준

#### 신뢰도 평가 (높음/보통/낮음)
- **높음**: 공식 발표, 주요 언론사 (조선일보, 한국경제 등)
- **보통**: 일반 언론사, 경제 전문지
- **낮음**: 개인 블로그, 커뮤니티, 미확인 출처

#### 출처 분류 (공식/언론/개인/커뮤니티)
- **공식**: 기업 공식 발표, IR 자료
- **언론**: 신문사, 뉴스 매체
- **개인**: 블로거, SNS
- **커뮤니티**: 주식 커뮤니티, 포럼

#### 검증 상태 (검증됨/부분검증/미검증/의심)
- **검증됨**: 다수 언론사 교차 확인
- **부분검증**: 일부 언론사만 보도
- **미검증**: 단일 출처, 확인 불가
- **의심**: 모순되는 정보, 근거 부족

### 출력 예시
```
1. 삼성전자 5000억 자사주 매입 → 신뢰도: 높음, 출처: 공식, 검증: 검증됨
2. 증권가 분석 → 신뢰도: 보통, 출처: 언론, 검증: 부분검증
```

### 코드 위치
- `src/ai_analyzer.py:81-99` (`_analyze_news_details()`)
- 호출: `ai_analyzer.py:66`

---

## 3. AIAnalyzer Agent (2단계) - 종합 루머 검증

**역할**: 1단계 분석 결과를 바탕으로 최종 루머 사실 여부 판정

### 입력
```python
{
    "rumor_text": "삼성전자 이재용이 자사주 매입했다는 거 사실이야?",
    "company_name": "삼성전자",
    "news_list": "1. 제목: ...\n2. 제목: ...",
    "analysis_details": "1. 삼성전자 5000억 자사주 매입 → 신뢰도: 높음..."
}
```

### Agent 설정
- **LLM**: Google Gemini 2.0 Flash
- **Temperature**: 0.3
- **프롬프트 소스**: `prompts/prompts.yaml` (외부 파일)

### 프롬프트 전략 (prompts.yaml:10-52)

```yaml
당신은 전문 팩트체킹 분석가이자 루머 검증 전문가입니다.

다음 루머에 대해 최신 뉴스를 바탕으로 사실 여부를 검증해주세요.

**검증할 루머**: "{rumor_text}"
**관련 회사**: "{company_name}"

최근 뉴스 목록:
{news_list}

다음 기준으로 분석해주세요:
1. 루머 내용과 뉴스의 일치성
2. 각 뉴스의 신뢰성 (높음/보통/낮음)
3. 뉴스 출처의 공신력 (공식 발표/언론사/개인/커뮤니티)
4. 사실 확인 가능성 (검증됨/부분검증/미검증/의심)
```

### Agent의 자율 판단 포인트

#### 1. 루머 판정 (4가지 중 선택)
- **사실**: 공식 발표나 신뢰할 수 있는 언론사에서 확인
- **부분 사실**: 일부는 맞지만 과장되거나 왜곡된 부분 존재
- **루머**: 근거가 없거나 허위 정보
- **검증 불가**: 충분한 정보 부족

#### 2. 전체 신뢰도 평가 (높음/보통/낮음)
- 뉴스 개수, 출처 다양성, 교차 검증 여부 종합 판단

#### 3. 확신도 점수 (1-5점, ⭐ 표시)
- ⭐⭐⭐⭐⭐: 명확한 공식 발표, 다수 언론사 확인
- ⭐⭐⭐⭐: 주요 언론사 다수 보도
- ⭐⭐⭐: 일반 언론사 보도, 일부 확인
- ⭐⭐: 단일 출처, 부분 확인
- ⭐: 불확실, 검증 불가

#### 4. 근거 분석
- **사실 근거**: 루머를 뒷받침하는 명확한 증거
- **의심 요소**: 모순되거나 불명확한 부분
- **추가 확인 필요**: 추가 조사가 필요한 항목

### LangChain 체인 구조 (ai_analyzer.py:68-76)

```python
prompt_template = PromptTemplate(
    template=prompts['rumor_verification']['template'],
    input_variables=['rumor_text', 'company_name', 'news_list', 'analysis_details']
)

chain = prompt_template | self.llm

result = chain.invoke({
    "rumor_text": rumor_text,
    "company_name": company_name,
    "news_list": news_list,
    "analysis_details": analysis_details
})
```

### 출력 형식 (Markdown)

```markdown
## 🔍 "삼성전자 이재용이 자사주 매입했다는 거 사실이야?" 루머 검증 분석

### 뉴스 신뢰성 분석
1. 삼성전자 5000억 자사주 매입 → 신뢰도: 높음, 출처: 공식, 검증: 검증됨
2. 증권가 분석 → 신뢰도: 보통, 출처: 언론, 검증: 부분검증

### 🎯 루머 검증 결과
- **전체 신뢰도**: 높음
- **루머 판정**: **사실**
- **확신도**: ⭐⭐⭐⭐⭐ (5점 만점)

### 📋 근거 분석
- **사실 근거**: 삼성전자 공식 발표 확인, 주요 언론사 다수 보도
- **의심 요소**: 없음
- **추가 확인 필요**: 자사주 매입 규모 및 일정

### 🚨 결론
해당 정보는 삼성전자의 공식 발표를 통해 확인된 사실입니다.
주요 언론사에서도 일제히 보도하고 있어 신뢰도가 높습니다.

**공식 발표나 신뢰할 수 있는 언론사의 확인이 필요합니다.**
```

### 코드 위치
- `src/ai_analyzer.py:62-79` (`verify_rumor()`)
- 호출: `main.py:149` (/auto-verify), `main.py:247` (/verify)

---

## Agent 간 데이터 전달 흐름

### 전체 데이터 파이프라인

```python
# 1단계: 회사명 추출
user_query = "삼전 자사주 매입 사실이야?"
    ↓
company_name = company_extractor.extract_company_from_query(user_query)
# company_name = "삼성전자"

# 2단계: 뉴스 검색 (Agent 아님)
news_results = news_searcher.search_stock_news(company_name, display=10)
    ↓
# 뉴스 포맷팅
news_list = ""
news_data = []
for item in news_results['items']:
    formatted = news_searcher.format_news_item(item)
    news_list += f"제목: {formatted['title']}\n내용: {formatted['description']}\n"
    news_data.append(formatted)

# 3단계: AI 분석 (2단계 Agent)
verification_result = ai_analyzer.verify_rumor(
    rumor_text=user_query,
    company_name=company_name,
    news_list=news_list  # ← 이 안에서 _analyze_news_details() 호출
)

# 4단계: 결과 저장 (Agent 아님)
result_storage.save_verification_result(
    rumor_text=user_query,
    company_name=company_name,
    news_data=news_data,
    final_result=verification_result,
    status="success"
)
```

---

## 에러 처리 및 백업 전략

### CompanyExtractor Agent
```python
try:
    llm = ChatClovaX(model="HCX-007", temperature=0.1)
except:
    # Clova 실패 시 Gemini로 자동 백업
    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
```
**위치**: `src/company_extractor.py:24-35`

### AIAnalyzer Agent
```python
try:
    result = chain.invoke({...})
    return result.content
except Exception as e:
    logger.error(f"루머 검증 중 오류: {e}")
    return f"❌ 루머 검증 중 오류 발생: {str(e)}"
```
**위치**: `src/ai_analyzer.py:64-79`

### 프롬프트 로드 실패
```python
try:
    with open(prompts_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
except Exception as e:
    logger.error(f"프롬프트 파일 로드 실패: {e}")
    return {}  # 빈 딕셔너리 반환
```
**위치**: `src/ai_analyzer.py:30-38`

---

## 상태별 Agent 행동

### 1. 회사명 추출 실패 (no_company)
```python
if not extracted_company:
    return RumorVerificationResponse(
        company_name="추출실패",
        verification_result="❌ 텍스트에서 회사명을 찾을 수 없습니다.",
        status="no_company"
    )
```
**위치**: `main.py:102-110`

### 2. 뉴스 없음 (no_news)
```python
if not news_results or len(news_results['items']) == 0:
    return RumorVerificationResponse(
        verification_result="❌ 관련 뉴스를 찾을 수 없습니다.",
        status="no_news"
    )
```
**위치**: `main.py:121-129`

### 3. 정상 처리 (success)
```python
# AI 분석 실행
verification_result = ai_analyzer.verify_rumor(...)

# 결과 저장
saved_file_path = result_storage.save_verification_result(...)

return RumorVerificationResponse(
    verification_result=verification_result,
    status="success",
    saved_file_path=saved_file_path
)
```
**위치**: `main.py:149-172`

### 4. 예외 발생 (error)
```python
except Exception as e:
    error_msg = f"분석 중 오류 발생: {str(e)}"
    logger.error(f"❌ {error_msg}")

    return RumorVerificationResponse(
        verification_result=f"❌ {error_msg}",
        status="error"
    )
```
**위치**: `main.py:174-187`

---

## 프롬프트 엔지니어링 전략

### 1. JSON 강제 출력 (CompanyExtractor)
```
- 반드시 JSON 객체 형식으로만 답변해야 합니다.
- 어떤 설명도 추가하지 말고, JSON 객체만 반환하세요.
```
**효과**: LLM이 추가 설명 없이 정확히 파싱 가능한 JSON만 출력

### 2. 정규화 규칙 내장 (CompanyExtractor)
```
# 회사명 정규화 규칙 (줄임말을 정식명칭으로 변환)
- "삼전" → "삼성전자"
- "lg엔솔" → "LG에너지솔루션"
```
**효과**: Few-shot learning 방식으로 정규화 패턴 학습

### 3. 역할 명시 (AIAnalyzer)
```
당신은 전문 팩트체킹 분석가이자 루머 검증 전문가입니다.
```
**효과**: LLM이 전문가 페르소나로 더 정확한 판단

### 4. 출력 형식 강제 (AIAnalyzer)
```yaml
### 🎯 루머 검증 결과
- **전체 신뢰도**: (높음/보통/낮음)
- **루머 판정**: **사실** / **부분 사실** / **루머** / **검증 불가**
```
**효과**: 구조화된 일관성 있는 응답 보장

### 5. 분석 기준 명시 (AIAnalyzer)
```
다음 기준으로 분석해주세요:
1. 루머 내용과 뉴스의 일치성
2. 각 뉴스의 신뢰성
3. 뉴스 출처의 공신력
4. 사실 확인 가능성
```
**효과**: Agent의 판단 기준 명확화

---

## Agent 성능 최적화

### Temperature 설정 전략

| Agent | Temperature | 이유 |
|-------|------------|------|
| CompanyExtractor (Clova) | 0.1 | 정확한 추출 우선, 창의성 불필요 |
| CompanyExtractor (Gemini) | 0.3 | 백업용, 약간의 유연성 허용 |
| AIAnalyzer | 0.3 | 분석의 일관성과 약간의 유연성 균형 |

**설정 위치**:
- `src/company_extractor.py:27`
- `config/settings.py:18`

### LLM 선택 전략

**CompanyExtractor**: Clova HCX-007 우선
- 이유: 한국어 회사명 처리에 특화
- 백업: Google Gemini (안정성)

**AIAnalyzer**: Google Gemini 2.0 Flash
- 이유: 복잡한 추론 능력, 긴 컨텍스트 처리

---

## 데이터 변환 과정

### 뉴스 데이터 변환 파이프라인

```python
# 원본 (Naver API)
{
    "title": "삼성전자, <b>자사주</b> 5000억 매입",
    "description": "<b>삼성</b>전자가...",
    "pubDate": "Wed, 31 Jan 2025 12:00:00 +0900"
}
    ↓ format_news_item() (news_searcher.py:72-81)
    ↓
# 포맷팅
{
    "title": "삼성전자, 자사주 5000억 매입",  # HTML 태그 제거
    "description": "삼성전자가...",
    "formatted_date": "2025-01-31 12:00"  # 날짜 포맷 변환
}
    ↓ news_list 문자열 생성 (main.py:133-138)
    ↓
# AI 입력용 텍스트
"""
1. 제목: 삼성전자, 자사주 5000억 매입
   내용: 삼성전자가...
   날짜: 2025-01-31 12:00
"""
    ↓ AI 분석
    ↓
# 저장용 구조화 데이터 (main.py:140-146)
{
    "title": "삼성전자, 자사주 5000억 매입",
    "description": "삼성전자가...",
    "link": "https://...",
    "pub_date": "Wed, 31 Jan 2025 12:00:00 +0900",
    "formatted_date": "2025-01-31 12:00"
}
```

---

## 핵심 파일 위치

| 파일 | 역할 | 주요 함수 |
|------|------|----------|
| `src/company_extractor.py` | CompanyExtractor Agent | `extract_company_from_query()` (37-84) |
| `src/ai_analyzer.py` | AIAnalyzer Agent | `verify_rumor()` (62-79)<br>`_analyze_news_details()` (81-99) |
| `src/news_searcher.py` | 뉴스 검색 (Agent 아님) | `search_stock_news()` (53-56)<br>`format_news_item()` (72-81) |
| `src/result_storage.py` | 결과 저장 (Agent 아님) | `save_verification_result()` (30-83) |
| `prompts/prompts.yaml` | AI 프롬프트 템플릿 | `rumor_verification` (10-52) |
| `config/settings.py` | LLM 설정 | `LLM_MODEL`, `LLM_TEMPERATURE` |
| `main.py` | Agent 오케스트레이션 | `/auto-verify` (82-188)<br>`/verify` (190-286) |

---

## 결론

이 시스템은 3개의 독립적인 AI Agent가 협력하여 루머를 검증합니다:

1. **CompanyExtractor Agent**: 자연어에서 회사명을 정확히 추출하고 정규화
2. **AIAnalyzer Agent (1단계)**: 뉴스 신뢰성을 개별 평가
3. **AIAnalyzer Agent (2단계)**: 종합 분석으로 최종 판정

각 Agent는 명확한 역할과 판단 기준을 가지며, 프롬프트 엔지니어링을 통해 일관성 있는 결과를 생성합니다.
