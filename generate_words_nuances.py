import os
import json
import requests
import datetime
import random
import time

api_key = os.environ.get("GEMINI_API_KEY_WORD_OF_THE_DAY")

if not api_key:
    print("Error: GEMINI_API_KEY_WORD_OF_THE_DAY environment variable is empty or missing.", flush=True)
    exit(1)

languages = [
    "English", "Spanish", "French", "German", "Japanese",
    "Italian", "Chinese", "Korean", "Khmer", "Afrikaans"
]

history_file = 'exclusion_history_nuances.json'
exclusions_by_lang = {}

if os.path.exists(history_file):
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            exclusions_by_lang = json.load(f)
    except Exception as e:
        print(f"Notice: Loading existing nuances exclusion history: {e}", flush=True)

exclusion_prompt_lines = []
for lang in languages:
    excluded_words = exclusions_by_lang.get(lang, [])
    if excluded_words:
        exclusion_prompt_lines.append(f"- {lang}: DO NOT use {', '.join(excluded_words[-50:])}")

exclusion_text = "\n".join(exclusion_prompt_lines)

today_str = datetime.date.today().strftime("%B %d, %Y")
topics = ["cultural nuances", "untranslatable feelings", "unique idioms", "proverbs & wisdom", "subtle expressions", "deep social customs"]
today_topic = random.choice(topics)

prompt = (
    f"Today is {today_str}. Generate a JSON object with a key 'nuances' containing a list of objects. "
    f"Provide a unique language nuance, idiom, untranslatable word, or deep cultural expression inspired by '{today_topic}' for each of these exact languages: {', '.join(languages)}.\n"
    f"STRICT PER-LANGUAGE EXCLUSION RULES (DO NOT REPEAT ANY OF THESE):\n"
    f"{exclusion_text}\n"
    f"SCHEMA REQUIREMENTS:\n"
    f"- 'language': Target language name\n"
    f"- 'phrase': The word, idiom, or expression written in Latin/English script phonetics\n"
    f"- 'literal_meaning': Direct English translation of the phrase\n"
    f"- 'nuance_explanation': A 1-2 sentence explanation of the subtle cultural, emotional, or social context behind this expression\n"
    f"- 'example_usage': A practical example sentence showing how it is used in conversation\n"
    f"Return ONLY raw JSON text matching this schema. Do not wrap in markdown code blocks."
)

models_to_try = [
    "models/gemini-3.8-flash",
    "models/gemini-3.5-flash-lite"
]

def generate():
    for clean_model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1/{clean_model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.95
            }
        }

        for attempt in range(1, 4):
            print(f"Attempting nuances generation for {today_str} (Topic: {today_topic}) with model: {clean_model} (Attempt {attempt}/3)...", flush=True)
            try:
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=90)
                if response.status_code == 200:
                    response_json = response.json()
                    raw_text = response_json['candidates'][0]['content']['parts'][0]['text'].strip()

                    if raw_text.startswith("```"):
                        raw_text = raw_text.split("```")[1]
                        if raw_text.startswith("json"):
                            raw_text = raw_text[4:].strip()
                        raw_text = raw_text.strip("`").strip()

                    parsed_data = json.loads(raw_text)
                    if isinstance(parsed_data, list):
                        data = {"nuances": parsed_data}
                        new_list = parsed_data
                    elif isinstance(parsed_data, dict):
                        data = parsed_data
                        new_list = data.get('nuances', [])
                    else:
                        raise ValueError("Parsed JSON is neither a list nor a dictionary.")

                    with open('words_nuances.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    for item in new_list:
                        l = item.get('lang') or item.get('language')
                        phrase = item.get('phrase') or item.get('word')
                        if l and phrase:
                            if l not in exclusions_by_lang:
                                exclusions_by_lang[l] = []
                            if phrase not in exclusions_by_lang[l]:
                                exclusions_by_lang[l].append(phrase)

                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump(exclusions_by_lang, f, ensure_ascii=False, indent=2)

                    print(f"Success! Generated fresh words_nuances.json using model: {clean_model}", flush=True)
                    return True
                else:
                    print(f"Model {clean_model} returned code {response.status_code}: {response.text}", flush=True)
                    break
            except Exception as err:
                print(f"Skipping attempt {attempt} for model {clean_model} due to error: {err}", flush=True)
                if attempt < 3:
                    time.sleep(10 * attempt)

    return False

if __name__ == "__main__":
    if generate():
        print("Nuances workflow completed successfully!", flush=True)
    else:
        print("CRITICAL: All available Gemini endpoints failed for nuances.", flush=True)
        exit(1)
