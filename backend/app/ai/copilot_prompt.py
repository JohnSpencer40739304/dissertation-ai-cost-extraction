from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
client = OpenAI()
app = FastAPI()

SYSTEM_PROMPT = """
You are a lightweight helper inside Excel.

Your job is to:
1. Ask the user which fields are important.
2. Suggest the simplest analysis method.
3. Produce a tiny JSON instruction for the backend.

You NEVER perform calculations.
You NEVER return raw data.
You ONLY help the user decide what to send.

Your final output MUST be:

{
  "fields": [...],
  "method": "<method>",
  "notes": "<short explanation>"
}

Where <method> is one of:
- correlation
- regression
- curve_fit
- clustering
- outliers
- forecast
"""

class CopilotMessage(BaseModel):
    message: str
@app.post("/copilot")
def copilot_chat(msg: CopilotMessage):
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": msg.message}
        ]
    )
    reply = completion.choices[0].message["content"]
    return {"reply": reply}
