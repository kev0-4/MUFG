# import os
# from dotenv import load_dotenv
# import google.generativeai as genai

# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# model = genai.GenerativeModel("gemini-2.5-flash")
# response = model.generate_content("Test query: What is superannuation?")
# print(response.text)

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content(
    "Test query: What is superannuation?",
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "object",
            "properties": {
                "heading": {"type": "string"},
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["heading"]
        }
    }
)

print(response.text)
