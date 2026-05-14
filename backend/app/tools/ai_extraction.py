from openai import OpenAI
import json

client = OpenAI()

def extract_attributes_with_ai(description: str) -> dict:
    if not description:
        return {}

    prompt = f"""
    Extract structured attributes from this description.
    Return ONLY valid JSON.

    Description: "{description}"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {}
