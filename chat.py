# chat.py
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def chat_with_contract(contract_text: str, conversation_history: list, user_message: str) -> str:
    system = f"""You are answering questions about the following contract.
Ground every answer in the actual text — quote or reference the relevant
clause when possible. If the answer isn't in the document, say so clearly.
Keep answers concise and in plain English.

CONTRACT TEXT:
{contract_text}
"""
    messages = conversation_history + [{"role": "user", "content": user_message}]

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        system=system,
        messages=messages
    )
    return response.content[0].text