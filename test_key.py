import google.generativeai as genai
import os
import time

# --- PASTE YOUR NEW KEY DIRECTLY HERE ---
NEW_KEY = "AIzaSyDuyLGQu_buMEoQqRyyuXXWp9IlNDeHIl8"

genai.configure(api_key=NEW_KEY)

models_to_test = [
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-pro'
]

print(f"Testing Key: {NEW_KEY[:5]}...{NEW_KEY[-5:]}")

for model in models_to_test:
    print(f"\nTesting model: {model}...")
    try:
        m = genai.GenerativeModel(model)
        response = m.generate_content("Reply with 'OK' if you can hear me.")
        print(f"✅ SUCCESS! {model} is working.")
        print(f"Response: {response.text.strip()}")
        break # We found a working one!
    except Exception as e:
        print(f"❌ FAILED: {model}")
        print(f"Error: {e}")