import streamlit as st
import asyncio
import nest_asyncio
import json
import os
import platform
from typing import Any, Dict, List, Callable, Optional
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
import uuid
os.environ['OPENAI_API_KEY'] = "sk-proj..."

os.environ['GOOGLE_API_KEY'] = "AIz.."


def random_uuid():
    return str(uuid.uuid4())


async def astream_graph(
    graph: CompiledStateGraph,
    inputs: dict,
    config: Optional[RunnableConfig] = None,
    node_names: List[str] = [],
    callback: Optional[Callable] = None,
    stream_mode: str = "messages",
    include_subgraphs: bool = False,
) -> Dict[str, Any]:
    """
    LangGraph의 실행 결과를 비동기적으로 스트리밍하고 직접 출력하는 함수입니다.

    Args:
        graph (CompiledStateGraph): 실행할 컴파일된 LangGraph 객체
        inputs (dict): 그래프에 전달할 입력값 딕셔너리
        config (Optional[RunnableConfig]): 실행 설정 (선택적)
        node_names (List[str], optional): 출력할 노드 이름 목록. 기본값은 빈 리스트
        callback (Optional[Callable], optional): 각 청크 처리를 위한 콜백 함수. 기본값은 None
            콜백 함수는 {"node": str, "content": Any} 형태의 딕셔너리를 인자로 받습니다.
        stream_mode (str, optional): 스트리밍 모드 ("messages" 또는 "updates"). 기본값은 "messages"
        include_subgraphs (bool, optional): 서브그래프 포함 여부. 기본값은 False

    Returns:
        Dict[str, Any]: 최종 결과 (선택적)
    """
    config = config or {}
    final_result = {}

    def format_namespace(namespace):
        return namespace[-1].split(":")[0] if len(namespace) > 0 else "root graph"

    prev_node = ""

    if stream_mode == "messages":
        async for chunk_msg, metadata in graph.astream(
            inputs, config, stream_mode=stream_mode
        ):
            curr_node = metadata["langgraph_node"]
            final_result = {
                "node": curr_node,
                "content": chunk_msg,
                "metadata": metadata,
            }

            # node_names가 비어있거나 현재 노드가 node_names에 있는 경우에만 처리
            if not node_names or curr_node in node_names:
                # 콜백 함수가 있는 경우 실행
                if callback:
                    result = callback({"node": curr_node, "content": chunk_msg})
                    if hasattr(result, "__await__"):
                        await result
                # 콜백이 없는 경우 기본 출력
                else:
                    # 노드가 변경된 경우에만 구분선 출력
                    if curr_node != prev_node:
                        print("\n" + "=" * 50)
                        print(f"🔄 Node: \033[1;36m{curr_node}\033[0m 🔄")
                        print("- " * 25)

                    # Claude/Anthropic 모델의 토큰 청크 처리 - 항상 텍스트만 추출
                    if hasattr(chunk_msg, "content"):
                        # 리스트 형태의 content (Anthropic/Claude 스타일)
                        if isinstance(chunk_msg.content, list):
                            for item in chunk_msg.content:
                                if isinstance(item, dict) and "text" in item:
                                    print(item["text"], end="", flush=True)
                        # 문자열 형태의 content
                        elif isinstance(chunk_msg.content, str):
                            print(chunk_msg.content, end="", flush=True)
                    # 그 외 형태의 chunk_msg 처리
                    else:
                        print(chunk_msg, end="", flush=True)

                prev_node = curr_node

    elif stream_mode == "updates":
        # 에러 수정: 언패킹 방식 변경
        # REACT 에이전트 등 일부 그래프에서는 단일 딕셔너리만 반환함
        async for chunk in graph.astream(
            inputs, config, stream_mode=stream_mode, subgraphs=include_subgraphs
        ):
            # 반환 형식에 따라 처리 방법 분기
            if isinstance(chunk, tuple) and len(chunk) == 2:
                # 기존 예상 형식: (namespace, chunk_dict)
                namespace, node_chunks = chunk
            else:
                # 단일 딕셔너리만 반환하는 경우 (REACT 에이전트 등)
                namespace = []  # 빈 네임스페이스 (루트 그래프)
                node_chunks = chunk  # chunk 자체가 노드 청크 딕셔너리

            # 딕셔너리인지 확인하고 항목 처리
            if isinstance(node_chunks, dict):
                for node_name, node_chunk in node_chunks.items():
                    final_result = {
                        "node": node_name,
                        "content": node_chunk,
                        "namespace": namespace,
                    }

                    # node_names가 비어있지 않은 경우에만 필터링
                    if len(node_names) > 0 and node_name not in node_names:
                        continue

                    # 콜백 함수가 있는 경우 실행
                    if callback is not None:
                        result = callback({"node": node_name, "content": node_chunk})
                        if hasattr(result, "__await__"):
                            await result
                    # 콜백이 없는 경우 기본 출력
                    else:
                        # 노드가 변경된 경우에만 구분선 출력 (messages 모드와 동일하게)
                        if node_name != prev_node:
                            print("\n" + "=" * 50)
                            print(f"🔄 Node: \033[1;36m{node_name}\033[0m 🔄")
                            print("- " * 25)

                        # 노드의 청크 데이터 출력 - 텍스트 중심으로 처리
                        if isinstance(node_chunk, dict):
                            for k, v in node_chunk.items():
                                if isinstance(v, BaseMessage):
                                    # BaseMessage의 content 속성이 텍스트나 리스트인 경우를 처리
                                    if hasattr(v, "content"):
                                        if isinstance(v.content, list):
                                            for item in v.content:
                                                if (
                                                    isinstance(item, dict)
                                                    and "text" in item
                                                ):
                                                    print(
                                                        item["text"], end="", flush=True
                                                    )
                                        else:
                                            print(v.content, end="", flush=True)
                                    else:
                                        v.pretty_print()
                                elif isinstance(v, list):
                                    for list_item in v:
                                        if isinstance(list_item, BaseMessage):
                                            if hasattr(list_item, "content"):
                                                if isinstance(list_item.content, list):
                                                    for item in list_item.content:
                                                        if (
                                                            isinstance(item, dict)
                                                            and "text" in item
                                                        ):
                                                            print(
                                                                item["text"],
                                                                end="",
                                                                flush=True,
                                                            )
                                                else:
                                                    print(
                                                        list_item.content,
                                                        end="",
                                                        flush=True,
                                                    )
                                            else:
                                                list_item.pretty_print()
                                        elif (
                                            isinstance(list_item, dict)
                                            and "text" in list_item
                                        ):
                                            print(list_item["text"], end="", flush=True)
                                        else:
                                            print(list_item, end="", flush=True)
                                elif isinstance(v, dict) and "text" in v:
                                    print(v["text"], end="", flush=True)
                                else:
                                    print(v, end="", flush=True)
                        elif node_chunk is not None:
                            if hasattr(node_chunk, "__iter__") and not isinstance(
                                node_chunk, str
                            ):
                                for item in node_chunk:
                                    if isinstance(item, dict) and "text" in item:
                                        print(item["text"], end="", flush=True)
                                    else:
                                        print(item, end="", flush=True)
                            else:
                                print(node_chunk, end="", flush=True)

                        # 구분선을 여기서 출력하지 않음 (messages 모드와 동일하게)

                    prev_node = node_name
            else:
                # 딕셔너리가 아닌 경우 전체 청크 출력
                print("\n" + "=" * 50)
                print(f"🔄 Raw output 🔄")
                print("- " * 25)
                print(node_chunks, end="", flush=True)
                # 구분선을 여기서 출력하지 않음
                final_result = {"content": node_chunks}

    else:
        raise ValueError(
            f"Invalid stream_mode: {stream_mode}. Must be 'messages' or 'updates'."
        )

    # 필요에 따라 최종 결과 반환
    return final_result

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# nest_asyncio 적용: 이미 실행 중인 이벤트 루프 내에서 중첩 호출 허용
nest_asyncio.apply()

