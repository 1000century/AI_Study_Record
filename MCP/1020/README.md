# Notion MCP (Model Context Protocol) 연동 테스트

Notion의 MCP API를 사용하여 페이지를 수정하고 도구를 조회하는 Python 스크립트 모음입니다.

## MCP 요청 스키마

### 1. Initialize (세션 ID 발급)

```json
{
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
```

**헤더:**
```
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
Accept: application/json, text/event-stream
```

**응답:** `Mcp-Session-Id` 헤더에서 세션 ID 획득

---

### 2. Tools List (도구 목록 조회)

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 2
}
```

**헤더:**
```
Authorization: Bearer {ACCESS_TOKEN}
Mcp-Session-Id: {SESSION_ID}
Content-Type: application/json
Accept: application/json, text/event-stream
```

---

### 3. Tools Call (도구 호출 - 페이지 수정)

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "notion-update-page",
    "arguments": {
      "data": {
        "page_id": "{PAGE_ID}",
        "command": "replace_content",
        "new_str": "# I changed text."
      }
    }
  },
  "id": "32323232323"
}
```

**헤더:**
```
Authorization: Bearer {ACCESS_TOKEN}
Mcp-Session-Id: {SESSION_ID}
Content-Type: application/json
Accept: application/json, text/event-stream
```

**command 옵션:**
- `replace_content`: 페이지 전체 내용 교체
- `replace_content_range`: 특정 범위 내용 교체
- `insert_content_after`: 특정 위치 이후에 내용 삽입
- `update_properties`: 페이지 속성 업데이트

---

## 파일 구성

### 1. `list_tools.py`
Notion MCP 서버에서 사용 가능한 도구 목록을 조회합니다.

**주요 기능:**
- MCP 서버에 연결 및 세션 초기화
- `tools/list` 메서드로 사용 가능한 도구 목록 조회
- `notion-update-page` 도구의 스키마 상세 출력
- 결과를 `list_tools_결과.json`에 저장

### 2. `check_tool.py`
Notion 페이지의 내용을 실제로 수정하는 도구 테스트 스크립트입니다.

**주요 기능:**
- MCP 세션 초기화
- `notion-update-page` 도구를 호출하여 페이지 내용 변경
- `replace_content` 명령으로 페이지 전체 내용을 "# I changed text."로 교체

**실행 결과:**

| 파일명 | 결과 |
|--------|------|
| `check_tool_결과.gif` | ![check_tool 실행 과정](check_tool_결과.gif) |

### 3. 환경 설정 파일

#### `.env`
실제 환경 변수 설정 (gitignore에 포함)

**필수 환경 변수:**
```
ACCESS_TOKEN=your_notion_access_token
PAGE_ID=your_page_id
```

---

## 결과 파일

- `list_tools_결과.json`: 사용 가능한 Notion MCP 도구 목록
- `check_tool_결과.gif`: 페이지 수정 테스트 실행 과정

---

## MCP 프로토콜 흐름

1. **Initialize**: 세션 ID 발급
   - 위의 스키마 참고
   - `Mcp-Session-Id` 헤더로 세션 ID 수신

2. **Tools List/Call**: 도구 조회 또는 호출
   - 세션 ID를 헤더에 포함하여 요청
   - `Mcp-Session-Id` 헤더 사용

---

## 참고 사항

- **MCP URL:** `https://mcp.notion.com/mcp`
- **프로토콜 버전:** `2024-11-05`
- **JSON-RPC 2.0** 사용
- **응답 형식:** Server-Sent Events (SSE)
