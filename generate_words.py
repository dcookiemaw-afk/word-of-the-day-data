import os
import json
import requests
import datetime
import random

api_key = os.environ.get("GEMINI_API_KEY_WORD_OF_THE_DAY")

if not api_key:
    print("Error: GEMINI_API_KEY_WORD_OF_THE_DAY environment variable is empty or missing.", flush=True)
    exit(1)

languages = [
    "English", "Spanish", "French", "German", "Japanese", 
    "Italian", "Chinese", "Korean", "Khmer", "Afrikaans"
]

# Dynamic date and randomized topic so Gemini generates fresh, non-repeating words every day!
today_str = datetime.date.today().strftime("%B %d, %Y")
topics = ["nature & seasons", "emotions & feelings", "art & beauty", "wisdom & philosophy", "daily life & wonder", "courage & inspiration", "friendship & connection"]
today_topic = random.choice(topics)

prompt = (
    f"Today is {today_str}. Generate a JSON object with a key 'words' containing a list of objects. "
    f"Provide a brand new, unique, and beautiful word inspired by '{today_topic}' for each of these exact languages: {', '.join(languages)}.\n"
    f"CRITICAL RULE FOR SCRIPTS & WRITING:\n"
    f"- For ALL languages in the list ({', '.join(languages)}), write 'word', 'sentence1', and 'sentence2' using Latin/English script phonetics (Romanization/transliteration) so an English speaker can easily read and pronounce them.\n"
    f"- 'type': Part of speech in English (e.g., Noun, Verb, Adjective)\n"
    f"- 'type_in_language': Part of speech in the target language written in Latin/English script phonetics (e.g., 'byvoeglike naamwoord' for Afrikaans, 'kuna neam' for Khmer, 'adjetivo' for Spanish)\n"
    f"- 'sentence1' & 'sentence2': Interesting example sentences written in English script phonetics showing how the word is used in that language, followed by its English translation in parentheses.\n"
    f"IMPORTANT: Ensure the generated words are fresh, unique, and DIFFERENT from common cliché default words.\n"
    f"Return ONLY raw JSON text matching this schema. Do not wrap in markdown code blocks."
)

models_to_try = [
    "models/gemini-3.8-flash",
    "models/gemini-3.5-flash-lite"
]

def generate():
    for clean_model in models_to_try:
        print(f"Attempting generation for {today_str} (Topic: {today_topic}) with model: {clean_model}...", flush=True)
        url = f"https://generativelanguage.googleapis.com/v1/{clean_model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.9
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            if response.status_code == 200:
                response_json = response.json()
                raw_text = response_json['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Validate schema
                data = json.loads(raw_text)
                with open('words.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Success! Generated fresh words.json using model: {clean_model}", flush=True)
                return True
            else:
                print(f"Model {clean_model} returned code {response.status_code}: {response.text}", flush=True)
        except Exception as err:
            print(f"Skipping model {clean_model} due to error: {err}", flush=True)
            
    return False

if __name__ == "__main__":
    if generate():
        print("Workflow completed successfully!", flush=True)
    else:
        print("CRITICAL: All available Gemini endpoints failed.", flush=True)
        exit(1)
