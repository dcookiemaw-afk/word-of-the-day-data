import os
import google.generativeai as genai
import json
import re

# We will use the library's preferred variable name
api_key = os.environ.get("GOOGLE_API_KEY_WORD_OF_THE_DAY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    # This will help us debug: it prints the first 4 characters of the key (if any exist)
    print(f"Available env vars: {[k for k in os.environ.keys() if 'API' in k]}")
    exit(1)

# Configure the AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

languages = ["English", "Spanish", "French", "German", "Japanese", "Italian", "Chinese", "Korean"]

prompt = (
    f"Generate a JSON object with a key 'words' containing a list of objects. "
    f"Each object must have 'lang', 'word', and 'translation'. "
    f"Provide one interesting word for each: {', '.join(languages)}. "
    f"Return ONLY raw JSON. No markdown."
)

try:
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Extract JSON just in case the AI adds markdown
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    
    data = json.loads(text)
    with open('words.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully updated words.json")

except Exception as e:
    print(f"Error: {e}")
    if 'text' in locals():
        print(f"AI Response was: {text}")
    exit(1)
