import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def load_model():
    return ChatOpenAI(
        model=os.environ.get("LLM_MODEL", "qwen2.5-7b"),
        api_key=os.environ.get("OPENAI_API_KEY", "not-needed"),
        base_url=os.environ.get("OPENAI_BASEURL", "http://192.168.31.120:9997/v1"),
        max_tokens=24800
    )

