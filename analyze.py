# analyze.py
import os
import json
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

RISK_SYSTEM_PROMPT = """You are a contract review assistant. You will be given the
full text of a contract. Identify individual clauses and assess their risk level
to the party signing (assume the reader is the tenant/contractor/weaker party
unless context suggests otherwise).

Return ONLY valid JSON, no markdown fences, no preamble, matching this schema:

{
  "document_type": "string, e.g. 'residential lease', 'freelance agreement'",
  "clauses": [
    {
      "clause_text": "short excerpt or paraphrase of the clause, under 30 words",
      "risk_level": "low | medium | high",
      "explanation": "plain-English explanation of why this matters, 1-2 sentences",
      "category": "e.g. 'termination', 'liability', 'payment', 'privacy'"
    }
  ],
  "missing_protections": [
    {
      "protection": "name of the standard clause that's absent",
      "why_it_matters": "1 sentence"
    }
  ],
  "overall_risk_score": "low | medium | high"
}
"""

def clean_json_response(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def analyze_contract(contract_text: str) -> dict:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=4000,
        system=RISK_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": contract_text}]
    )
    raw = response.content[0].text
    return clean_json_response(raw)