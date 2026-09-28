import os
import json
import requests

api_key = os.environ.get("GEMINI_API_KEY_WORD_OF_THE_DAY")

if not api_key:
    print("Error: GEMINI_API_KEY_WORD_OF_THE_DAY environment variable is empty or missing.", flush=True)
    exit(1)

languages = [
    "English", "Spanish", "French", "German", "Japanese", 
    "Italian", "Chinese", "Korean", "Khmer", "Afrikaans"
]

prompt = (
    f"Generate a JSON object with a key 'words' containing a list of objects. "
    f"Each object must have 'lang', 'word', 'translation', 'type', 'type_in_language', 'sentence1', and 'sentence2'.\n"
    f"CRITICAL RULE FOR SCRIPTS & WRITING:\n"
    f"- For ALL languages (including Khmer, Chinese, Japanese, Korean, Russian, Hindi, Arabic, etc.), write 'word', 'sentence1', and 'sentence2' using Latin/English script phonetics (Romanization/transliteration) so an English speaker can easily read and pronounce them.\n"
    f"- 'type': Part of speech in English (e.g., Noun, Verb, Adjective)\n"
    f"- 'type_in_language': Part of speech in the target language written in Latin/English script phonetics (e.g., 'byvoeglike naamwoord' for Afrikaans, 'kuna neam' for Khmer, 'adjetivo' for Spanish)\n"
    f"- 'sentence1' & 'sentence2': Example sentences written in English script phonetics showing how the word is used in that language, followed by its English translation in parentheses.\n"
    f"Provide one beautiful word for each of these languages: {', '.join(languages)}.\n"
    f"Return ONLY raw JSON text matching this schema. Do not wrap in markdown code blocks."
)

models_to_try = [
    "models/gemini-3.8-flash",
    "models/gemini-3.5-flash-lite"
]

def generate():
    for clean_model in models_to_try:
        print(f"Attempting generation with model: {clean_model}...", flush=True)
        url = f"https://generativelanguage.googleapis.com/v1/{clean_model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
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
                print(f"Success! Generated words.json using model: {clean_model}", flush=True)
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
