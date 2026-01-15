import spacy
from dataclasses import dataclass
import google.generativeai as genai
import json
from src.model_config import MODEL_ROSTER

nlp = None

@dataclass
class Claim:
    id: int
    text: str

def get_spacy_model():
    global nlp
    if nlp is None:
        try: nlp = spacy.load("en_core_web_sm")
        except: 
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
    return nlp

def split_with_llm(text: str, api_key: str) -> list[str]:
    genai.configure(api_key=api_key)
    prompt = f"Break text into atomic facts. Return JSON list of strings.\nTEXT: {text}"
    
    for model_name in MODEL_ROSTER:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            clean = res.text.replace("```json", "").replace("```", "").strip()
            if "[" in clean: clean = clean[clean.find("["):clean.rfind("]")+1]
            return json.loads(clean)
        except: continue
    return []

def extract_claims(text: str, api_key: str = None) -> list[Claim]:
    claims = split_with_llm(text, api_key) if api_key else []
    if not claims:
        doc = get_spacy_model()(text)
        claims = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 10]
    return [Claim(i, t) for i, t in enumerate(claims)]