# 전역 이벤트 루프 생성 및 재사용 (한번 생성한 후 계속 사용)
if "event_loop" not in st.session_state:
    loop = asyncio.new_event_loop()
    st.session_state.event_loop = loop
    asyncio.set_event_loop(loop)

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages.ai import AIMessageChunk
from langchain_core.messages.tool import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

# 환경 변수 로드 (.env 파일에서 API 키 등의 설정을 가져옴)
load_dotenv(override=True)

# config.json 파일 경로 설정
CONFIG_FILE_PATH = "config.json"

# JSON 설정 파일 로드 함수
def load_config_from_json():
    """
    config.json 파일에서 설정을 로드합니다.
    파일이 없는 경우 기본 설정으로 파일을 생성합니다.

    반환값:
        dict: 로드된 설정
    """
    default_config = {
        "get_current_time": {
            "command": "python",
            "args": ["./mcp_server_time.py"],
            "transport": "stdio"
        }
    }
    
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # 파일이 없는 경우 기본 설정으로 파일 생성
            save_config_to_json(default_config)
            return default_config
    except Exception as e:
        st.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
        return default_config

# JSON 설정 파일 저장 함수
def save_config_to_json(config):
    """
    설정을 config.json 파일에 저장합니다.

    매개변수:
        config (dict): 저장할 설정
    
    반환값:
        bool: 저장 성공 여부
    """
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"설정 파일 저장 중 오류 발생: {str(e)}")
        return False

