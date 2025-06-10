# flutter_app

Flutter 기반의 모바일 앱으로, **로컬에 저장된 문서들의 임베딩**을 활용해 OpenAI 및 Google Gemini API를 이용한 질의응답 시스템을 제공합니다.

---

## 🗂 디렉토리 구조

```
flutter_app/
├── assets/
│   └── documents.db          # 사전 임베딩된 문서가 저장된 SQLite DB
├── lib/
│   ├── ui/
│   │   └── home_page.dart    # 홈 화면 UI 및 사용자 입력 처리
│   └── utils/
│       └── rag_service.dart  # 핵심 로직: DB 조회, 임베딩, 질의응답
├── .env                      # API 키가 담긴 환경 변수 파일
├── pubspec.yaml              # 의존성 및 리소스 설정
```
---

## 🔑 환경 변수 (`.env`)

```env
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

## 🔧 의존성 (`pubspec.yaml`)
```yaml
name: flutter_app

environment:
  sdk: '^3.8.0'

flutter:
  assets:
    - .env
    - assets/documents.db

dependencies:
  flutter:
    sdk: flutter
  flutter_dotenv: ^5.0.2
  http: ^0.13.5
  sqflite: ^2.3.0
  path: ^1.8.0
```

## 🧠 주요 로직 설명 (`lib/utils/rag_service.dart`)
🔹 `init()`

- 로컬 DB가 없을 경우 assets/documents.db를 앱 디렉토리에 복사 후 연결

🔹 `searchRelevantChunks(String query)`

- 사용자의 질문에 대해 OpenAI Embedding API로 임베딩 생성
로컬 DB에서 각 문서 chunk와의 코사인 유사도를 계산
유사도가 높은 상위 5개를 반환

🔹 `generateAnswer(String question, List<String> contexts)`

- Google Gemini API를 사용하여, 문맥 + 질문을 기반으로 포괄적인 답변 생성

🔹 `_getEmbedding(String text)`

- OpenAI text-embedding-3-small 모델 호출하여 입력 텍스트 임베딩 생성


## 🖥 홈 UI (lib/ui/home_page.dart)
### 핵심 기능

- 텍스트 입력을 받고 `RAGService.searchRelevantChunks()` → `generateAnswer()` 호출
- 결과를 UI에 표시


## 🚀 실행 방법

1. .env 파일 생성 및 API 키 입력
2. 의존성 설치
    ```
    flutter pub get
    ```

3. 에뮬레이터 or 실제 디바이스에서 실행
    ```
    flutter run
    ```


## 🧩 참고 사항

- DB는 `documents 테이블`에 `text`, `embedding` 컬럼이 있어야 하며, **embedding은 JSON 배열**로 저장되어야 함
- 
