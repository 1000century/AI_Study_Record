from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from typing import AsyncGenerator


# 1. 콘텐츠 생성 에이전트
story_writer = LlmAgent(
    name="StoryWriter",
    model="gemini-2.0-flash-exp",
    instruction="""당신은 창의적인 작가입니다.
    사용자가 제공한 주제에 대해 짧은 이야기를 작성해주세요."""
)

# 2. 콘텐츠 검토 에이전트
story_critic = LlmAgent(
    name="StoryCritic",
    model="gemini-2.0-flash-exp",
    output_key="critic_decision",  # 직접 output_key 설정
    instruction="""당신은 비평가입니다.
    주어진 이야기가 주제에 맞고 흥미로운지 평가하고,
    반드시 '승인' 또는 '수정' 중 하나만 답변해주세요.
    다른 설명 없이 딱 한 단어만 답변하세요."""
)

# 3. 조건부 라우터
class ConditionalRouter(BaseAgent):
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        critic_decision = ctx.session.state.get("critic_decision", "")

        print(f"\n[Router] 비평가 결정: '{critic_decision}'")

        # '승인'이 포함되어 있으면 종료
        if "승인" in critic_decision:
            print("[Router] ✓ 승인됨 - 워크플로우 종료")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            print("[Router] ✗ 수정 필요 - 다시 작성")
            yield Event(author=self.name, actions=EventActions(escalate=False))

# 4. 워크플로우 구성
generative_flow = SequentialAgent(
    name="GenerativeWorkflow",
    sub_agents=[
        story_writer,
        story_critic,
        ConditionalRouter(name="Router")
    ]
)

# 5. 워크플로우 실행
async def main():
    session_service = InMemorySessionService()
    runner = Runner(
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

    print("\n" + "="*80)
    print("                      워크플로우 시작")
    print("="*80)
    print("\n[사용자] 우주 탐험에 대한 짧은 이야기를 써줘.\n")

    step = 0
    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=content
    ):
        step += 1

        # 에이전트별 시각화
        if event.author == "StoryWriter":
            print(f"\n{'─'*80}")
            print(f"📝 Step {step}: StoryWriter (작가)")
            print(f"{'─'*80}")
            if event.content and event.content.parts:
                story = event.content.parts[0].text
                print(f"[작성된 이야기]\n{story[:200]}..." if len(story) > 200 else f"[작성된 이야기]\n{story}")

        elif event.author == "StoryCritic":
            print(f"\n{'─'*80}")
            print(f"🔍 Step {step}: StoryCritic (비평가)")
            print(f"{'─'*80}")
            if event.content and event.content.parts:
                decision = event.content.parts[0].text.strip()
                print(f"[비평 결과] {decision}")

                # 상태 확인
                if event.actions and event.actions.state_delta:
                    print(f"[세션 저장] critic_decision = '{decision}'")

        elif event.author == "Router":
            print(f"\n{'─'*80}")
            print(f"🔀 Step {step}: Router (라우터)")
            print(f"{'─'*80}")

            if event.actions and event.actions.escalate is not None:
                if event.actions.escalate:
                    print("➜ 결정: 워크플로우 종료 ✓")
                else:
                    print("➜ 결정: 다시 작성 ↻")

    print("\n" + "="*80)
    print("                      워크플로우 종료")
    print("="*80 + "\n")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())