# 로그인 세션 변수 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 로그인 필요 여부 확인
use_login = os.environ.get("USE_LOGIN", "false").lower() == "true"

# 로그인 상태에 따라 페이지 설정 변경
if use_login and not st.session_state.authenticated:
    # 로그인 페이지는 기본(narrow) 레이아웃 사용
    st.set_page_config(page_title="Agent with MCP Tools", page_icon="🧠")
else:
    # 메인 앱은 wide 레이아웃 사용
    st.set_page_config(page_title="Agent with MCP Tools", page_icon="🧠", layout="wide")

# 로그인 기능이 활성화되어 있고 아직 인증되지 않은 경우 로그인 화면 표시
if use_login and not st.session_state.authenticated:
    st.title("🔐 로그인")
    st.markdown("시스템을 사용하려면 로그인이 필요합니다.")

    # 로그인 폼을 화면 중앙에 좁게 배치
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submit_button = st.form_submit_button("로그인")

        if submit_button:
            expected_username = os.environ.get("USER_ID")
            expected_password = os.environ.get("USER_PASSWORD")

            if username == expected_username and password == expected_password:
                st.session_state.authenticated = True
                st.success("✅ 로그인 성공! 잠시만 기다려주세요...")
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")

    # 로그인 화면에서는 메인 앱을 표시하지 않음
    st.stop()

# 기존 페이지 타이틀 및 설명
st.title("💬 MCP 도구 활용 에이전트")
st.markdown("✨ MCP 도구를 활용한 ReAct 에이전트에게 질문해보세요.")

SYSTEM_PROMPT = """<ROLE>
You are a smart agent with an ability to use tools. 
You will be given a question and you will use the tools to answer the question.
Pick the most relevant tool to answer the question. 
If you are failed to answer the question, try different tools to get context.
Your answer should be very polite and professional.
</ROLE>

----

<INSTRUCTIONS>
Step 1: Analyze the question
- Analyze user's question and final goal.
- If the user's question is consist of multiple sub-questions, split them into smaller sub-questions.

Step 2: Pick the most relevant tool
- Pick the most relevant tool to answer the question.
- If you are failed to answer the question, try different tools to get context.

Step 3: Answer the question
- Answer the question in the same language as the question.
- Your answer should be very polite and professional.

Step 4: Provide the source of the answer(if applicable)
- If you've used the tool, provide the source of the answer.
- Valid sources are either a website(URL) or a document(PDF, etc).

Guidelines:
- If you've used the tool, your answer should be based on the tool's output(tool's output is more important than your own knowledge).
- If you've used the tool, and the source is valid URL, provide the source(URL) of the answer.
- Skip providing the source if the source is not URL.
- Answer in the same language as the question.
- Answer should be concise and to the point.
- Avoid response your output with any other information than the answer and the source.  
</INSTRUCTIONS>

----

<OUTPUT_FORMAT>
(concise answer to the question)

**Source**(if applicable)
- (source1: valid URL)
- (source2: valid URL)
- ...
</OUTPUT_FORMAT>
"""

OUTPUT_TOKEN_INFO = {
    "claude-3-5-sonnet-latest": {"max_tokens": 8192},
    "claude-3-5-haiku-latest": {"max_tokens": 8192},
    "claude-3-7-sonnet-latest": {"max_tokens": 64000},
    "gpt-4o": {"max_tokens": 16000},
    "gpt-4o-mini": {"max_tokens": 16000},
    "gemini-2.0-flash": {"max_tokens": 16000},
    "gemini-2.5-pro": {"max_tokens": 16000},
    "gemini-2.5-flash": {"max_tokens": 16000},
}

# 세션 상태 초기화
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False  # 세션 초기화 상태 플래그
    st.session_state.agent = None  # ReAct 에이전트 객체 저장 공간
    st.session_state.history = []  # 대화 기록 저장 리스트
    st.session_state.mcp_client = None  # MCP 클라이언트 객체 저장 공간
    st.session_state.timeout_seconds = 120  # 응답 생성 제한 시간(초), 기본값 120초
    st.session_state.selected_model = "claude-3-7-sonnet-latest"  # 기본 모델 선택
    st.session_state.recursion_limit = 100  # 재귀 호출 제한, 기본값 100

if "thread_id" not in st.session_state:
    st.session_state.thread_id = random_uuid()


# --- 함수 정의 부분 ---


async def cleanup_mcp_client():
    """
    기존 MCP 클라이언트를 안전하게 종료합니다.

    기존 클라이언트가 있는 경우 정상적으로 리소스를 해제합니다.
    """
    if "mcp_client" in st.session_state and st.session_state.mcp_client is not None:
        try:

            await st.session_state.mcp_client.__aexit__(None, None, None)
            st.session_state.mcp_client = None
        except Exception as e:
            import traceback

            # st.warning(f"MCP 클라이언트 종료 중 오류: {str(e)}")
            # st.warning(traceback.format_exc())


