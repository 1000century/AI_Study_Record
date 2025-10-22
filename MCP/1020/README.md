| 날짜 | 주제 | 내용 | 기술 스택 |
|------|------|------|----------|
| 2025-10-20 | Notion MCP 직접 호출 | LLM 없이 Python에서 MCP 서버에 직접 HTTP 요청, JSON-RPC 2.0으로 도구 호출 | Python, requests, Notion MCP, JSON-RPC 2.0 |

---

# Notion MCP (Model Context Protocol) 학습 기록

## 학습 개요

MCP(Model Context Protocol)는 보통 LLM이 중간에서 도구를 선택하고 호출하는 프로토콜이다. 하지만 이번 학습에서는 **LLM 없이 Python에서 직접 MCP 서버에 요청**을 보내는 방법을 공부했다.

**학습 내용:**
- Notion MCP 서버(`https://mcp.notion.com/mcp`)에 HTTP 요청으로 직접 통신
- JSON-RPC 2.0 프로토콜을 사용해 도구 목록 조회 및 호출
- Notion 페이지 내용을 프로그래밍 방식으로 수정

## MCP 요청 방법

**Base URL:** `https://mcp.notion.com/mcp`

| 단계 | 메서드 | 설명 |
|------|--------|------|
| 1 | `initialize` | 세션 ID 발급 (응답 헤더에서 `Mcp-Session-Id` 획득) |
| 2 | `tools/list` | 사용 가능한 도구 목록 조회 |
| 3 | `tools/call` | 특정 도구 호출 (예: 페이지 수정) |

---

### 1. Initialize (세션 ID 발급)

**URL:** `https://mcp.notion.com/mcp`

```python
import requests

url = "https://mcp.notion.com/mcp"
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}
payload = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {
            "name": "manual-client",
            "version": "1.0"
        }
    },
    "id": 1
}

response = requests.post(url, json=payload, headers=headers)
session_id = response.headers.get("Mcp-Session-Id")
```

**응답:** `Mcp-Session-Id` 헤더에서 세션 ID 획득

---

### 2. Tools List (도구 목록 조회)

**URL:** `https://mcp.notion.com/mcp`

```python
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Mcp-Session-Id": session_id,
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}
payload = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
}

response = requests.post(url, json=payload, headers=headers)
```

---

### 3. Tools Call (도구 호출 - 페이지 수정)

**URL:** `https://mcp.notion.com/mcp`

```python
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Mcp-Session-Id": session_id,
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "notion-update-page",
        "arguments": {
            "data": {
                "page_id": PAGE_ID,
                "command": "replace_content",
                "new_str": "# I changed text."
            }
        }
    },
    "id": "32323232323"
}

response = requests.post(url, json=payload, headers=headers)
```

**사용 가능한 command:**
- `replace_content`: 페이지 전체 내용 교체
- `replace_content_range`: 특정 범위 내용 교체
- `insert_content_after`: 특정 위치 이후에 내용 삽입
- `update_properties`: 페이지 속성 업데이트

---

## 작성한 코드

### 1. `list_tools.py`
MCP 서버에서 사용 가능한 도구 목록을 조회하는 코드

**기능:**
- 세션 초기화
- 도구 목록 조회
- `notion-update-page` 도구 스키마 출력
- 결과를 `list_tools_결과.json`에 저장

### 2. `check_tool.py`
Notion 페이지 내용을 실제로 수정하는 코드

**기능:**
- `notion-update-page` 도구 호출
- 페이지 전체 내용을 "# I changed text."로 교체

**실행 결과:**

| 파일명 | 설명 |
|--------|------|
| `check_tool_결과.gif` | ![check_tool 실행 과정](check_tool_결과.gif) |

### 3. `.env` (환경 변수 설정)

```env
ACCESS_TOKEN=your_notion_access_token
PAGE_ID=your_page_id
```

---

## 학습 정리

### MCP 통신 흐름

1. **Initialize** → `Mcp-Session-Id` 헤더로 세션 ID 받기
2. **Tools List** → 사용 가능한 도구 목록 확인
3. **Tools Call** → 원하는 도구 호출 (예: 페이지 수정)

### 핵심 포인트

- **MCP URL:** `https://mcp.notion.com/mcp`
- **프로토콜:** JSON-RPC 2.0
- **인증:** Bearer Token (Authorization 헤더)
- **세션 관리:** `Mcp-Session-Id` 헤더로 세션 유지
- **응답 형식:** Server-Sent Events (SSE)
