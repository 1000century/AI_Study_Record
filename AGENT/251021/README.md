# LangGraph Counter Agent

LangGraph를 사용한 간단한 카운터 에이전트 예제

## 파일 구조

| 파일 | 설명 |
|------|------|
| `graph.py` | LangGraph 워크플로우 정의 |
| `langgraph.json` | LangGraph 설정 |
| `__init__.py` | 패키지 초기화 |

## 워크플로우

```
Start → Increment → [count < 5?]
                        ├─ Yes → Double → End
                        └─ No → End
```

## State

| 필드 | 타입 | 설명 |
|------|------|------|
| `count` | `int` | 현재 카운트 값 |
| `messages` | `list[str]` | 실행 로그 |

## 노드

| 노드 | 동작 |
|------|------|
| `start` | 시작, "Started" 메시지 추가 |
| `increment` | count + 1 |
| `double` | count * 2 |
| `end` | 종료, "Finished" 메시지 추가 |

## 실행 방법

### 1. LangGraph Studio (개발 서버)

```bash
langgraph dev
```

- Studio UI에서 그래프 시각화 및 테스트
- `langgraph.json` 설정 자동 로드

### 2. Python 코드

```python
from graph import graph

result = graph.invoke({"count": 0, "messages": []})
print(f"Final: {result['count']}")  # 4
```

## 실행 결과

| 초기 count | 최종 count | 경로 |
|-----------|-----------|------|
| 0 | 4 | Start → Inc(1) → Double(2) → End |
| 2 | 6 | Start → Inc(3) → Double(6) → End |
| 4 | 5 | Start → Inc(5) → End |

## 설치

```bash
pip install langgraph
```
