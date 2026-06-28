import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# ============================================================
# Environment
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set."
    )


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    temperature=0,
)