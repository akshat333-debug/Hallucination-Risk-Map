import google.generativeai as genai

api_key = input("AIzaSyDuyLGQu_buMEoQqRyyuXXWp9IlNDeHIl8").strip()
genai.configure(api_key=api_key)

print("\nSearching for available models...")
try:
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ FOUND: {m.name}")
            found_any = True
    
    if not found_any:
        print("❌ No models found. Check if 'Generative Language API' is enabled in your Google Console.")
except Exception as e:
    print(f"Error: {e}")