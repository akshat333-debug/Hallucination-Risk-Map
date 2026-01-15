import spacy
from dataclasses import dataclass
import subprocess
import sys

# Global NLP model
nlp = None

@dataclass
class Claim:
    id: int
    text: str

def get_spacy_model():
    global nlp
    if nlp is None:
        try: 
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading SpaCy model...")
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
    return nlp

def extract_claims(text: str, api_key: str = None) -> list[Claim]:
    # API Key is ignored now, purely local splitting
    doc = get_spacy_model()(text)
    
    # Filter for meaningful sentences (len > 10 chars)
    claims = [s.text.strip() for s in doc.sents if len(s.text.strip()) > 10]
    
    return [Claim(i, t) for i, t in enumerate(claims)]