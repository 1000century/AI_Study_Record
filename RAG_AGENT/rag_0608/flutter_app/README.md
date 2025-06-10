# flutter_app

**로컬에 저장된 문서들의 임베딩**을 활용한 RAG 시스템

<img src="demo.gif" alt="데모" height="600">

---

## 디렉토리 구조

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

## 환경 변수 (`.env`)

```env
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

## 의존성 (`pubspec.yaml`)
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

## 주요 로직 (`lib/utils/rag_service.dart`)
- `init()` : 로컬 DB가 없을 경우 assets/documents.db를 앱 디렉토리에 복사 후 연결

- `searchRelevantChunks(String query)` : 사용자의 질문에 대해 OpenAI Embedding API로 임베딩 생성
로컬 DB에서 각 문서 chunk와의 코사인 유사도를 계산
유사도가 높은 상위 5개를 반환
  ```dart
  Future<List<Map<String, dynamic>>> searchRelevantChunks(String query) async {
    final queryEmbedding = await _getEmbedding(query);
    List<Map<String, dynamic>> scored = [];

    // 전체 문서 개수 조회
    final countResult = await _db.rawQuery('SELECT COUNT(*) as count FROM documents');
    final totalCount = Sqflite.firstIntValue(countResult) ?? 0;

    const int batchSize = 1000;
    int offset = 0;

    // 배치 반복
    while (offset < totalCount) {
      final batch = await _db.query(
        'documents',
        columns: ['text', 'embedding'],
        limit: batchSize,
        offset: offset,
      );

      for (final row in batch) {
        final text = row['text'] as String;
        final rawEmbedding = row['embedding'];

        try {
          final embedding = List<double>.from(json.decode(rawEmbedding as String));
          final score = _cosineSimilarity(queryEmbedding, embedding);
          scored.add({'text': text, 'score': score});
        } catch (e) {
          print("Failed to parse embedding: $e");
        }
      }

      offset += batchSize;
    }

    // 유사도 기준 정렬 후 상위 10개 반환
    scored.sort((a, b) => b['score'].compareTo(a['score']));
    return scored.take(10).toList();
  }
  ```


- `generateAnswer(String question, List<String> contexts)` : Google Gemini API를 사용하여, 문맥 + 질문을 기반으로 포괄적인 답변 생성

- `_getEmbedding(String text)` : OpenAI text-embedding-3-small 모델 호출하여 입력 텍스트 임베딩 생성
  ```dart
  Future<List<double>> _getEmbedding(String text) async {
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/embeddings'),
      headers: {
        'Authorization': 'Bearer $_openAiApiKey',
        'Content-Type': 'application/json'
      },
      body: json.encode({
        'input': text,
        'model': 'text-embedding-3-small'
      }),
    );

    final data = json.decode(response.body);
    return List<double>.from(data['data'][0]['embedding']);
  }
  ```

## 홈 UI (lib/ui/home_page.dart)
### 핵심 기능

- 텍스트 입력을 받고 `RAGService.searchRelevantChunks()` → `generateAnswer()` 호출
- 결과를 UI에 표시


## 실행 방법

1. .env 파일 생성 및 API 키 입력
2. 의존성 설치
    ```
    flutter pub get
    ```

3. 에뮬레이터 or 실제 디바이스에서 실행
    ```
    flutter run
    ```


## 참고 사항

- DB는 `documents 테이블`에 `text`, `embedding` 컬럼이 있어야 하며, **embedding은 JSON 배열**로 저장되어야 함
- 
