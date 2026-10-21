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

    # Remove Markdown code fences if Claude adds them.
    if raw.startswith("```"):
        lines = raw.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        raw = "\n".join(lines).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Claude returned invalid or incomplete JSON "
            f"at line {exc.lineno}, column {exc.colno}. "
            "The response may be truncated. "
            "Check the model output and token limit."
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("Claude's response must be a JSON object.")

    return result


def analyze_contract(contract_text: str) -> dict:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=8000,
        system=RISK_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": contract_text
            }
        ]
    )

    # Detect a response cut off by the output-token limit.
    if response.stop_reason == "max_tokens":
        raise ValueError(
            "Claude's response was truncated because it reached "
            "the output-token limit. Increase max_tokens or "
            "reduce the requested analysis length."
        )

    raw = "".join(
        block.text
        for block in response.content
        if block.type == "text"
    )

    if not raw.strip():
        raise ValueError("Claude returned an empty response.")

    return clean_json_response(raw)
