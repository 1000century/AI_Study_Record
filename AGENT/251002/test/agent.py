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