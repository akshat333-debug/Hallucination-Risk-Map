import google.generativeai as genai
import os

# Paste your key here or ensure it's in environment
api_key = "AIzaSyDuyLGQu_buMEoQqRyyuXXWp9IlNDeHIl8" 
genai.configure(api_key=api_key)

print("Searching for 1.5 models...")
for m in genai.list_models():
    if "1.5" in m.name and "flash" in m.name:
        print(f"✅ FOUND: {m.name}")
