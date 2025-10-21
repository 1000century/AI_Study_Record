from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


class State(TypedDict):
    """에이전트 상태"""
    count: int
    messages: list[str]


def start_node(state: State) -> State:
    """시작 노드"""
    return {
        "count": state["count"],
        "messages": state.get("messages", []) + ["Started"]
    }


def increment(state: State) -> State:
    """카운트 증가"""
    return {
        "count": state["count"] + 1,
        "messages": state.get("messages", []) + [f"Incremented to {state['count'] + 1}"]
    }


def double(state: State) -> State:
    """카운트 두 배로"""
    return {
        "count": state["count"] * 2,
        "messages": state.get("messages", []) + [f"Doubled to {state['count'] * 2}"]
    }


def end_node(state: State) -> State:
    """종료 노드"""
    return {
        "count": state["count"],
        "messages": state.get("messages", []) + ["Finished"]
    }


def should_double(state: State) -> Literal["double", "end"]:
    """카운트가 5보다 작으면 double, 아니면 end"""
    if state["count"] < 5:
        return "double"
    return "end"


# 그래프 생성
workflow = StateGraph(State)

# 노드 추가
workflow.add_node("start", start_node)
workflow.add_node("increment", increment)
workflow.add_node("double", double)
workflow.add_node("end", end_node)

# 시작점 설정
workflow.set_entry_point("start")

# 엣지 추가
workflow.add_edge("start", "increment")
workflow.add_conditional_edges(
    "increment",
    should_double,
    {
        "double": "double",
        "end": "end"
    }
)
workflow.add_edge("double", "end")
workflow.add_edge("end", END)

# 컴파일
graph = workflow.compile()