def print_message():
    """
    채팅 기록을 화면에 출력합니다.

    사용자와 어시스턴트의 메시지를 구분하여 화면에 표시하고,
    도구 호출 정보는 어시스턴트 메시지 컨테이너 내에 표시합니다.
    """
    i = 0
    while i < len(st.session_state.history):
        message = st.session_state.history[i]

        if message["role"] == "user":
            st.chat_message("user", avatar="🧑‍💻").markdown(message["content"])
            i += 1
        elif message["role"] == "assistant":
            # 어시스턴트 메시지 컨테이너 생성
            with st.chat_message("assistant", avatar="🤖"):
                # 어시스턴트 메시지 내용 표시
                st.markdown(message["content"])

                # 다음 메시지가 도구 호출 정보인지 확인
                if (
                    i + 1 < len(st.session_state.history)
                    and st.session_state.history[i + 1]["role"] == "assistant_tool"
                ):
                    # 도구 호출 정보를 동일한 컨테이너 내에 expander로 표시
                    with st.expander("🔧 도구 호출 정보", expanded=False):
                        st.markdown(st.session_state.history[i + 1]["content"])
                    i += 2  # 두 메시지를 함께 처리했으므로 2 증가
                else:
                    i += 1  # 일반 메시지만 처리했으므로 1 증가
        else:
            # assistant_tool 메시지는 위에서 처리되므로 건너뜀
            i += 1


