import os
import google.generativeai as genai
import json
import re

# Set up Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Define the languages you want to support
languages = ["English", "Spanish", "French", "German", "Japanese", "Italian", "Chinese", "Korean"]

# Create the AI Prompt
prompt = (
    f"Generate a JSON object with a key 'words' containing a list of objects. "
    f"Each object must have 'lang', 'word', and 'translation'. "
    f"Provide one interesting word for each of these languages: {', '.join(languages)}. "
    f"Return ONLY the JSON. No markdown formatting."
)

try:
    response = model.generate_content(prompt)
    # Clean the response to ensure it's valid JSON
    text = response.text
    if "```json" in text:
        text = re.search(r"```json\n(.*?)\n```", text, re.DOTALL).group(1)
    
    # Validate JSON
    data = json.loads(text)
    
    # Save to file
    with open('words.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully updated words.json")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
