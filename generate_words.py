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

# Load recent word history to prevent ANY repetition
history_file = 'history.json'
recent_words = []

if os.path.exists(history_file):
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            recent_words = json.load(f)
    except Exception as e:
        print(f"Notice: Could not load history file: {e}", flush=True)

if os.path.exists('words.json'):
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            for w in old_data.get('words', []):
                word_text = w.get('word') or w.get('text')
                if word_text and word_text not in recent_words:
                    recent_words.append(word_text)
    except Exception:
        pass

# Add known clichés to exclusion list
cliches = ["Vellichor", "Petrichor", "Serendipity", "Sonder", "Ethereal", "Aurora", "Limerence", "Ephemeral", "Auraforge", "Epiphron"]
for c in cliches:
    if c not in recent_words:
        recent_words.append(c)

# Keep last 150 words in exclusion history
exclusion_list = recent_words[-150:]

today_str = datetime.date.today().strftime("%B %d, %Y")
topics = ["nature & seasons", "emotions & feelings", "art & beauty", "wisdom & philosophy", "daily life & wonder", "courage & inspiration", "friendship & connection", "space & universe", "starlight & dreams", "harvest & joy"]
today_topic = random.choice(topics)

prompt = (
    f"Today is {today_str}. Generate a JSON object with a key 'words' containing a list of objects. "
    f"Provide a brand new, unique, and beautiful word inspired by '{today_topic}' for each of these exact languages: {', '.join(languages)}.\n"
    f"STRICT EXCLUSION RULE:\n"
    f"- DO NOT use any of these previously used or cliché words: {', '.join(exclusion_list)}.\n"
    f"CRITICAL RULE FOR SCRIPTS & WRITING:\n"
    f"- For ALL languages in the list ({', '.join(languages)}), write 'word', 'sentence1', and 'sentence2' using Latin/English script phonetics (Romanization/transliteration) so an English speaker can easily read and pronounce them.\n"
    f"- 'type': Part of speech in English (e.g., Noun, Verb, Adjective)\n"
    f"- 'type_in_language': Part of speech in the target language written in Latin/English script phonetics (e.g., 'byvoeglike naamwoord' for Afrikaans, 'kuna neam' for Khmer, 'adjetivo' for Spanish)\n"
    f"- 'sentence1' & 'sentence2': Interesting example sentences written in English script phonetics showing how the word is used in that language, followed by its English translation in parentheses.\n"
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
                "temperature": 0.95
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            if response.status_code == 200:
                response_json = response.json()
                raw_text = response_json['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Validate schema
                data = json.loads(raw_text)
                new_words_list = data.get('words', [])
                
                # Save words.json
                with open('words.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # Update history.json
                for item in new_words_list:
                    wt = item.get('word') or item.get('text')
                    if wt and wt not in recent_words:
                        recent_words.append(wt)
                        
                with open(history_file, 'w', encoding='utf-8') as f:
                    json.dump(recent_words[-200:], f, ensure_ascii=False, indent=2)

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
