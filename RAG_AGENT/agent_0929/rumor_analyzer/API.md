# API 전체 명세서

## 목차
- [루머 검증 API](#루머-검증-api)
- [조회 API](#조회-api)
- [응답 형식](#응답-형식)
- [데이터 저장 구조](#데이터-저장-구조)

---

## 루머 검증 API

### 1. 회사명 자동 추출 루머 검증 (권장)

**Endpoint**: `POST /auto-verify`

AI가 텍스트에서 회사명을 자동으로 추출하여 검증합니다.

**요청 예시**
```bash
curl -X POST "http://localhost:9000/auto-verify" \
     -H "Content-Type: application/json" \
     -d '{
       "rumor_text": "삼성전자 이재용이 자사주 매입했다는 거 사실이야?",
       "news_count": 10
     }'
```

**요청 파라미터**
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| rumor_text | string | ✅ | - | 검증할 루머 내용 |
| news_count | integer | ❌ | 10 | 검색할 뉴스 개수 (최대 100) |

**회사명 자동 정규화 규칙**
- "삼전" → "삼성전자"
- "lg엔솔", "엘지엔솔", "lg 엔솔" → "LG에너지솔루션"
- "카뱅", "카카오뱅크" → "카카오뱅크"
- "현대차" → "현대자동차"
- "sk하이닉스", "sk 하이닉스" → "SK하이닉스"
- "kakao" → "카카오"
- "naver", "네이버" → "NAVER"

**응답 예시**
```json
{
  "rumor_text": "삼성전자 이재용이 자사주 매입했다는 거 사실이야?",
  "company_name": "삼성전자",
  "verification_result": "## 🔍 루머 검증 분석\n\n### 🎯 루머 검증 결과\n- **전체 신뢰도**: 높음\n- **루머 판정**: **사실**\n- **확신도**: ⭐⭐⭐⭐⭐ (5점 만점)\n\n### 📋 근거 분석\n...",
  "news_count": 10,
  "status": "success",
  "timestamp": "2025-01-31T12:00:00",
  "saved_file_path": "verification_results/2025-01-31/삼성전자_120000_abc12345.json"
}
```

**상태 코드**
| 상태 | 설명 |
|------|------|
| success | 검증 성공 |
| no_company | 회사명 추출 실패 |
| no_news | 관련 뉴스 없음 |
| error | 서버 오류 |

---

### 2. 회사명 직접 지정 루머 검증

**Endpoint**: `POST /verify`

회사명을 직접 지정하여 루머를 검증합니다.

**요청 예시**
```bash
curl -X POST "http://localhost:9000/verify" \
     -H "Content-Type: application/json" \
     -d '{
       "rumor_text": "자사주 매입했다는 거 사실이야?",
       "company_name": "삼성전자",
       "news_count": 10
     }'
```

**요청 파라미터**
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| rumor_text | string | ✅ | - | 검증할 루머 내용 |
| company_name | string | ✅ | - | 관련 회사명 |
| news_count | integer | ❌ | 10 | 검색할 뉴스 개수 (최대 100) |

**응답 형식**: `/auto-verify`와 동일

---

## 조회 API

### 1. API 상태 확인

**Endpoint**: `GET /`

```bash
curl http://localhost:9000/
```

**응답**
```json
{
  "message": "🔍 Rumor Verification API",
  "status": "running",
  "endpoints": {
    "auto-verify": "/auto-verify - 회사명 자동 추출 루머 검증",
    "verify": "/verify - 기업 루머 검증 (회사명 직접 입력)",
    "recent": "/recent - 최근 검증 결과 조회",
    "search": "/search - 검증 결과 검색",
    "health": "/health - 헬스 체크"
  }
}
```

---

### 2. 헬스 체크

**Endpoint**: `GET /health`

```bash
curl http://localhost:9000/health
```

**응답**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-31T12:00:00"
}
```

---

### 3. 최근 검증 결과 조회

**Endpoint**: `GET /recent`

최근 검증된 결과 목록을 시간순으로 반환합니다.

**요청 예시**
```bash
# 최근 10개 결과 (기본값)
curl http://localhost:9000/recent

# 최근 5개 결과
curl http://localhost:9000/recent?limit=5
```

**쿼리 파라미터**
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| limit | integer | ❌ | 10 | 조회할 결과 개수 (최대 100) |

**응답 예시**
```json
{
  "status": "success",
  "count": 3,
  "results": [
    {
      "id": "abc12345",
      "timestamp": "2025-01-31T12:00:00",
      "rumor_text": "삼성전자 이재용이 자사주 매입했다는 거...",
      "company_name": "삼성전자",
      "filename": "삼성전자_120000_abc12345.json",
      "date": "2025-01-31"
    },
    {
      "id": "def67890",
      "timestamp": "2025-01-31T11:30:00",
      "rumor_text": "LG전자 신규 공장 설립 계획...",
      "company_name": "LG전자",
      "filename": "LG전자_113000_def67890.json",
      "date": "2025-01-31"
    }
  ]
}
```

---

### 4. 검증 결과 검색

**Endpoint**: `GET /search`

회사명이나 키워드로 과거 검증 결과를 검색합니다.

**요청 예시**
```bash
# 회사명으로 검색
curl "http://localhost:9000/search?company_name=삼성전자"

# 키워드로 검색
curl "http://localhost:9000/search?keyword=자사주"

# 회사명 + 키워드 조합 검색
curl "http://localhost:9000/search?company_name=삼성전자&keyword=매입"
```

**쿼리 파라미터**
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| company_name | string | ❌* | 검색할 회사명 |
| keyword | string | ❌* | 검색할 키워드 |

*둘 중 하나는 필수

**응답 형식**: `/recent`와 동일

**에러 응답**
```json
{
  "detail": "company_name 또는 keyword 중 하나는 필수입니다."
}
```

---

### 5. 특정 검증 결과 상세 조회

**Endpoint**: `GET /verification/{verification_id}`

특정 검증 결과의 전체 데이터를 조회합니다 (뉴스 데이터 포함).

**요청 예시**
```bash
curl http://localhost:9000/verification/abc12345
```

**응답 예시**
```json
{
  "status": "success",
  "result": {
    "id": "abc12345",
    "timestamp": "2025-01-31T12:00:00",
    "request": {
      "rumor_text": "삼성전자 이재용이 자사주 매입했다는 거 사실이야?",
      "company_name": "삼성전자",
      "news_count": 10
    },
    "news_data": [
      {
        "title": "삼성전자, 자사주 5000억원 규모 매입 결정",
        "description": "삼성전자가 주주가치 제고를 위해 자사주 매입을 결정했다...",
        "link": "https://news.naver.com/...",
        "pub_date": "Wed, 31 Jan 2025 12:00:00 +0900",
        "formatted_date": "2025-01-31 12:00"
      }
    ],
    "analysis_details": "뉴스별 신뢰성 분석 결과...",
    "final_result": "## 🔍 루머 검증 분석\n\n...",
    "status": "success",
    "metadata": {
      "total_news_found": 10,
      "processing_time": "2025-01-31T12:00:00"
    }
  }
}
```

**에러 응답 (404)**
```json
{
  "detail": "검증 결과를 찾을 수 없습니다."
}
```

---

## 응답 형식

### 검증 결과 구조

모든 루머 검증 API는 다음 형식으로 응답합니다:

```typescript
{
  rumor_text: string;          // 검증 요청한 루머 내용
  company_name: string;        // 회사명 (추출되거나 입력된 값)
  verification_result: string; // AI 분석 결과 (Markdown 형식)
  news_count: number;          // 분석에 사용된 뉴스 개수
  status: string;              // success | no_company | no_news | error
  timestamp: string;           // ISO 8601 형식
  saved_file_path?: string;    // 저장된 파일 경로 (선택)
}
```

### AI 분석 결과 형식

`verification_result` 필드는 Markdown으로 작성되며, 다음 섹션을 포함합니다:

```markdown
## 🔍 "[루머 내용]" 루머 검증 분석

### 🎯 루머 검증 결과
- **전체 신뢰도**: 높음/보통/낮음
- **루머 판정**: **사실** / **부분 사실** / **루머** / **검증 불가**
- **확신도**: ⭐⭐⭐⭐⭐ (1-5점)

### 📋 근거 분석
- **사실 근거**: [구체적 근거]
- **의심 요소**: [의심되는 부분]
- **추가 확인 필요**: [추가 확인 사항]

### 🚨 결론
[명확한 결론 및 권고사항]
```

### 판정 기준

#### 루머 판정 유형
| 판정 | 설명 |
|------|------|
| **사실** | 공식 발표나 신뢰할 수 있는 언론사에서 확인된 정보 |
| **부분 사실** | 일부는 맞지만 과장되거나 왜곡된 부분이 있는 정보 |
| **루머** | 근거가 없거나 허위인 정보 |
| **검증 불가** | 충분한 정보가 없어 판단하기 어려운 경우 |

#### 신뢰도 평가
| 신뢰도 | 설명 |
|--------|------|
| **높음** | 공식 발표, 주요 언론사 보도, 다수의 교차 검증된 출처 |
| **보통** | 일반 언론사, 부분적 확인 가능 |
| **낮음** | 개인 블로그, 커뮤니티, 미확인 정보, 단일 출처 |

---

## 데이터 저장 구조

### 저장 파일 형식

검증 결과는 JSON 파일로 저장되며, 다음 구조를 따릅니다:

```json
{
  "id": "abc12345",
  "timestamp": "2025-01-31T12:00:00",
  "request": {
    "rumor_text": "루머 내용",
    "company_name": "회사명",
    "news_count": 10
  },
  "news_data": [
    {
      "title": "뉴스 제목",
      "description": "뉴스 내용 요약",
      "link": "뉴스 링크",
      "pub_date": "발행일",
      "formatted_date": "2025-01-31 12:00"
    }
  ],
  "analysis_details": "개별 뉴스 분석 결과",
  "final_result": "AI 루머 검증 최종 결과",
  "status": "success",
  "metadata": {
    "total_news_found": 10,
    "processing_time": "2025-01-31T12:00:00"
  }
}
```

### 디렉토리 구조

```
verification_results/
├── index.json              # 검색용 인덱스 (최근 100개)
├── 2025-01-31/             # 날짜별 폴더
│   ├── 삼성전자_120000_abc12345.json
│   └── LG전자_113000_def67890.json
└── 2025-02-01/
    └── 현대차_140000_ghi11111.json
```

### 저장 시스템 특징

- 📅 **날짜별 분류**: 검증 날짜별로 폴더 자동 생성
- 🔍 **빠른 검색**: 인덱스 파일을 통한 효율적인 검색
- 📊 **완전한 기록**: 요청부터 결과까지 모든 과정 저장
- 🏷️ **고유 ID**: 각 검증마다 고유 식별자 부여 (UUID 8자리)

---

## 에러 처리

### HTTP 상태 코드

| 코드 | 설명 |
|------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (필수 파라미터 누락 등) |
| 404 | 리소스를 찾을 수 없음 |
| 500 | 서버 내부 오류 |

### 에러 응답 형식

```json
{
  "detail": "오류 메시지"
}
```

---

## 사용 제한

- 뉴스 검색 최대 개수: 100개
- 인덱스 파일 최대 저장: 100개 (자동 정리)
- API Rate Limit: 네이버 API 정책 준수

---

## 기술 스택

- **Web Framework**: FastAPI
- **LLM**: Google Gemini 2.0 Flash / Clova HCX-007
- **News API**: Naver Search API
- **Storage**: JSON 파일 기반
- **Language**: Python 3.8+
