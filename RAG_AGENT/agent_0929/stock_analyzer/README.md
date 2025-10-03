# 🔍 Rumor Verification API

기업 루머 및 뉴스 팩트체킹 AI 분석 시스템

## 개요

실시간 뉴스 데이터를 기반으로 기업 관련 루머의 사실 여부를 검증하는 AI 시스템입니다. 네이버 뉴스 API를 통해 최신 뉴스를 수집하고, Google Gemini AI를 활용하여 팩트체킹을 수행합니다.

## 주요 기능

- 🔍 **루머 검증**: 특정 루머 내용과 회사명을 입력하면 사실 여부 판단
- 🤖 **회사명 자동 추출**: AI가 텍스트에서 회사명을 자동으로 감지 및 정규화
- 📰 **뉴스 수집**: 네이버 뉴스 API를 통한 실시간 뉴스 검색
- 🧠 **AI 분석**: Google Gemini를 활용한 신뢰성 있는 팩트체킹
- 📊 **신뢰도 평가**: 뉴스 출처 공신력 및 확신도 평가
- 💾 **자동 저장**: 모든 검증 결과와 수집된 뉴스 데이터 자동 저장
- 🔎 **결과 조회**: 과거 검증 결과 검색 및 조회 기능

## 빠른 시작

### 1. 회사명 자동 추출 루머 검증 (권장)
```bash
curl -X POST "http://localhost:9000/auto-verify" \
     -H "Content-Type: application/json" \
     -d '{
       "rumor_text": "삼성전자 이재용이 자사주 매입했다는 거 사실이야?",
       "news_count": 10
     }'
```

**특징**: AI가 자동으로 회사명을 추출하고 정규화합니다 ("삼전" → "삼성전자", "lg엔솔" → "LG에너지솔루션")

### 2. 회사명 직접 지정 루머 검증
```bash
curl -X POST "http://localhost:9000/verify" \
     -H "Content-Type: application/json" \
     -d '{
       "rumor_text": "자사주 매입했다는 거 사실이야?",
       "company_name": "삼성전자",
       "news_count": 10
     }'
```

### 응답 예시
```json
{
  "rumor_text": "삼성전자 이재용이 자사주 매입했다는 거 사실이야?",
  "company_name": "삼성전자",
  "verification_result": "## 🔍 \"삼성전자 이재용이 자사주 매입했다는 거 사실이야?\" 루머 검증 분석\n\n### 🎯 루머 검증 결과\n- **전체 신뢰도**: 높음\n- **루머 판정**: **사실**\n- **확신도**: ⭐⭐⭐⭐⭐ (5점 만점)\n\n### 📋 근거 분석\n- **사실 근거**: 공식 보도자료 확인됨\n- **의심 요소**: 없음\n- **추가 확인 필요**: 매입 규모 및 시기\n\n### 🚨 결론\n해당 정보는 공식 발표를 통해 확인된 사실입니다.",
  "news_count": 10,
  "status": "success",
  "timestamp": "2025-01-31T12:00:00",
  "saved_file_path": "verification_results/2025-01-31/삼성전자_120000_abc12345.json"
}
```

### 3. 기타 API
```bash
# 최근 검증 결과 조회
curl http://localhost:9000/recent

# 회사명으로 검색
curl "http://localhost:9000/search?company_name=삼성전자"

# 특정 검증 결과 상세 조회
curl http://localhost:9000/verification/abc12345
```

> 📖 **전체 API 명세는 [API.md](API.md) 참고**

## 설치 및 실행

### 1. 환경 설정
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성)
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
GOOGLE_API_KEY=your_google_api_key
```

### 2. 서버 실행
```bash
python main.py
```

서버는 기본적으로 `http://localhost:9000`에서 실행됩니다.

### 3. CLI 모드 (선택)
```bash
# 기본 사용법
python main.py "루머 내용" "회사명"

# 예시
python main.py "삼성전자 이재용이 자사주 매입했다는 거 사실이야?" "삼성전자"
```

## 프로젝트 구조

```
stock_analyzer/
├── main.py                     # FastAPI 서버 메인 파일
├── src/
│   ├── company_extractor.py    # 회사명 자동 추출 모듈 (AI)
│   ├── news_searcher.py        # 네이버 뉴스 검색 모듈
│   ├── ai_analyzer.py          # AI 루머 분석 모듈 (Google Gemini)
│   └── result_storage.py       # 검증 결과 저장 모듈
├── config/
│   └── settings.py             # 설정 파일
├── prompts/
│   └── prompts.yaml            # AI 프롬프트 템플릿
├── verification_results/       # 검증 결과 저장 폴더 (자동 생성)
│   ├── index.json              # 검색용 인덱스 파일
│   └── 2025-01-31/             # 날짜별 폴더
│       └── 삼성전자_120000_abc12345.json
└── requirements.txt            # 의존성 목록
```

## 핵심 기술

- **회사명 정규화**: "삼전" → "삼성전자", "lg엔솔" → "LG에너지솔루션" 등 자동 변환
- **멀티 LLM**: Clova HCX-007 또는 Google Gemini 백업 지원
- **실시간 뉴스 분석**: 네이버 뉴스 API를 통한 최신 정보 수집
- **구조화된 저장**: 날짜별 자동 분류 및 인덱싱

## 판정 기준

**루머 판정 유형**: 사실 | 부분 사실 | 루머 | 검증 불가
**신뢰도 평가**: 높음 (공식 발표, 주요 언론) | 보통 (일반 언론) | 낮음 (커뮤니티, 미확인)

## 상세 문서

- 📖 [API 전체 명세서](API.md)

## 주의사항

- 이 시스템은 뉴스 기반 분석이며, 투자나 중요한 결정에는 추가적인 확인이 필요합니다
- AI 분석 결과는 참고용이며, 최종 판단은 사용자의 책임입니다
- 실시간 뉴스 데이터에 의존하므로, 최신 정보가 반영되지 않을 수 있습니다