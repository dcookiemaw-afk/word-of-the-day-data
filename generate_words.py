import os
import google.generativeai as genai
import json
import re

# Read the environment variable passed by GitHub
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable is empty or missing.")
    exit(1)

# Configure the AI library
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Define the languages you want to support
languages = ["English", "Spanish", "French", "German", "Japanese", "Italian", "Chinese", "Korean"]

prompt = (
    f"Generate a JSON object with a key 'words' containing a list of objects. "
    f"Each object must have 'lang', 'word', and 'translation'. "
    f"Provide one interesting word for each: {', '.join(languages)}. "
    f"Return ONLY raw JSON text. Do not wrap in markdown tags."
)

try:
    response = model.generate_content(prompt)
    text = response.text.strip()
    
    # Extract JSON content
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    
    data = json.loads(text)
    with open('words.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully generated and saved words.json!")

except Exception as e:
    print(f"Error occurred during generation: {e}")
    if 'text' in locals():
        print(f"Raw text received from AI: {text}")
    exit(1)
