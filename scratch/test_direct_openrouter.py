from openrouter import OpenRouter
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")
print(f"Key starts with: {key[:10]}...")

try:
    with OpenRouter(api_key=key) as client:
        response = client.chat.send(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[
                {
                    "role": "user",
                    "content": "What is the meaning of life?"
                }
            ]
        )
        print("Response:", response.choices[0].message.content)
except Exception as e:
    print("Error type:", type(e))
    print("Error message:", e)
    if hasattr(e, "response"):
        print("Response status:", e.response.status_code)
        print("Response body:", e.response.text)
