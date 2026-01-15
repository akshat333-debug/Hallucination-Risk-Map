import google.generativeai as genai
import time
from src.model_config import MODEL_ROSTER
from src.local_generator import local_generate_answer, local_rewrite

def generate_with_fallback(prompt_func):
    """
    Tries all API models. If all fail, raises Exception.
    """
    for model_name in MODEL_ROSTER:
        try:
            model = genai.GenerativeModel(model_name)
            return prompt_func(model)
        except Exception as e:
            # Check for quota errors vs other errors
            if "429" in str(e) or "quota" in str(e).lower():
                continue # Try next model
            time.sleep(1) # Brief pause for network glitches
            
    raise Exception("All API models exhausted")

def generate_answer(question: str, context_chunks: list[dict], api_key: str = None, force_local: bool = False) -> str:
    """
    Generates answer. 
    Priority: 
    1. Local (if forced)
    2. API (if available)
    3. Local Fallback (if API fails)
    """
    # 1. Force Local Mode
    if force_local:
        print("🏠 Force Local Mode active.")
        return local_generate_answer(question, context_chunks)

    # 2. Try API
    if api_key:
        genai.configure(api_key=api_key)
        ctx = "\n\n".join([c['text'] for c in context_chunks])
        prompt = f"Context:\n{ctx}\n\nQuestion:\n{question}\n\nAnswer:"
        
        def _do(model): return model.generate_content(prompt).text
        
        try:
            return generate_with_fallback(_do)
        except Exception as e:
            print(f"⚠️ API Failed ({e}). Switching to Local...")

    # 3. Local Fallback
    return local_generate_answer(question, context_chunks)

def rewrite_verified_answer(question: str, verified_facts: list[str], api_key: str = None) -> str:
    # Try API
    if api_key:
        genai.configure(api_key=api_key)
        facts = "\n- ".join(verified_facts)
        prompt = f"Using ONLY these facts:\n{facts}\n\nAnswer this: {question}"
        def _do(model): return model.generate_content(prompt).text
        
        try:
            return generate_with_fallback(_do)
        except:
            pass # Fallthrough to local

    # Local Fallback
    return local_rewrite(question, verified_facts)