from openai import OpenAI

client = OpenAI()

import unicodedata
import json

# added to handle curly quotes of AI prompts
def sanitize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u00A0", " ")
    return text



def ai_extract_any_table(text: str):
    text = sanitize_text(text)
    prompt = f"""
    You are a document extraction model.

    Extract ALL tables from the text below.
    A table is any group of values arranged in rows and columns.

    Output JSON in this exact structure:

    {{
      "tables": [
        {{
          "headers": ["header1", "header2", ...],
          "rows": [
            ["cell1", "cell2", ...],
            ["cell1", "cell2", ...]
          ]
        }}
      ]
    }}

    If headers are missing, infer them.
    If a row has missing cells, fill with null.

    TEXT:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    #return response.choices[0].message.parsed
    #return json.loads(response.choices[0].message.content[0].text)
    json_text = response.choices[0].message.content
    return json.loads(json_text)
