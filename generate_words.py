import os
import json
from google import genai
from google.genai import types

# Read the environment variable passed by GitHub
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY environment variable is empty or missing.")
    exit(1)

# Configure the client
client = genai.Client(api_key=api_key)

# Define the languages you want to support
languages = ["English", "Spanish", "French", "German", "Japanese", "Italian", "Chinese", "Korean"]

prompt = f"Provide one interesting word of the day with its English translation for each of these languages: {', '.join(languages)}."

try:
    # Use Structured JSON Output configuration to guarantee valid JSON formatting
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "words": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "lang": types.Schema(type=types.Type.STRING),
                                "word": types.Schema(type=types.Type.STRING),
                                "translation": types.Schema(type=types.Type.STRING),
                            },
                            required=["lang", "word", "translation"],
                        ),
                    )
                },
                required=["words"],
            ),
        ),
    )

    text = response.text.strip()
    
    # Validate and save data
    data = json.loads(text)
    with open('words.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Successfully generated and saved words.json via Structured Output!")

except Exception as e:
    print(f"Error occurred during generation: {e}")
    if 'response' in locals() and hasattr(response, 'text'):
        print(f"Raw response text: {response.text}")
    exit(1)
