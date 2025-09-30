from dotenv import load_dotenv

load_dotenv()

from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from typing import AsyncGenerator


# 1. 콘텐츠 생성 에이전트 정의
story_writer = LlmAgent(
    name="StoryWriter",
    model="gemini-2.0-flash-exp",
    instruction="""당신은 창의적인 작가입니다.
    사용자가 제공한 주제에 대해 짧은 이야기를 작성해주세요."""
)

# 2. 콘텐츠 검토 에이전트 정의
story_critic = LlmAgent(
    name="StoryCritic",
    model="gemini-2.0-flash-exp",
    instruction="""당신은 비평가입니다.
    주어진 이야기가 주제에 맞고 흥미로운지 평가하고,
    '승인' 또는 '수정'으로만 답변해주세요."""
)

# 3. 조건부 흐름을 위한 사용자 정의 에이전트
class ConditionalRouter(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # 이전 단계(StoryCritic)의 결과 확인
        critic_decision = ctx.session.state.get("critic_decision")

        # '승인'일 경우 워크플로우 종료
        if critic_decision == "승인":
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            # 그 외의 경우(수정) 다음 단계로 진행
            yield Event(author=self.name, actions=EventActions(escalate=False))

# 4. 워크플로우 구성
# SequentialAgent를 사용하여 에이전트들을 순차적으로 연결합니다.
# LoopAgent와 같은 다른 워크플로우 에이전트를 사용하여 반복적인 작업을 처리할 수도 있습니다. [8, 9]
generative_flow = SequentialAgent(
    name="GenerativeWorkflow",
    sub_agents=[
        story_writer,
        # LlmAgent의 출력을 세션 상태에 저장하여 다음 에이전트가 사용할 수 있도록 합니다.
        LlmAgent(
            name="SaveCriticInput",
            model="gemini-2.0-flash-exp",
            output_key="critic_input",  # story_writer의 출력을 critic_input 키로 저장
            instruction="""다음 에이전트가 사용할 수 있도록 이전 단계의 출력을 저장합니다."""
        ),
        story_critic,
        # story_critic의 출력을 critic_decision 키로 저장
        LlmAgent(
            name="SaveCriticDecision",
            model="gemini-2.0-flash-exp",
            output_key="critic_decision",
            instruction="""다음 에이전트가 사용할 수 있도록 이전 단계의 출력을 저장합니다."""
        ),
        ConditionalRouter(name="Router")
    ]
)

# 5. 워크플로우 실행
async def main():
    session_service = InMemorySessionService()
    runner =  Runner(
        session_service=session_service,
        app_name="GenerativeApp",
        agent=generative_flow,
    )


    session_id = "session1"
    await session_service.create_session(
        app_name="GenerativeApp",
        user_id="user1",
        session_id=session_id
    )

    content = types.Content(
        role="user", 
        parts=[types.Part(text="우주 탐험에 대한 짧은 이야기를 써줘.")]
    )


    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=content
    ):
        # 각 에이전트별로 출력 확인 (모든 이벤트)
        print(f"\n{'='*50}")
        print(f"에이전트: {event.author}")
        print(f"{'='*50}")

        if event.content and event.content.parts:
            print(f"출력:\n{event.content.parts[0].text}")

        # 세션 상태 확인 (event에서 직접 확인)
        if hasattr(event, 'actions') and event.actions and event.actions.state_delta:
            print(f"\n상태 변경: {event.actions.state_delta}")
        print(event.actions)

        # Escalate 상태 확인
        if hasattr(event, 'actions') and event.actions:
            if event.actions.escalate is not None:
                print(f"Escalate: {event.actions.escalate}")

        # 최종 응답 확인 (종료하지 않고 계속 진행)
        if event.is_final_response():
            print(f"\n*** 최종 응답 ***")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())