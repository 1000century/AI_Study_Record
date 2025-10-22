from dotenv import load_dotenv
load_dotenv()
import requests
import json

import os
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN","")
MCP_URL = "https://mcp.notion.com/mcp"
PAGE_ID = os.getenv("PAGE_ID"," ")

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
        session_id = init_resp.headers.get("Mcp-Session-Id")
        print("Initialize Data:", data)
        break

if not session_id:
    print("Error: Could not get Session ID")
    print("Raw Response:", init_resp.text)
else:
    print("Session ID:", session_id)
    headers["Mcp-Session-Id"] = session_id

    # 🛠 callTool 요청
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
        "id": '32323232323'
    }

    response = requests.post(MCP_URL, headers=headers, json=payload)

    print("\n\nCall Tool Status:", response.status_code)
    lines = response.text.strip().split("\n")
    for line in lines:
        if line.startswith("data: "):
            data = json.loads(line[6:])
            print(json.dumps(data, indent=2))
            break