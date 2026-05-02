import json
import re
from llm import ask_llm


# 🔹 SUMMARY TOOL (uses context)
def summarize_tool(text, context=None):
    if context:
        return ask_llm(f"""
Summarize this medical interaction:

Doctor: {context.get("doctor")}
Date: {context.get("date")}
Type: {context.get("type")}
Notes: {context.get("notes")}
""")
    return ask_llm(f"Summarize: {text}")


# 🔹 SUGGEST TOOL (CONTEXT AWARE)
def suggest_tool(user_text, context=None):
    if context:
        return ask_llm(f"""
User had this medical interaction:

Doctor: {context.get("doctor")}
Date: {context.get("date")}
Type: {context.get("type")}
Notes: {context.get("notes")}

Question: {user_text}

Give specific next steps related to THIS case.
Avoid generic advice.
""")
    return ask_llm(user_text)


# 🔹 EXTRACTION TOOL (ROBUST)
def extract_interaction_tool(text):
    prompt = f"""
Extract structured information from the text.

IMPORTANT RULES:
- "doctor" → name of doctor
- "date" → date of interaction
- "type" → MUST be one of:
  ["meeting", "discussion", "treatment", "follow-up"]
- DO NOT put diseases in "type"
- "notes" → remaining details

Text: {text}

Return ONLY valid JSON:
{{
  "doctor": "",
  "date": "",
  "type": "",
  "notes": ""
}}
"""

    response = ask_llm(prompt)

    try:
        clean = re.sub(r"```json|```", "", response).strip()
        data = json.loads(clean)

        # 🔥 RULE-BASED FIX FOR TYPE
        text_lower = text.lower()

        if "treatment" in text_lower:
            data["type"] = "treatment"
        elif "follow" in text_lower:
            data["type"] = "follow-up"
        elif "discuss" in text_lower:
            data["type"] = "discussion"
        elif "met" in text_lower:
            data["type"] = "meeting"

        return {
            "doctor": data.get("doctor", ""),
            "date": data.get("date", ""),
            "type": data.get("type", ""),
            "notes": data.get("notes", "")
        }

    except Exception as e:
        print("❌ ERROR parsing LLM output:", response)

        return {
            "doctor": "",
            "date": "",
            "type": "",
            "notes": text
        }