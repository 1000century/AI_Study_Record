# 1. test 폴더

- google adk web으로 실행해보기 

```cmd
adk web
```



# 2. agent_study.py

## 📋 목차
1. [환경 설정](#환경-설정)
2. [핵심 컴포넌트](#핵심-컴포넌트)
3. [코드 구조](#코드-구조)
4. [실행 결과](#실행-결과)
5. [동작 원리](#동작-원리)

---

## 환경 설정

### 프로젝트 정보
- **경로**: `C:\Users\Sese\AI_Study_Record\AGENT\1002\test`
- **실행**: `python agent.py`
- **가상환경**: `venv` 활성화

### 주요 의존성
```python
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
```

---

## 핵심 컴포넌트

| 컴포넌트 | 클래스/타입 | 역할 | 주요 속성/메서드 |
|---------|------------|------|----------------|
| **Agent** | `Agent` | LLM 기반 에이전트 | `model`, `name`, `description`, `instruction` |
| **Model** | `LiteLlm` | 외부 LLM 연결 | `model`, `api_key`, `api_base` |
| **Session Service** | `InMemorySessionService` | 세션 관리 (메모리) | `create_session()` |
| **Runner** | `Runner` | 에이전트 실행 엔진 | `run_async()` |
| **Event** | `Event` | 실행 중 발생 이벤트 | `author`, `is_final_response()`, `content` |

---

## 코드 구조

### 1. Agent 초기화

```python
root_agent = Agent(
    model=LiteLlm(
        model='openai/HCX-007',
        api_key='<API_KEY>',
        api_base='https://clovastudio.stream.ntruss.com/v1/openai'
    ),
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
```

| 파라미터 | 값 | 설명 |
|---------|---|------|
| `model` | `openai/HCX-007` | Naver Clova Studio 모델 |
| `api_base` | `https://clovastudio.stream.ntruss.com/v1/openai` | API 엔드포인트 |
| `name` | `root_agent` | 에이전트 식별자 |
| `instruction` | 사용자 질문에 답변 | 시스템 프롬프트 |

### 2. Session 설정

```python
session_service = InMemorySessionService()
USER_ID = "sese_1234"
SESSION_ID = "session_1234"
```

### 3. Runner 생성

```python
runner = Runner(
    agent=root_agent,
    app_name="데모",
    session_service=session_service
)
```

### 4. 비동기 실행 함수

```python
async def call_agent_async(query:str, runner, user_id:str, session_id:str):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    async for event in runner.run_async(
        user_id=user_id, 
        session_id=session_id, 
        new_message=content
    ):
        if event.is_final_response():
            final_response_text = event.content.parts[0].text
            break
```

---

## 실행 결과

### 테스트 시나리오

| 순서 | 질문 | 언어 | 목적 |
|-----|------|------|------|
| 1 | "런던의 날씨는 어때?" | 한국어 | 초기 질문 |
| 2 | "How about Paris?" | 영어 | 컨텍스트 유지 확인 |
| 3 | "지금까지 내 질문들을 요약해" | 한국어 | 메모리 테스트 |

### 실행 결과 상세

#### 1차 질문: "런던의 날씨는 어때?"

```
[Event] Author: root_agent, Type: Event, Final: True
```

| 속성 | 값 |
|-----|---|
| Author | `root_agent` |
| Type | `Event` |
| Final | `True` |
| Content | 런던 계절별 날씨 정보 (1~7°C 겨울, 10~15°C 봄 등) |

**응답 특징**:
- 실시간 날씨 정보 제공 불가 명시
- 계절별 일반적인 기후 정보 제공
- 외부 사이트 (BBC Weather, AccuWeather) 추천

#### 2차 질문: "How about Paris?"

```
[Event] Author: root_agent, Type: Event, Final: True
```

| 속성 | 값 |
|-----|---|
| Author | `root_agent` |
| Type | `Event` |
| Final | `True` |
| Content | 파리 해양성 기후, 계절별 특징 (-2~7°C 겨울, 15~25°C 여름) |

**컨텍스트 유지 확인**:
- ✅ "How about Paris?" 만으로 날씨 질문임을 이해
- ✅ 이전 질문("런던 날씨")의 문맥을 기억
- ✅ 추가 설명 없이 파리 날씨 정보 제공

#### 3차 질문: "지금까지 내 질문들을 요약해"

```
[Event] Author: root_agent, Type: Event, Final: True
```

| 속성 | 값 |
|-----|---|
| Author | `root_agent` |
| Type | `Event` |
| Final | `True` |
| Content | 이전 2개 질문 요약 (런던/파리 날씨) |

**메모리 동작 확인**:
```
사용자의 최근 질문 요약:
1. 런던 날씨 문의
   → 해양성 기후로 겨울(-2~7°C), 봄/가을(5~15°C), 여름(15~20°C)
   → 흐린 날 많고 갑작스런 비/안개 흔함

2. 파리 날씨 문의
   → 겨울(-2~7°C), 여름(15~25°C) 중심
   → 연평균 600mm 강수량

공통점: 두 도시 모두 변덕스러운 날씨
```

---

## 동작 원리

### Event 처리 흐름

```mermaid
graph TD
    A[User Query] --> B[Runner.run_async]
    B --> C[Event Stream 생성]
    C --> D{Event Loop}
    D --> E[Event 수신]
    E --> F{is_final_response?}
    F -->|No| D
    F -->|Yes| G[최종 응답 추출]
    G --> H[event.content.parts[0].text]
```

### Session Memory 동작

```
Session: session_1234
├── Message 1: "런던의 날씨는 어때?"
│   └── Response: [런던 날씨 정보]
├── Message 2: "How about Paris?"
│   └── Response: [파리 날씨 정보] ← 컨텍스트 유지
└── Message 3: "지금까지 내 질문들을 요약해"
    └── Response: [1, 2번 질문 요약] ← 메모리 활용
```

### Event 객체 구조

| 속성 | 타입 | 설명 | 예시 |
|-----|------|------|------|
| `author` | `str` | 이벤트 생성자 | `"root_agent"` |
| `type` | `str` | 이벤트 타입 | `"Event"` |
| `is_final_response()` | `bool` | 최종 응답 여부 | `True` / `False` |
| `content` | `Content` | 응답 내용 객체 | `parts=[Part(text="...")]` |
| `content.parts` | `list[Part]` | 응답 파트 리스트 | `[Part(text="응답 텍스트")]` |
| `content.role` | `str` | 역할 | `"model"` |
| `actions` | `Actions` | 액션 정보 | `escalate` 등 |
| `error_message` | `str` | 에러 메시지 | 에러 발생 시 |

---

## 핵심 학습 포인트

### ✅ Session Memory
- `InMemorySessionService`가 대화 히스토리를 메모리에 저장
- 동일 `SESSION_ID`로 여러 턴의 대화 컨텍스트 유지
- 3번째 질문에서 1, 2번째 내용을 정확히 기억하고 요약

### ✅ Event Stream
- `run_async()`는 `AsyncGenerator` 반환
- `async for` 루프로 이벤트 순차 처리
- `is_final_response()`로 최종 응답 식별

### ✅ Context Awareness
- "How about Paris?"만으로 날씨 질문임을 이해
- 이전 대화 흐름을 자동으로 파악
- 명시적 컨텍스트 전달 불필요

### ✅ Multi-turn Conversation
- 단일 세션 내 연속 대화 지원
- 각 질문이 독립적이지 않고 연결됨
- 대화 히스토리 기반 응답 생성

---

## 코드 실행 패턴

### 전체 실행 흐름

```python
# 1. Session 생성
session = await session_service.create_session(
    app_name="데모",
    user_id=USER_ID,
    session_id=SESSION_ID
)

# 2. 첫 번째 대화
await call_agent_async("런던의 날씨는 어때?", runner, USER_ID, SESSION_ID)
# → Session에 저장됨

# 3. 두 번째 대화 (컨텍스트 유지)
await call_agent_async("How about Paris?", runner, USER_ID, SESSION_ID)
# → Session에서 이전 대화 참조

# 4. 세 번째 대화 (메모리 활용)
await call_agent_async("지금까지 내 질문들을 요약해", runner, USER_ID, SESSION_ID)
# → Session에서 전체 히스토리 조회
```

### 비동기 처리 구조

| 단계 | 함수 | 동작 | 반환 |
|-----|------|------|------|
| 1 | `run_conversation()` | 전체 대화 시나리오 실행 | `None` |
| 2 | `call_agent_async()` | 단일 질문 처리 | `None` |
| 3 | `runner.run_async()` | Agent 실행 | `AsyncGenerator[Event]` |
| 4 | Event Loop | 이벤트 순회 처리 | 최종 응답 텍스트 |

---

## 추가 발견 사항

### Event 출력 형식
```
[Event] Author: root_agent, Type: Event, Final: True, Content: parts=[Part(text="...")]
```
- Author: 항상 `root_agent` (정의된 에이전트 이름)
- Type: `Event` (기본 이벤트 타입)
- Final: 중간 이벤트는 `False`, 최종 응답만 `True`
- Content: `Content` 객체로 `parts` 리스트와 `role` 포함

### 응답 추출 로직
```python
if event.is_final_response():
    if event.content and event.content.parts:
        final_response_text = event.content.parts[0].text
    elif event.actions and event.actions.escalate:
        final_response_text = f"Agent escalated: {event.error_message}"
```

**처리 우선순위**:
1. 정상 응답: `event.content.parts[0].text`
2. Escalation: `event.actions.escalate` 확인
3. 기본값: "에이전트는 마지막 응답을 생성하지 못했습니다."

---

## 결론

### 검증된 기능
| 기능 | 상태 | 비고 |
|-----|------|------|
| Agent 초기화 | ✅ | LiteLlm 모델 연결 성공 |
| Session 생성 | ✅ | InMemory 방식 동작 |
| Event Stream | ✅ | 비동기 이벤트 수신 |
| Context 유지 | ✅ | 2번째 질문에서 확인 |
| Memory 활용 | ✅ | 3번째 질문에서 요약 성공 |
| Multi-turn | ✅ | 3회 연속 대화 정상 동작 |
| 다국어 | ✅ | 한국어/영어 혼용 가능 |

### 학습 완료 항목
- ✅ Google ADK의 Agent-Session-Runner 구조 이해
- ✅ Event 기반 비동기 처리 패턴
- ✅ InMemorySessionService의 메모리 동작 방식
- ✅ Multi-turn conversation 구현 방법
- ✅ LiteLlm을 통한 외부 모델 연동