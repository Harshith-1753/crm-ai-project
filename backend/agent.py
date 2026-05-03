
import json
import re
from datetime import datetime, timedelta
from tools import summarize_tool, suggest_tool, extract_interaction_tool
from llm import ask_llm
from db import save_interaction, get_last_interaction



# 🔥 MEMORY
last_interaction = get_last_interaction()

# =========================
# 🧠 DATE PARSER
# =========================
def parse_natural_date(text):
    text = text.lower().strip()
    today = datetime.today()

    # tomorrow
    if "tomorrow" in text:
        return (today + timedelta(days=1)).strftime("%B %d")

    # next weekday
    days = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }

    for day in days:
        if f"next {day}" in text:
            today_weekday = today.weekday()
            target_day = days[day]

            days_ahead = (target_day - today_weekday + 7) % 7
            if days_ahead == 0:
                days_ahead = 7

            return (today + timedelta(days=days_ahead)).strftime("%B %d")

    # "15 april"
    try:
        parsed = datetime.strptime(text + " 2026", "%d %B %Y")
        return parsed.strftime("%B %d")
    except:
        pass

    # "april 15"
    try:
        parsed = datetime.strptime(text + " 2026", "%B %d %Y")
        return parsed.strftime("%B %d")
    except:
        pass

    return text


# =========================
# 🧠 UPDATE PARSER (FIXED)
# =========================
def parse_update_fields(text):
    updates = {}

    parts = [p.strip() for p in text.split(" and ")]

    for part in parts:

        # doctor
        match = re.search(r"(?:doctor|dr)\s*(?:to)\s*([a-zA-Z ]+)", part)
        if match:
            updates["doctor"] = match.group(1).strip().title()
            continue

        # date
        match = re.search(r"date\s*(?:to)\s*([a-zA-Z0-9 ]+)", part)
        if match:
            raw_date = match.group(1).strip()
            parsed_date = parse_natural_date(raw_date)

            if len(parsed_date.split()) <= 3:
                updates["date"] = parsed_date
            continue

        # type
        match = re.search(r"type\s*(?:to)\s*([a-zA-Z ]+)", part)
        if match:
            updates["type"] = match.group(1).strip().lower()
            continue

        # notes
        match = re.search(r"notes?\s*(?:to)\s*(.+)", part)
        if match:
            updates["notes"] = match.group(1).strip()
            continue

    return updates


# =========================
# 🚀 MAIN LOGIC
# =========================
def agent_logic(input_text):
    global last_interaction

    text = input_text.lower()

    # =========================
    # 🔥 UPDATE EXISTING
    # =========================
    if any(word in text for word in ["change", "update", "modify"]):

        if not last_interaction:
            return "No existing interaction to update."

        updates = parse_update_fields(text)

        updated = last_interaction.copy()
        updated.update(updates)

        last_interaction = updated

        print("UPDATED DATA:", updated)
        return updated


    # =========================
    # 🔥 FORM CREATION
    # =========================
    elif any(word in text for word in [
        "dr", "doctor", "met", "april", "may", "june",
        "treatment", "discussed"
    ]):

        extracted = extract_interaction_tool(input_text)

        if isinstance(extracted, str):
            try:
                extracted = json.loads(extracted)
            except:
                extracted = {}

        final_data = {
            "doctor": extracted.get("doctor", ""),
            "date": extracted.get("date", ""),
            "type": extracted.get("type", ""),
            "notes": extracted.get("notes", "")
        }

        last_interaction = final_data

        print("FINAL EXTRACTED:", final_data)
        return final_data


    # =========================
    # 🔥 SUMMARY
    # =========================
    elif "summary" in text or "summarize" in text:
        return summarize_tool(input_text, last_interaction)


    # =========================
    # 🔥 SUGGESTION (CONTEXT-AWARE)
    # =========================
    elif any(word in text for word in ["next", "suggest"]):

        if not last_interaction:
            return "No interaction available to suggest next steps."

        context = f"""
Doctor: {last_interaction.get('doctor')}
Date: {last_interaction.get('date')}
Type: {last_interaction.get('type')}
Notes: {last_interaction.get('notes')}
"""

        return ask_llm(f"""
Based on the following medical interaction, suggest next steps:

{context}
""")


    # =========================
    # 🔥 GENERAL CHAT
    # =========================
    else:
        return ask_llm(input_text)
