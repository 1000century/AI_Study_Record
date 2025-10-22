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

| 파일 | 설명 |
|------|------|
| `list_tools.py` | MCP 도구 목록 조회 및 스키마 확인 |
| `check_tool.py` | Notion 페이지 내용 수정 테스트 |
| `.env` | 환경 변수 설정 (`ACCESS_TOKEN`, `PAGE_ID`) |
| `list_tools_결과.json` | 조회된 도구 목록 저장 결과 |
| `check_tool_결과.gif` | 페이지 수정 실행 과정 |

---

## 환경 설정

`.env` 파일 예시:
```
ACCESS_TOKEN=your_notion_access_token
PAGE_ID=your_page_id
```

---

## 참고

- **MCP URL:** `https://mcp.notion.com/mcp`
- **프로토콜 버전:** `2024-11-05`
- **응답 형식:** Server-Sent Events (SSE)
