# backend/app/ai/extrapolation_router.py

# REDUNDANT - First attempt using sent excel data
from openai import OpenAI
import json

client = OpenAI()

async def runExtrapolationAI(payload: dict):

    system_prompt = """
You are an Extrapolation Analyst AI. Your job is to analyze a dataset and a user instruction,
choose the most appropriate extrapolation method, and generate four aligned output arrays:

1. values[]      — extrapolated or predicted numeric values
2. flags[]       — quality or status indicators for each row
3. methods[]     — the method used for each row or group of rows
4. confidence[]  — confidence score (0–1)

Rules:
- adapt to any dataset structure
- detect patterns automatically
- choose the best extrapolation strategy
- justify your choice internally (not in the output)
- handle missing or inconsistent data
- avoid hallucinating columns that do not exist
- never reorder rows
- always return arrays of equal length
- always return valid JSON
"""

    user_prompt = f"""
USER INSTRUCTION:
{payload.get('instruction')}

DATASET:
Headers: {json.dumps(payload.get('dataset', {}).get('headers', []))}
Rows: {json.dumps(payload.get('dataset', {}).get('rows', []))}

CONTEXT:
Run number: {payload.get('runNumber')}
User: {payload.get('userId')}

TASK:
Analyze the dataset and the instruction. Choose the best extrapolation method.
Generate the four output arrays.

OUTPUT FORMAT (MANDATORY):
{{
  "values": [...],
  "flags": [...],
  "methods": [...],
  "confidence": [...]
}}

Do not include explanations. Do not include text outside JSON.
"""

    # Call OpenAI Responses API
    response = client.responses.create(
        #model="gpt-4.1",
        model="gpt-4.1-mini",
        temperature=0.2,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract the text output
    content = response.output[0].content[0].text

    # Parse JSON safely
    try:
        return json.loads(content)
    except Exception:
        print("AI returned invalid JSON:", content)
        raise ValueError("AI returned invalid JSON")
