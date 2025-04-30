from google import genai
from google.genai import types

from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

async def generate_response(prompt):

    try:
        response = client.models.generate_content(
            model="models/gemini-2.5-flash-preview-04-17", 
            contents=prompt,
            config=types.GenerateContentConfig(
                # max_output_tokens=500,
                system_instruction="You are the Most Humble man on Earth",
                temperature=0.1
            )
        )
        
        print(response.text)     
        return response.text
    
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }