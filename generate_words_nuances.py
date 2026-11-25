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

history_file = 'exclusion_history_nuances.json'
exclusions_list = []

if os.path.exists(history_file):
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            exclusions_data = json.load(f)
            if isinstance(exclusions_data, list):
                exclusions_list = exclusions_data
            elif isinstance(exclusions_data, dict):
                exclusions_list = exclusions_data.get("English", [])
    except Exception as e:
        print(f"Notice: Loading existing nuances exclusion history: {e}", flush=True)

exclusion_text = f"DO NOT use any of these previously generated nuances/titles: {', '.join(exclusions_list[-50:])}" if exclusions_list else "No previous exclusions."

today_str = datetime.date.today().strftime("%B %d, %Y")
topics = ["commonly confused words", "idioms with rich history", "misunderstood sayings", "subtle conversational distinctions", "unique English phrasing", "grammatical & tone nuances"]
today_topic = random.choice(topics)

prompt = (
    f"Today is {today_str}. Generate a JSON object with a key 'nuances' containing a list of 1 object. "
    f"Provide a unique English linguistic nuance inspired by '{today_topic}'. "
    f"This can be a pair of commonly confused/misused words (e.g., 'Sarcastic vs Sardonic', 'Affect vs Effect'), "
    f"a subtle conversational phrase/saying with interesting origins (e.g., 'Bite the bullet', 'Keeping up appearances'), "
    f"or a commonly misspoken expression (e.g., 'For all intents and purposes' vs 'For all intensive purposes').\n"
    f"EXCLUSION RULE: {exclusion_text}\n"
    f"SCHEMA REQUIREMENTS:\n"
    f"- 'language': 'English'\n"
    f"- 'title': Main topic title (e.g., 'Sarcastic vs Sardonic' or 'Bite the bullet' or 'For all intents and purposes')\n"
    f"- 'type': Category type (e.g., 'Word Comparison', 'Idiom & Origin', 'Common Misconception', 'Conversational Nuance')\n"
    f"- 'meaning': Clear, direct English definition or core meaning\n"
    f"- 'nuance_explanation': A 1-2 sentence breakdown of the subtle distinction, historical origin, or conversational context\n"
    f"- 'example_usage': A natural example sentence demonstrating correct usage in conversation\n"
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
                        title = item.get('title') or item.get('phrase') or item.get('word1')
                        if title:
                            if title not in exclusions_list:
                                exclusions_list.append(title)
                            
                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump({"English": exclusions_list}, f, ensure_ascii=False, indent=2)

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
        print("Versatile nuances workflow completed successfully!", flush=True)
    else:
        print("CRITICAL: All available Gemini endpoints failed for nuances.", flush=True)
        exit(1)