def get_streaming_callback(text_placeholder, tool_placeholder):
    """
    스트리밍 콜백 함수를 생성합니다.

    이 함수는 LLM에서 생성되는 응답을 실시간으로 화면에 표시하기 위한 콜백 함수를 생성합니다.
    텍스트 응답과 도구 호출 정보를 각각 다른 영역에 표시합니다.

    매개변수:
        text_placeholder: 텍스트 응답을 표시할 Streamlit 컴포넌트
        tool_placeholder: 도구 호출 정보를 표시할 Streamlit 컴포넌트

    반환값:
        callback_func: 스트리밍 콜백 함수
        accumulated_text: 누적된 텍스트 응답을 저장하는 리스트
        accumulated_tool: 누적된 도구 호출 정보를 저장하는 리스트
    """
    accumulated_text = []
    accumulated_tool = []

    def callback_func(message: dict):
        nonlocal accumulated_text, accumulated_tool
        message_content = message.get("content", None)

        if isinstance(message_content, AIMessageChunk):
            content = message_content.content
            # 콘텐츠가 리스트 형태인 경우 (Claude 모델 등에서 주로 발생)
            if isinstance(content, list) and len(content) > 0:
                message_chunk = content[0]
                # 텍스트 타입인 경우 처리
                if message_chunk["type"] == "text":
                    accumulated_text.append(message_chunk["text"])
                    text_placeholder.markdown("".join(accumulated_text))
                # 도구 사용 타입인 경우 처리
                elif message_chunk["type"] == "tool_use":
                    if "partial_json" in message_chunk:
                        accumulated_tool.append(message_chunk["partial_json"])
                    else:
                        tool_call_chunks = message_content.tool_call_chunks
                        tool_call_chunk = tool_call_chunks[0]
                        accumulated_tool.append(
                            "\n```json\n" + str(tool_call_chunk) + "\n```\n"
                        )
                    with tool_placeholder.expander("🔧 도구 호출 정보", expanded=True):
                        st.markdown("".join(accumulated_tool))
            # tool_calls 속성이 있는 경우 처리 (OpenAI 모델 등에서 주로 발생)
            elif (
                hasattr(message_content, "tool_calls")
                and message_content.tool_calls
                and len(message_content.tool_calls[0]["name"]) > 0
            ):
                tool_call_info = message_content.tool_calls[0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander("🔧 도구 호출 정보", expanded=True):
                    st.markdown("".join(accumulated_tool))
            # 단순 문자열인 경우 처리
            elif isinstance(content, str):
                accumulated_text.append(content)
                text_placeholder.markdown("".join(accumulated_text))
            # 유효하지 않은 도구 호출 정보가 있는 경우 처리
            elif (
                hasattr(message_content, "invalid_tool_calls")
                and message_content.invalid_tool_calls
            ):
                tool_call_info = message_content.invalid_tool_calls[0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander(
                    "🔧 도구 호출 정보 (유효하지 않음)", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
            # tool_call_chunks 속성이 있는 경우 처리
            elif (
                hasattr(message_content, "tool_call_chunks")
                and message_content.tool_call_chunks
            ):
                tool_call_chunk = message_content.tool_call_chunks[0]
                accumulated_tool.append(
                    "\n```json\n" + str(tool_call_chunk) + "\n```\n"
                )
                with tool_placeholder.expander("🔧 도구 호출 정보", expanded=True):
                    st.markdown("".join(accumulated_tool))
            # additional_kwargs에 tool_calls가 있는 경우 처리 (다양한 모델 호환성 지원)
            elif (
                hasattr(message_content, "additional_kwargs")
                and "tool_calls" in message_content.additional_kwargs
            ):
                tool_call_info = message_content.additional_kwargs["tool_calls"][0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander("🔧 도구 호출 정보", expanded=True):
                    st.markdown("".join(accumulated_tool))
        # 도구 메시지인 경우 처리 (도구의 응답)
        elif isinstance(message_content, ToolMessage):
            accumulated_tool.append(
                "\n```json\n" + str(message_content.content) + "\n```\n"
            )
            with tool_placeholder.expander("🔧 도구 호출 정보", expanded=True):
                st.markdown("".join(accumulated_tool))
        return None

    return callback_func, accumulated_text, accumulated_tool


async def process_query(query, text_placeholder, tool_placeholder, timeout_seconds=60):
    """
    사용자 질문을 처리하고 응답을 생성합니다.

    이 함수는 사용자의 질문을 에이전트에 전달하고, 응답을 실시간으로 스트리밍하여 표시합니다.
    지정된 시간 내에 응답이 완료되지 않으면 타임아웃 오류를 반환합니다.

    매개변수:
        query: 사용자가 입력한 질문 텍스트
        text_placeholder: 텍스트 응답을 표시할 Streamlit 컴포넌트
        tool_placeholder: 도구 호출 정보를 표시할 Streamlit 컴포넌트
        timeout_seconds: 응답 생성 제한 시간(초)

    반환값:
        response: 에이전트의 응답 객체
        final_text: 최종 텍스트 응답
        final_tool: 최종 도구 호출 정보
    """
    try:
        if st.session_state.agent:
            streaming_callback, accumulated_text_obj, accumulated_tool_obj = (
                get_streaming_callback(text_placeholder, tool_placeholder)
            )
            try:
                response = await asyncio.wait_for(
                    astream_graph(
                        st.session_state.agent,
                        {"messages": [HumanMessage(content=query)]},
                        callback=streaming_callback,
                        config=RunnableConfig(
                            recursion_limit=st.session_state.recursion_limit,
                            thread_id=st.session_state.thread_id,
                        ),
                    ),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                error_msg = f"⏱️ 요청 시간이 {timeout_seconds}초를 초과했습니다. 나중에 다시 시도해 주세요."
                return {"error": error_msg}, error_msg, ""

            final_text = "".join(accumulated_text_obj)
            final_tool = "".join(accumulated_tool_obj)
            return response, final_text, final_tool
        else:
            return (
                {"error": "🚫 에이전트가 초기화되지 않았습니다."},
                "🚫 에이전트가 초기화되지 않았습니다.",
                "",
            )
    except Exception as e:
        import traceback

        error_msg = f"❌ 쿼리 처리 중 오류 발생: {str(e)}\n{traceback.format_exc()}"
        return {"error": error_msg}, error_msg, ""


async def initialize_session(mcp_config=None):
    """
    MCP 세션과 에이전트를 초기화합니다.

    매개변수:
        mcp_config: MCP 도구 설정 정보(JSON). None인 경우 기본 설정 사용

    반환값:
        bool: 초기화 성공 여부
    """
    with st.spinner("🔄 MCP 서버에 연결 중..."):
        # 먼저 기존 클라이언트를 안전하게 정리
        await cleanup_mcp_client()

        if mcp_config is None:
            # config.json 파일에서 설정 로드
            mcp_config = load_config_from_json()
        print("Loaded MCP config:", mcp_config)
        client = MultiServerMCPClient(mcp_config)
        print("Connecting to MCP servers...", client)
        # await client.__aenter__()
        tools = await client.get_tools()
        print("Available tools:", len(tools))
        st.session_state.tool_count = len(tools)
        st.session_state.mcp_client = client

        # 선택된 모델에 따라 적절한 모델 초기화
        selected_model = st.session_state.selected_model

        if selected_model in [
            "claude-3-7-sonnet-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-5-haiku-latest",
        ]:
            model = ChatAnthropic(
                model=selected_model,
                temperature=0.1,
                max_tokens=OUTPUT_TOKEN_INFO[selected_model]["max_tokens"],
            )
        elif selected_model in [
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "gemini-2.5-flash",
        ]:
            model = ChatGoogleGenerativeAI(
                model = selected_model,
                temperature=0.1,
                max_tokens=OUTPUT_TOKEN_INFO[selected_model]["max_tokens"],
            )
        else:  # OpenAI 모델 사용
            model = ChatOpenAI(
                model=selected_model,
                temperature=0.1,
                max_tokens=OUTPUT_TOKEN_INFO[selected_model]["max_tokens"],
            )
        agent = create_react_agent(
            model,
            tools,
            checkpointer=MemorySaver(),
            prompt=SYSTEM_PROMPT,
        )
        st.session_state.agent = agent
        st.session_state.session_initialized = True
        return True


# --- 사이드바: 시스템 설정 섹션 ---
with st.sidebar:
    st.subheader("⚙️ 시스템 설정")

    # 모델 선택 기능
    # 사용 가능한 모델 목록 생성
    available_models = []

    # Anthropic API 키 확인
    has_anthropic_key = os.environ.get("ANTHROPIC_API_KEY") is not None
    if has_anthropic_key:
        available_models.extend(
            [
                "claude-3-7-sonnet-latest",
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-latest",
            ]
        )

    # OpenAI API 키 확인
    has_openai_key = os.environ.get("OPENAI_API_KEY") is not None
    # Google API 키 확인
    has_google_key = os.environ.get("GOOGLE_API_KEY") is not None
    if has_google_key:
        available_models.extend(["gemini-2.0-flash", "gemini-2.5-pro", "gemini-2.5-flash"])
    if has_openai_key:
        available_models.extend(["gpt-4o", "gpt-4o-mini"])

    # 사용 가능한 모델이 없는 경우 메시지 표시
    if not available_models:
        st.warning(
            "⚠️ API 키가 설정되지 않았습니다. .env 파일에 ANTHROPIC_API_KEY 또는 OPENAI_API_KEY를 추가해주세요."
        )
        # 기본값으로 Claude 모델 추가 (키가 없어도 UI를 보여주기 위함)
        available_models = ["claude-3-7-sonnet-latest"]

    # 모델 선택 드롭다운
    previous_model = st.session_state.selected_model
    st.session_state.selected_model = st.selectbox(
        "🤖 사용할 모델 선택",
        options=available_models,
        index=(
            available_models.index(st.session_state.selected_model)
            if st.session_state.selected_model in available_models
            else 0
        ),
        help="Anthropic 모델은 ANTHROPIC_API_KEY가, OpenAI 모델은 OPENAI_API_KEY가 환경변수로 설정되어야 합니다.",
    )

    # 모델이 변경되었을 때 세션 초기화 필요 알림
    if (
        previous_model != st.session_state.selected_model
        and st.session_state.session_initialized
    ):
        st.warning(
            "⚠️ 모델이 변경되었습니다. '설정 적용하기' 버튼을 눌러 변경사항을 적용하세요."
        )

    # 타임아웃 설정 슬라이더 추가
    st.session_state.timeout_seconds = st.slider(
        "⏱️ 응답 생성 제한 시간(초)",
        min_value=60,
        max_value=300,
        value=st.session_state.timeout_seconds,
        step=10,
        help="에이전트가 응답을 생성하는 최대 시간을 설정합니다. 복잡한 작업은 더 긴 시간이 필요할 수 있습니다.",
    )

    st.session_state.recursion_limit = st.slider(
        "⏱️ 재귀 호출 제한(횟수)",
        min_value=10,
        max_value=200,
        value=st.session_state.recursion_limit,
        step=10,
        help="재귀 호출 제한 횟수를 설정합니다. 너무 높은 값을 설정하면 메모리 부족 문제가 발생할 수 있습니다.",
    )

    st.divider()  # 구분선 추가

    # 도구 설정 섹션 추가
    st.subheader("🔧 도구 설정")

    # expander 상태를 세션 상태로 관리
    if "mcp_tools_expander" not in st.session_state:
        st.session_state.mcp_tools_expander = False

    # MCP 도구 추가 인터페이스
    with st.expander("🧰 MCP 도구 추가", expanded=st.session_state.mcp_tools_expander):
        # config.json 파일에서 설정 로드하여 표시
        loaded_config = load_config_from_json()
        default_config_text = json.dumps(loaded_config, indent=2, ensure_ascii=False)
        
        # pending config가 없으면 기존 mcp_config_text 기반으로 생성
        if "pending_mcp_config" not in st.session_state:
            try:
                st.session_state.pending_mcp_config = loaded_config
            except Exception as e:
                st.error(f"초기 pending config 설정 실패: {e}")

        # 개별 도구 추가를 위한 UI
        st.subheader("도구 추가")
        st.markdown(
            """
            [어떻게 설정 하나요?](https://teddylee777.notion.site/MCP-1d324f35d12980c8b018e12afdf545a1?pvs=4)

            ⚠️ **중요**: JSON을 반드시 중괄호(`{}`)로 감싸야 합니다."""
        )

        # 보다 명확한 예시 제공
        example_json = {
            "github": {
                "command": "npx",
                "args": [
                    "-y",
                    "@smithery/cli@latest",
                    "run",
                    "@smithery-ai/github",
                    "--config",
                    '{"githubPersonalAccessToken":"your_token_here"}',
                ],
                "transport": "stdio",
            }
        }

        default_text = json.dumps(example_json, indent=2, ensure_ascii=False)

        new_tool_json = st.text_area(
            "도구 JSON",
            default_text,
            height=250,
        )

        # 추가하기 버튼
        if st.button(
            "도구 추가",
            type="primary",
            key="add_tool_button",
            use_container_width=True,
        ):
            try:
                # 입력값 검증
                if not new_tool_json.strip().startswith(
                    "{"
                ) or not new_tool_json.strip().endswith("}"):
                    st.error("JSON은 중괄호({})로 시작하고 끝나야 합니다.")
                    st.markdown('올바른 형식: `{ "도구이름": { ... } }`')
                else:
                    # JSON 파싱
                    parsed_tool = json.loads(new_tool_json)

                    # mcpServers 형식인지 확인하고 처리
                    if "mcpServers" in parsed_tool:
                        # mcpServers 안의 내용을 최상위로 이동
                        parsed_tool = parsed_tool["mcpServers"]
                        st.info(
                            "'mcpServers' 형식이 감지되었습니다. 자동으로 변환합니다."
                        )

                    # 입력된 도구 수 확인
                    if len(parsed_tool) == 0:
                        st.error("최소 하나 이상의 도구를 입력해주세요.")
                    else:
                        # 모든 도구에 대해 처리
                        success_tools = []
                        for tool_name, tool_config in parsed_tool.items():
                            # URL 필드 확인 및 transport 설정
                            if "url" in tool_config:
                                # URL이 있는 경우 transport를 "sse"로 설정
                                tool_config["transport"] = "sse"
                                st.info(
                                    f"'{tool_name}' 도구에 URL이 감지되어 transport를 'sse'로 설정했습니다."
                                )
                            elif "transport" not in tool_config:
                                # URL이 없고 transport도 없는 경우 기본값 "stdio" 설정
                                tool_config["transport"] = "stdio"

                            # 필수 필드 확인
                            if (
                                "command" not in tool_config
                                and "url" not in tool_config
                            ):
                                st.error(
                                    f"'{tool_name}' 도구 설정에는 'command' 또는 'url' 필드가 필요합니다."
                                )
                            elif "command" in tool_config and "args" not in tool_config:
                                st.error(
                                    f"'{tool_name}' 도구 설정에는 'args' 필드가 필요합니다."
                                )
                            elif "command" in tool_config and not isinstance(
                                tool_config["args"], list
                            ):
                                st.error(
                                    f"'{tool_name}' 도구의 'args' 필드는 반드시 배열([]) 형식이어야 합니다."
                                )
                            else:
                                # pending_mcp_config에 도구 추가
                                st.session_state.pending_mcp_config[tool_name] = (
                                    tool_config
                                )
                                success_tools.append(tool_name)

                        # 성공 메시지
                        if success_tools:
                            if len(success_tools) == 1:
                                st.success(
                                    f"{success_tools[0]} 도구가 추가되었습니다. 적용하려면 '설정 적용하기' 버튼을 눌러주세요."
                                )
                            else:
                                tool_names = ", ".join(success_tools)
                                st.success(
                                    f"총 {len(success_tools)}개 도구({tool_names})가 추가되었습니다. 적용하려면 '설정 적용하기' 버튼을 눌러주세요."
                                )
                            # 추가되면 expander를 접어줌
                            st.session_state.mcp_tools_expander = False
                            st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"JSON 파싱 에러: {e}")
                st.markdown(
                    f"""
                **수정 방법**:
                1. JSON 형식이 올바른지 확인하세요.
                2. 모든 키는 큰따옴표(")로 감싸야 합니다.
                3. 문자열 값도 큰따옴표(")로 감싸야 합니다.
                4. 문자열 내에서 큰따옴표를 사용할 경우 이스케이프(\\")해야 합니다.
                """
                )
            except Exception as e:
                st.error(f"오류 발생: {e}")

    # 등록된 도구 목록 표시 및 삭제 버튼 추가
    with st.expander("📋 등록된 도구 목록", expanded=True):
        try:
            pending_config = st.session_state.pending_mcp_config
        except Exception as e:
            st.error("유효한 MCP 도구 설정이 아닙니다.")
        else:
            # pending config의 키(도구 이름) 목록을 순회하며 표시
            for tool_name in list(pending_config.keys()):
                col1, col2 = st.columns([8, 2])
                col1.markdown(f"- **{tool_name}**")
                if col2.button("삭제", key=f"delete_{tool_name}"):
                    # pending config에서 해당 도구 삭제 (즉시 적용되지는 않음)
                    del st.session_state.pending_mcp_config[tool_name]
                    st.success(
                        f"{tool_name} 도구가 삭제되었습니다. 적용하려면 '설정 적용하기' 버튼을 눌러주세요."
                    )

    st.divider()  # 구분선 추가

# --- 사이드바: 시스템 정보 및 작업 버튼 섹션 ---
with st.sidebar:
    st.subheader("📊 시스템 정보")
    st.write(f"🛠️ MCP 도구 수: {st.session_state.get('tool_count', '초기화 중...')}")
    selected_model_name = st.session_state.selected_model
    st.write(f"🧠 현재 모델: {selected_model_name}")

    # 설정 적용하기 버튼을 여기로 이동
    if st.button(
        "설정 적용하기",
        key="apply_button",
        type="primary",
        use_container_width=True,
    ):
        # 적용 중 메시지 표시
        apply_status = st.empty()
        with apply_status.container():
            st.warning("🔄 변경사항을 적용하고 있습니다. 잠시만 기다려주세요...")
            progress_bar = st.progress(0)

            # 설정 저장
            st.session_state.mcp_config_text = json.dumps(
                st.session_state.pending_mcp_config, indent=2, ensure_ascii=False
            )

            # config.json 파일에 설정 저장
            save_result = save_config_to_json(st.session_state.pending_mcp_config)
            if not save_result:
                st.error("❌ 설정 파일 저장에 실패했습니다.")
            
            progress_bar.progress(15)

            # 세션 초기화 준비
            st.session_state.session_initialized = False
            st.session_state.agent = None

            # 진행 상태 업데이트
            progress_bar.progress(30)

            # 초기화 실행
            success = st.session_state.event_loop.run_until_complete(
                initialize_session(st.session_state.pending_mcp_config)
            )

            # 진행 상태 업데이트
            progress_bar.progress(100)

            if success:
                st.success("✅ 새로운 설정이 적용되었습니다.")
                # 도구 추가 expander 접기
                if "mcp_tools_expander" in st.session_state:
                    st.session_state.mcp_tools_expander = False
            else:
                st.error("❌ 설정 적용에 실패하였습니다.")

        # 페이지 새로고침
        st.rerun()

    st.divider()  # 구분선 추가

    # 작업 버튼 섹션
    st.subheader("🔄 작업")

    # 대화 초기화 버튼
    if st.button("대화 초기화", use_container_width=True, type="primary"):
        # thread_id 초기화
        st.session_state.thread_id = random_uuid()

        # 대화 히스토리 초기화
        st.session_state.history = []

        # 알림 메시지
        st.success("✅ 대화가 초기화되었습니다.")

        # 페이지 새로고침
        st.rerun()

    # 로그인 기능이 활성화된 경우에만 로그아웃 버튼 표시
    if use_login and st.session_state.authenticated:
        st.divider()  # 구분선 추가
        if st.button("로그아웃", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.success("✅ 로그아웃 되었습니다.")
            st.rerun()

# --- 기본 세션 초기화 (초기화되지 않은 경우) ---
if not st.session_state.session_initialized:
    st.info(
        "MCP 서버와 에이전트가 초기화되지 않았습니다. 왼쪽 사이드바의 '설정 적용하기' 버튼을 클릭하여 초기화해주세요."
    )


# --- 대화 기록 출력 ---
print_message()

# --- 사용자 입력 및 처리 ---
user_query = st.chat_input("💬 질문을 입력하세요")
if user_query:
    if st.session_state.session_initialized:
        st.chat_message("user", avatar="🧑‍💻").markdown(user_query)
        with st.chat_message("assistant", avatar="🤖"):
            tool_placeholder = st.empty()
            text_placeholder = st.empty()
            resp, final_text, final_tool = (
                st.session_state.event_loop.run_until_complete(
                    process_query(
                        user_query,
                        text_placeholder,
                        tool_placeholder,
                        st.session_state.timeout_seconds,
                    )
                )
            )
        if "error" in resp:
            st.error(resp["error"])
        else:
            st.session_state.history.append({"role": "user", "content": user_query})
            st.session_state.history.append(
                {"role": "assistant", "content": final_text}
            )
            if final_tool.strip():
                st.session_state.history.append(
                    {"role": "assistant_tool", "content": final_tool}
                )
            st.rerun()
    else:
        st.warning(
            "⚠️ MCP 서버와 에이전트가 초기화되지 않았습니다. 왼쪽 사이드바의 '설정 적용하기' 버튼을 클릭하여 초기화해주세요."
        )
