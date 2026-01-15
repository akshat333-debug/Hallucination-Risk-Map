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
    # 1. Light Preprocessing: Remove bold/italic markers but keep structure
    clean_text = text.replace("**", "").replace("__", "")
    
    # 2. Use SpaCy for initial splitting
    doc = get_spacy_model()(clean_text)
    raw_sents = [s.text.strip() for s in doc.sents if s.text.strip()]
    
    merged_claims = []
    buffer = ""
    
    for sent in raw_sents:
        # Heuristic: If sentence is too short (< 20 chars) or ends with a colon (Header), 
        # it is likely a fragment/header -> Convert to context for next sentence OR append to previous.
        
        is_short = len(sent) < 20
        is_header = sent.endswith(":")
        is_bullet = sent.startswith("*") or sent.startswith("-")

        if is_short or is_header or is_bullet:
            if buffer:
                buffer += " " + sent
            else:
                buffer = sent
        else:
            if buffer:
                # Attach buffer to this sentence (Context + Claim)
                merged_claims.append(buffer + " " + sent)
                buffer = ""
            else:
                merged_claims.append(sent)
    
    # If anything left in buffer, append it to the last claim if possible
    if buffer and merged_claims:
        merged_claims[-1] += " " + buffer
    elif buffer:
        merged_claims.append(buffer)

    return [Claim(i, t) for i, t in enumerate(merged_claims)]