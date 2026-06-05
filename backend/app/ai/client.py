from openai import OpenAI
import os

ai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)