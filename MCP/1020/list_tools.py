from dotenv import load_dotenv
load_dotenv()

import requests
import json

import os
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN","")
MCP_URL = "https://mcp.notion.com/mcp"


# 1️⃣ Initialize 요청 (Session ID 발급)
init_payload = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "manual-client", "version": "1.0"}
    },
    "id": 1
}

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

init_resp = requests.post(MCP_URL, headers=headers, json=init_payload)
print("Initialize Status:", init_resp.status_code)
if init_resp.status_code != 200:
    print("Initialize Response Text:", init_resp.text)
lines = init_resp.text.strip().split("\n")
session_id = None
for line in lines:
    if line.startswith("data: "):
        data = json.loads(line[6:])
        print(data)
        session_id = init_resp.headers.get("Mcp-Session-Id")
        break

if not session_id:
    print("Error: Could not get Session ID")
else:
    print("Session ID:", session_id)
    headers["Mcp-Session-Id"] = session_id

    # 2️⃣ tools/list 요청
    list_payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }

    response = requests.post(MCP_URL, headers=headers, json=list_payload)

    lines = response.text.strip().split("\n")
    for line in lines:
        if line.startswith("data: "):
            data = json.loads(line[6:])

            # notion-update-page 도구만 찾아서 상세 출력
            if "result" in data and "tools" in data["result"]:
                for tool in data["result"]["tools"]:
                    if tool["name"] == "notion-update-page":
                        print("\n=== notion-update-page 도구 스키마 ===")
                        print(json.dumps(tool, indent=2, ensure_ascii=False))
            break
    # 저장
    with open("list_tools_결과.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
