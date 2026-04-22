from openrouter import OpenRouter
import os

try:
    with OpenRouter(api_key="test") as client:
        print("Methods in client.chat:", dir(client.chat))
except Exception as e:
    print("Error:", e)
