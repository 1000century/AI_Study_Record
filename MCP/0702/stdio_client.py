from dotenv import load_dotenv
load_dotenv()
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
# astream_graph 함수 정의
from typing import Any, Dict, List, Callable, Optional
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

text  = r"""        "id": null,
        "type": "R",
        "description": "30세 남자가 2주 전부터 시작된 기침으로 왔다. 혈압 118/80 mmHg, 맥박 102회/분, 호흡 22회/분, 체온 38.2℃\n였다. 우측 폐의 호흡음은 정상이었고, 좌측 폐에서 흡기 시 악설음이 들렸다(두 가지).",
        "solution": null,
        "examName": "임종평15-1",
        "examPeriod": 2,
        "examNumber": 1,
        "choices": [
            "기관지내 이물질",
            "기관지확장증",
            "기흉",
            "만성 폐쇄성 폐질환",
            "천식",
            "폐결핵",
            "폐렴",
            "폐섬유화증",
            "폐색전증",
            "폐암"
        ],
        "answer": [],
        "createdAt": "2016-12-02T15:09:16+09:00",
        "publishedAt": "2016-12-02T15:09:16+09:00",
        "deletedAt": null,
        "version": 1.0,
        "chapterId": 9999,
        "problemId": null,
        "isDefault": true,
        "book_id": null,
        "book_title": null,
        "chapter_title": null,
        "시험연도": "15",
        "시험종류": "01",
        "시험교시": "02",
        "문제번호": 1,
        "문제고유번호": "15010201",
        "대단원": null,
        "소단원": null,
        "소단원번호": null,
        "알렌문제번호": 99,
        "문제": "30세 남자가 2주 전부터 시작된 기침으로 왔다. 혈압 118/80 mmHg, 맥박 102회/분, 호흡 22회/분, 체온 38.2℃\n였다. 우측 폐의 호흡음은 정상이었고, 좌측 폐에서 흡기 시 악설음이 들렸다(두 가지).",
        "lab_data": null,
        "table": null,
        "사진들": null,
        "선지들": [
            "기관지내 이물질",
            "기관지확장증",
            "기흉",
            "만성 폐쇄성 폐질환",
            "천식",
            "폐결핵",
            "폐렴",
            "폐섬유화증",
            "폐색전증",
            "폐암"
        ],
        "정답들": [],
        "imp": [],
        "ddx": [],
        "correct_rate": 0.0
    },
    {
        "id": null,
        "type": "R",
        "description": "50세 여자가 1개월간 지속된 기침으로 왔다. 호흡기 질환의 과거력은 없다. 혈압 120/78 mmHg, 맥박 80회/분,\n호흡 18회/분, 체온 36.5℃였다. 좌측 폐의 호흡음은 정상이었고, 우측 폐에서는 호기 시 천명음이 들렸다(두 가\n지).",
        "solution": null,
        "examName": "임종평15-1",
        "examPeriod": 2,
        "examNumber": 2,
        "choices": [
            "기관지내 이물질",
            "기관지확장증",
            "기흉",
            "만성 폐쇄성 폐질환",
            "천식",
            "폐결핵",
            "폐렴",
            "폐섬유화증",
            "폐색전증",
            "폐암"
        ],
        "answer": [],
        "createdAt": "2016-12-02T15:09:16+09:00",
        "publishedAt": "2016-12-02T15:09:16+09:00",
        "deletedAt": null,
        "version": 1.0,
        "chapterId": 9999,
        "problemId": null,
        "isDefault": true,
        "book_id": null,
        "book_title": null,
        "chapter_title": null,
        "시험연도": "15",
        "시험종류": "01",
        "시험교시": "02",
        "문제번호": 2,
        "문제고유번호": "15010202",
        "대단원": null,
        "소단원": null,
        "소단원번호": null,
        "알렌문제번호": 99,
        "문제": "50세 여자가 1개월간 지속된 기침으로 왔다. 호흡기 질환의 과거력은 없다. 혈압 120/78 mmHg, 맥박 80회/분,\n호흡 18회/분, 체온 36.5℃였다. 좌측 폐의 호흡음은 정상이었고, 우측 폐에서는 호기 시 천명음이 들렸다(두 가\n지).",
        "lab_data": null,
        "table": null,
        "사진들": null,
        "선지들": [
            "기관지내 이물질",
            "기관지확장증",
            "기흉",
            "만성 폐쇄성 폐질환",
            "천식",
            "폐결핵",
            "폐렴",
            "폐섬유화증",
            "폐색전증",
            "폐암"
        ],
        "정답들": [],
        "imp": [],
        "ddx": [],
        "correct_rate": 0.0
    },
    {
        "id": null,
        "type": "R",
        "description": "19세 남자가 어제 갑자기 발생한 가슴 통증으로 왔다. 주로 앞가슴이 아팠으며 숨을 크게 들이마시거나 움직이면\n심해졌다. 혈압 118/72 mmHg, 맥박 98회/분, 호흡 21회/분이었다. 키 180 cm, 몸무게 70 kg였다. 가슴 청진에서\n마찰음이 있었다. 가슴 X선 사진 (사진 1-1) 및 심전도결과 (사진 1-2) 이다(한 가지).",
        "solution": null,
        "examName": "임종평15-1",
        "examPeriod": 2,
        "examNumber": 3,
        "choices": [
            "급성대동맥박리증",
            "급성대동맥벽내혈종",
            "급성가슴막염",
            "급성심근경색",
            "급성심장막염",
            "기흉",
            "불안정형협심증",
            "식도연축",
            "폐색전증"
        ],
        "answer": [],
        "createdAt": "2016-12-02T15:09:16+09:00",
        "publishedAt": "2016-12-02T15:09:16+09:00",
        "deletedAt": null,
        "version": 1.0,
        "chapterId": 9999,
        "problemId": null,
        "isDefault": true,
        "book_id": null,
        "book_title": null,
        "chapter_title": null,
        "시험연도": "15",
        "시험종류": "01",
        "시험교시": "02",
        "문제번호": 3,
        "문제고유번호": "15010203",
        "대단원": null,
        "소단원": null,
        "소단원번호": null,
        "알렌문제번호": 99,
        "문제": "19세 남자가 어제 갑자기 발생한 가슴 통증으로 왔다. 주로 앞가슴이 아팠으며 숨을 크게 들이마시거나 움직이면\n심해졌다. 혈압 118/72 mmHg, 맥박 98회/분, 호흡 21회/분이었다. 키 180 cm, 몸무게 70 kg였다. 가슴 청진에서\n마찰음이 있었다. 가슴 X선 사진 (사진 1-1) 및 심전도결과 (사진 1-2) 이다(한 가지).",
        "lab_data": null,
        "table": null,
        "사진들": null,
        "선지들": [
            "급성대동맥박리증",
            "급성대동맥벽내혈종",
            "급성가슴막염",
            "급성심근경색",
            "급성심장막염",
            "기흉",
            "불안정형협심증",
            "식도연축",
            "폐색전증"
        ],
        "정답들": [],
        "imp": [],
        "ddx": [],
        "correct_rate": 0.0
    },
    {
        "id": null,
        "type": "R",
        "description": "68세 남자가 가슴이 아파서 병원에 왔다. 약 2시간 전 등 한가운데가 심하게 아팠다가 지금은 앞가슴에 통증이\n있다. 혈압 188/96 mmHg, 맥박 75회/분이었다. 키 170 cm, 몸무게 66 kg였다. 호흡음은 정상이고 심잡음은 들리\n지 않았다. 가슴 X선 사진 (사진 2-1) 및 심전도결과 (사진 2-2) 이다(두 가지).",
        "solution": null,
        "examName": "임종평15-1",
        "examPeriod": 2,
        "examNumber": 4,
        "choices": [
            "급성대동맥박리증",
            "급성대동맥벽내혈종",
            "급성가슴막염",
            "급성심근경색",
            "급성심장막염",
            "기흉",
            "불안정형협심증",
            "식도연축",
            "폐색전증"
        ],
        "answer": [],
        "createdAt": "2016-12-02T15:09:16+09:00",
        "publishedAt": "2016-12-02T15:09:16+09:00",
        "deletedAt": null,
        "version": 1.0,
        "chapterId": 9999,
        "problemId": null,
        "isDefault": true,
        "book_id": null,
        "book_title": null,
        "chapter_title": null,
        "시험연도": "15",
        "시험종류": "01",
        "시험교시": "02",
        "문제번호": 4,
        "문제고유번호": "15010204",
        "대단원": null,
        "소단원": null,
        "소단원번호": null,
        "알렌문제번호": 99,
        "문제": "68세 남자가 가슴이 아파서 병원에 왔다. 약 2시간 전 등 한가운데가 심하게 아팠다가 지금은 앞가슴에 통증이\n있다. 혈압 188/96 mmHg, 맥박 75회/분이었다. 키 170 cm, 몸무게 66 kg였다. 호흡음은 정상이고 심잡음은 들리\n지 않았다. 가슴 X선 사진 (사진 2-1) 및 심전도결과 (사진 2-2) 이다(두 가지).",
        "lab_data": null,
        "table": null,
        "사진들": null,
        "선지들": [
            "급성대동맥박리증",
            "급성대동맥벽내혈종",
            "급성가슴막염",
            "급성심근경색",
            "급성심장막염",
            "기흉",
            "불안정형협심증",
            "식도연축",
            "폐색전증"
        ],
        "정답들": [],
        "imp": [],
        "ddx": [],
        "correct_rate": 0.0
    },
    {
        "id": null,
        "type": "R",
        "description": "52세 여자가 가을 산행을 다녀온 일주일 뒤부터 열이 나고, 온 몸이 아프며 붉은 반점이 생긴다고 왔다. 혈압\n110/74 mmHg, 맥박 90회/분, 호흡 20회/분, 체온 38.3°C였다. 압통을 동반하는 이횡지 크기의 간이 만져졌다. 혈\n액 검사는 다음과 같다(두 가지).",
        "solution": null,
        "examName": "임종평15-1",
        "examPeriod": 2,
        "examNumber": 5,
        "choices": [
            "감염단핵구증",
            "결핵",
            "기쿠치병(Kikuchi’s disease)",
            "독감",
            "렙토스피라병",
            "림프종",
            "사슬알균 인두염",
            "츠츠가무시병"
        ],
        "answer": [],
        "createdAt": "2016-12-02T15:09:16+09:00",
        "publishedAt": "2016-12-02T15:09:16+09:00",
        "deletedAt": null,
        "version": 1.0,
        "chapterId": 9999,
        "problemId": null,
        "isDefault": true,
        "book_id": null,
        "book_title": null,
        "chapter_title": null,
        "시험연도": "15",
        "시험종류": "01",
        "시험교시": "02",
        "문제번호": 5,
        "문제고유번호": "15010205",
        "대단원": null,
        "소단원": null,
        "소단원번호": null,
        "알렌문제번호": 99,
        "문제": "52세 여자가 가을 산행을 다녀온 일주일 뒤부터 열이 나고, 온 몸이 아프며 붉은 반점이 생긴다고 왔다. 혈압\n110/74 mmHg, 맥박 90회/분, 호흡 20회/분, 체온 38.3°C였다. 압통을 동반하는 이횡지 크기의 간이 만져졌다. 혈\n액 검사는 다음과 같다(두 가지).",
        "lab_data": "혈색소 12 g/dL, 백혈구 9,000/mm3 (호중구 65%, 비전형 림프구 0.5%), 혈소판 85,000/mm3,\n알라닌아미노전달효소 80 IU/L, 아스파르테이트아미노전달효소 120 IU/L",
        "table": null,
        "사진들": null,
        "선지들": [
            "감염단핵구증",
            "결핵",
            "기쿠치병(Kikuchi’s disease)",
            "독감",
            "렙토스피라병",
            "림프종",
            "사슬알균 인두염",
            "츠츠가무시병"
        ],
        "정답들": [],
        "imp": [],
        "ddx": [],
        "correct_rate": 0.0
    },
    {
        "id": null,
        "type": "R",
        "description": "19세 남자가 일주일 전부터 열이 나고, 침을 삼키면 목이 아파서 왔다. 양쪽 목뒤 공간(posterior cervical space)\n에 압통을 동반하는 유동성의 림프절이 만져졌다. 혈압 110/74 mmHg, 맥박 105회/분, 호흡 20회/분, 체온 38.6°C\n였다. 혈액 검사는 다음과 같다(한 가지).",
        "solution": null,
        "examName": "임종평15-1",
        "examPeriod": 2,
        "examNumber": 6,
        "choices": [
            "감염단핵구증",
            "결핵",
            "기쿠치병(Kikuchi’s disease)",
            "독감",
            "렙토스피라병",
            "림프종",
            "사슬알균 인두염",
            "츠츠가무시병"
        ],
        "answer": [],
        "createdAt": "2016-12-02T15:09:16+09:00",
        "publishedAt": "2016-12-02T15:09:16+09:00",
        "deletedAt": null,
        "version": 1.0,
        "chapterId": 9999,
        "problemId": null,
        "isDefault": true,
        "book_id": null,
        "book_title": null,
        "chapter_title": null,
        "시험연도": "15",
        "시험종류": "01",
        "시험교시": "02",
        "문제번호": 6,
        "문제고유번호": "15010206",
        "대단원": null,
        "소단원": null,
        "소단원번호": null,
        "알렌문제번호": 99,
        "문제": "19세 남자가 일주일 전부터 열이 나고, 침을 삼키면 목이 아파서 왔다. 양쪽 목뒤 공간(posterior cervical space)\n에 압통을 동반하는 유동성의 림프절이 만져졌다. 혈압 110/74 mmHg, 맥박 105회/분, 호흡 20회/분, 체온 38.6°C\n였다. 혈액 검사는 다음과 같다(한 가지).",
        "lab_data": "혈색소 14 g/dL, 백혈구 8,500/mm3 (호중구 50%, 비전형 림프구 26%), 혈소판 95,000/mm3, 알라닌아미노전달\n효소 170 IU/L, 아스파르테이트아미노전달효소 109 IU/L",
        "table": null,
        "사진들": null,
        "선지들": [
            "감염단핵구증",
            "결핵",
            "기쿠치병(Kikuchi’s disease)",
            "독감",
            "렙토스피라병",
            "림프종",
            "사슬알균 인두염",
            "츠츠가무시병"
        ],
        "정답들": [],
        "imp": [],
        "ddx": [],
        "correct_rate": 0.0
    },
    {
        "id": null,
        "type": "R",
        "description": "33세 산과력 0-0-0-0인 여자가 질 출혈로 병원에 왔다. 골반 초음파에서 특이 소견 없었고, 자궁경부질세포진검사\n에서 의미미결정 비정형편평세포(atypical squamous cell of undetermined significance)가 관찰되었다(두 가지).",
        "solution": null,
        "examName": "임종평15-1",
        "examPeriod": 2,
        "examNumber": 7,
        "choices": [
            "광범위 자궁 절제술 및 양측 부속기 절제술",
            "광범위 자궁목절제술 및 양측 부속기 절제술",
            "단순자궁절제술",
            "사람유두종바이러스검사",
            "원뿔절제술",
            "자궁경부질세포진검사",
            "자궁내막 긁어냄술",
            "질확대경검사"
        ],
        "answer": [],
        "createdAt": "2016-12-02T15:09:16+09:00",
        "publishedAt": "2016-12-02T15:09:16+09:00",
        "deletedAt": null,
        "version": 1.0,
        "chapterId": 9999,
        "problemId": null,
        "isDefault": true,
        "book_id": null,
        "book_title": null,
        "chapter_title": null,
        "시험연도": "15",
        "시험종류": "01",
        "시험교시": "02",
        "문제번호": 7,
        "문제고유번호": "15010207",
        "대단원": null,
        "소단원": null,
        "소단원번호": null,
        "알렌문제번호": 99,
        "문제": "33세 산과력 0-0-0-0인 여자가 질 출혈로 병원에 왔다. 골반 초음파에서 특이 소견 없었고, 자궁경부질세포진검사\n에서 의미미결정 비정형편평세포(atypical squamous cell of undetermined significance)가 관찰되었다(두 가지).",
        "lab_data": null,
        "table": null,
        "사진들": null,
        "선지들": [
            "광범위 자궁 절제술 및 양측 부속기 절제술",
            "광범위 자궁목절제술 및 양측 부속기 절제술",
            "단순자궁절제술",
            "사람유두종바이러스검사",
            "원뿔절제술",
            "자궁경부질세포진검사",
            "자궁내막 긁어냄술",
            "질확대경검사"
        ],
        "정답들": [],
        "imp": [],
        "ddx": [],
        "correct_rate": 0.0
    },"""

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

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-pro"
)

prompt = f"해당 문제들을 바탕으로 문제번호를 포함해서서 주제나 단원별로 markdown형식으로 정리해. 이때, 문제번호는 원래 문제번호를 따라가. 그 다음에 마인드맵을 만들어줘\n\ntext: {text}"

server_params = StdioServerParameters(
    command="npx",
    args = ["-y", "@jinzcdev/markmap-mcp-server"],
    env = {"MARKMAP_DIR": r"C:\Users\Sese\AI_Study_Record\MCP\0702"}
)

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print(session)
            await session.initialize()
            print(session)
            
            tools = await load_mcp_tools(session)
            agent = create_react_agent(
                llm, tools
            )
            
            response = await astream_graph(
                graph = agent,
                inputs = {"messages":[HumanMessage(content=prompt)]}
            )
            return response

if __name__=="__main__":
    result = asyncio.run(main())