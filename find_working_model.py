import google.generativeai as genai
import time

# --- PASTE YOUR KEY HERE ---
api_key = "AIzaSyDuyLGQu_buMEoQqRyyuXXWp9IlNDeHIl8"
genai.configure(api_key=api_key)

# The full list derived from your previous logs
candidates = [
    'gemini-2.0-flash-lite-preview-02-05',
    'gemini-2.0-flash-lite-001',
    'gemini-exp-1206',
    'gemini-2.0-flash-exp',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash',
    'gemini-2.0-flash-001',
    'gemini-flash-latest',
    'gemini-flash-lite-latest',
    'gemini-pro-latest',
    'models/gemini-1.5-flash-8b', # Sometimes 8b has separate quota
    'gemini-1.5-flash-latest'
]

print(f"🔎 Testing {len(candidates)} models for a working quota...\n")

working_model = None

for model_name in candidates:
    print(f"Testing: {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        # Try a tiny prompt
        response = model.generate_content("Hi", request_options={'timeout': 10})
        print("✅ SUCCESS! Working.")
        working_model = model_name
        break # Found one!
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print("❌ Quota Exceeded.")
        elif "404" in str(e):
            print("❌ Not Found.")
        else:
            print(f"❌ Error: {str(e)[:50]}...")

print("-" * 30)
if working_model:
    print(f"🎉 WE FOUND A WORKING MODEL: {working_model}")
    print("Please update 'MODEL_NAME' in your code to this exact string.")
else:
    print("💀 All models are exhausted or blocked.")
    print("Solution: You MUST wait 24 hours or create a new Google Cloud Project.")