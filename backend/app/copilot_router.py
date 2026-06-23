# backend/app/copilot_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from openai import OpenAI
import json

from backend.app.tools.join_tools import load_clean_tables_for_copilot
from backend.app.services.extrapolation_orchestrator import ExtrapolationOrchestrator
from backend.app.tools.join_tools import build_joined_table

router = APIRouter()
client = OpenAI()


# ---------------------------------------------------------
# History model

class HistoryTurn(BaseModel):
    role: str
    content: Any


# ---------------------------------------------------------
# Request model
class CopilotRequest(BaseModel):
    history: List[HistoryTurn]
    message: str
    file_id: int


# ---------------------------------------------------------
# Chat endpoint (AI reasoning)
@router.post("")
def copilot_chat(req: CopilotRequest):

    print("DEBUG: Entered copilot_chat()")

    # 1. Load dataset context
    try:
        print("DEBUG: Before load_clean_tables_for_copilot")
        df_main, df_attr = load_clean_tables_for_copilot(req.file_id)
        print("DEBUG: After load_clean_tables_for_copilot")
    except Exception as e:
        print("ERROR: load_clean_tables_for_copilot failed:", repr(e))
        raise HTTPException(status_code=500, detail=f"Failed to load dataset: {e}")

    #headers = list(df_main.columns)
    #sample_rows = df_main.head(10).to_dict(orient="records")
    df_main, df_attr = load_clean_tables_for_copilot(req.file_id)
    # Build the joined table (this contains dimension)
    df_joined = build_joined_table(df_main, df_attr)

    # Use the joined table for the prompt
    headers = list(df_joined.columns)
    sample_rows = df_joined.head(5).to_dict(orient="records")

    print("DEBUG HEADERS SENT TO MODEL:", headers)
    print("DEBUG SAMPLE ROWS SENT TO MODEL:", sample_rows)

    # 2. Build conversation transcript
    history_text = ""
    for turn in req.history:
        history_text += f"{turn.role.upper()}: {str(turn.content)}\n"

    # 3. Build AI prompt
    prompt = f"""
SYSTEM:
You are a structured-output agent. You MUST respond ONLY with a JSON object that matches the schema below.
Nothing outside the JSON object is allowed. No markdown. No backticks. No headings. No code fences.

The JSON schema you MUST follow:

{{
  "reply": "a friendly, conversational natural-language reply to the user",
  "fields": ["list", "of", "fields", "to", "use"],
  "method": "analysis method or null",
  "notes": "extra notes or empty string",
  "action": "none | summarize | detect_zero_prices | extrapolate",
  "target": "unit_price",
  "attribute": "",
  "group_field": ""
}}

STRICT RULES:
- The *reply* field SHOULD be conversational, friendly, and helpful.
- NOTHING may appear outside the JSON object.
- The JSON MUST be valid and parseable by json.loads().
- If unsure, output a valid JSON object anyway.

MULTI-TURN DECISION RULES:
- NEVER guess the attribute field. If the user has not explicitly stated it, ask a clarifying question and set:
    "attribute": ""
- NEVER guess the grouping field. If the user has not explicitly stated it, ask a clarifying question and set:
    "group_field": ""
- NEVER set "action": "extrapolate" until:
    1. The user has explicitly confirmed they want extrapolation.
    2. The attribute field is known.
    3. The grouping field is known.
- If the user expresses analytical intent but details are missing, ask a clarifying question and set:
    "action": "none"
- If the user expresses interest in extrapolation but has not confirmed, set:
    "action": "none"
    and ask: "Would you like me to run extrapolation once we identify the attribute and grouping fields?"

ASSISTANT BEHAVIOR:
Inside the "reply" field:
- Speak naturally and conversationally.
- Guide the user through the steps needed to determine:
    - the attribute field (numeric predictor)
    - the grouping field (e.g., Country)
    - the action (summarize, detect_zero_prices, extrapolate)
- Ask one clarifying question at a time.
- Be concise, confident, and helpful.

USER CONTEXT:
You are helping the user analyze tabular cost data in Excel.
You should detect:
- missing or zero prices
- price-to-speed curves
- country-based differences
- regression or curve fitting opportunities
- extrapolation needs

CONVERSATION HISTORY:
{history_text}

LATEST USER MESSAGE:
{req.message}

DATASET HEADERS:
{headers}

SAMPLE ROWS:
{sample_rows}

END OF PROMPT.
"""




    # 4. Call OpenAI
    print("DEBUG: Before OpenAI call")
    completion = client.responses.create(
        model="gpt-4.1",
        input=prompt
    )
    print("DEBUG: After OpenAI call")

    raw_text = completion.output_text.strip()

    print("DEBUG RAW MODEL RESPONSE:\n", raw_text)



    # 5. Parse JSON safely
    try:
        parsed = json.loads(raw_text)
    except Exception:
        parsed = {
            "reply": raw_text,
            "fields": [],
            "method": None,
            "notes": "",
            "action": "none",
            "target": "unit_price",
            "attribute": None,
            "group_field": None
        }

    return parsed


# ---------------------------------------------------------
# Action endpoint (executes backend tools)
# ---------------------------------------------------------
class ActionRequest(BaseModel):
    file_id: int
    instruction: Dict[str, Any]


@router.post("/run")
def run_analysis(req: ActionRequest):

    orchestrator = ExtrapolationOrchestrator(req.file_id)
    result = orchestrator.run(req.instruction)

    return result
