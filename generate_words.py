import os
import json
import requests

# Read the environment variable passed by GitHub
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable is empty or missing.")
    exit(1)

languages = ["English", "Spanish", "French", "German", "Japanese", "Italian", "Chinese", "Korean"]

prompt = (
    f"Generate a JSON object with a key 'words' containing a list of objects. "
    f"Each object must have 'lang', 'word', and 'translation'. "
    f"Provide one interesting word for each: {', '.join(languages)}. "
    f"Return ONLY raw JSON text matching this schema. Do not wrap in markdown text blocks."
)

def discover_and_generate():
    # Step 1: Query Google to see what models this key is authorized to use
    list_url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
    try:
        print("Discovering available models on your account...")
        list_response = requests.get(list_url)
        if list_response.status_code != 200:
            print(f"Failed to list models: {list_response.text}")
            return False
            
        models_data = list_response.json()
        # Find all models that support generating content
        available_models = [
            m["name"] for m in models_data.get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
        print(f"Authorized models found on your account: {available_models}")
        
    except Exception as e:
        print(f"Error during model discovery phase: {e}")
        # Fallback list if discovery fails
        available_models = ["models/gemini-2.0-flash-lite", "models/gemini-2.0-flash", "models/gemini-pro"]

    # Step 2: Try each available model until one succeeds
    for model_path in available_models:
        # Strip out any double 'models/' prefixing if present
        clean_model = model_path if model_path.startswith("models/") else f"models/{model_path}"
        print(f"Attempting production generation with: {clean_model}...")
        
        url = f"https://generativelanguage.googleapis.com/v1/{clean_model}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                response_json = response.json()
                raw_text = response_json['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Save the validated data asset file
                data = json.loads(raw_text)
                with open('words.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Success! Generated words.json using model: {clean_model}")
                return True
            else:
                print(f"Model {clean_model} rejected request with code {response.status_code}: {response.text}")
        except Exception as err:
            print(f"Skipping model {clean_model} due to parsing error: {err}")
            
    return False

if __name__ == "__main__":
    if discover_and_generate():
        print("Workflow completed successfully!")
    else:
        print("CRITICAL: All available Gemini endpoints rejected the API Key layout profile mapping configuration.")
        exit(1)
