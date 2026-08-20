"""
Unified LLM client -- routes to either local Ollama (free, used in dev)
or Groq (free tier, used for the hosted demo where Ollama isn't available)
based on the LLM_PROVIDER environment variable. Both generation.py and
assessor.py call generate_text() instead of talking to Ollama directly,
so the same prompts and logic work in both environments unchanged.
"""

import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

OLLAMA_MODEL = "llama3.1:8b"
GROQ_MODEL = "openai/gpt-oss-20b"

def generate_text(prompt: str, temperature: float = 0.7) -> str:
    if LLM_PROVIDER == "groq":
        return _generate_groq(prompt, temperature)
    return _generate_ollama(prompt, temperature)


def _generate_ollama(prompt: str, temperature: float) -> str:
    import ollama
    response = ollama.generate(
        model=OLLAMA_MODEL,
        prompt=prompt,
        options={"temperature": temperature},
    )
    return response["response"]


def _generate_groq(prompt: str, temperature: float) -> str:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content