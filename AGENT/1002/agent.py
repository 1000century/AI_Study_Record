from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from a .env file if present

from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm




root_agent = Agent(
    model=LiteLlm(
        model = 'openai/HCX-007',
        api_key = os.getenv('CLOVA_API_KEY'),
        api_base = 'https://clovastudio.stream.ntruss.com/v1/openai'
    ),
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

session_service = InMemorySessionService()


USER_ID = "sese_1234"
SESSION_ID = "session_1234"



from google.genai import types
async def call_agent_async(query:str, runner, user_id:str, session_id:str):
    print(f"\n>>> User: {query}\n")
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    
    final_response_text = "에이전트는 마지막 응답을 생성하지 못했습니다."
    
    
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
      

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    print(f"\n>>> Agent Final Response: {repr(final_response_text)}\n")

# @title Run the Initial Conversation

# We need an async function to await our interaction helper
async def run_conversation():

    session = await session_service.create_session(
        app_name="데모",
        user_id=USER_ID,
        session_id = SESSION_ID
    )

    runner = Runner(
        agent = root_agent,
        app_name = "데모",
        session_service = session_service
    )


    await call_agent_async("런던의 날씨는 어때?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

    await call_agent_async("How about Paris?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID) # Expecting the tool's error message

    await call_agent_async("지금까지 내 질문들을 요약해",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)


# --- OR ---

# Uncomment the following lines if running as a standard Python script (.py file):
import asyncio
if __name__ == "__main__":
    try:
        asyncio.run(run_conversation())
    except Exception as e:
        print(f"An error occurred: {e}")