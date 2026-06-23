from openai import OpenAI
import json

client = OpenAI()

def run_copilot_ai(message: str, headers: list, sample_rows: list):
    system_prompt = (
        "You are an AI assistant helping analyse pricing data in Excel.\n"
        "You receive:\n"
        "- A user message\n"
        "- A list of column headers\n"
        "- A small sample of rows (5 max)\n\n"
        "Your job:\n"
        "1. Understand what the user wants.\n"
        "2. Decide which columns are relevant.\n"
        "3. Choose one method from: ['curve_fit', 'regression', 'summary', 'diagnostic'].\n"
        "4. Reply in natural language.\n"
        "5. Return ONLY a JSON object with keys: reply, fields, method, notes.\n"
        "Fields must be a subset of the provided headers.\n"
        "If unsure, set fields/method to null.\n"
    )

    user_prompt = (
        f"User message:\n{message}\n\n"
        f"Headers:\n{headers}\n\n"
        f"Sample rows:\n{sample_rows}\n\n"
        "Respond ONLY with a JSON object with keys: reply, fields, method, notes."
    )
