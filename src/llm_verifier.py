import google.generativeai as genai
import json
import time
from src.model_config import MODEL_ROSTER

class LLMVerifier:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if api_key: genai.configure(api_key=api_key)

    def verify_batch(self, batch_data: list) -> list:
        if not self.api_key: return None 

        final_results_map = {}
        chunk_size = 5
        chunks = [batch_data[i:i + chunk_size] for i in range(0, len(batch_data), chunk_size)]
        
        for chunk_index, chunk in enumerate(chunks):
            # Prepare Prompt
            prompt_items = [f"ID: {it['id']} | CLAIM: {it['claim']} | CONTEXT: {it['context']}" for it in chunk]
            full_prompt = f"""
            Verify claims. Return JSON list: [{{ "id": <int>, "label": "entailment"|"contradiction"|"neutral", "confidence": <float>, "reason": "str" }}]
            ITEMS:\n{chr(10).join(prompt_items)}
            """

            chunk_success = False
            for model_name in MODEL_ROSTER:
                if chunk_success: break
                try:
                    model = genai.GenerativeModel(model_name)
                    res = model.generate_content(full_prompt)
                    clean = res.text.replace("```json", "").replace("```", "").strip()
                    if "[" in clean: clean = clean[clean.find("["):clean.rfind("]")+1]
                    
                    for r in json.loads(clean):
                        final_results_map[r['id']] = {
                            "p_entailment": r.get('confidence', 0) if r.get('label')=='entailment' else 0,
                            "p_contradiction": r.get('confidence', 0) if r.get('label')=='contradiction' else 0,
                            "p_neutral": r.get('confidence', 0) if r.get('label')=='neutral' else 1,
                            "reason": r.get("reason", f"Verified by {model_name}")
                        }
                    chunk_success = True
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        continue # Try next model
            
            if not chunk_success:
                print("❌ Batch failed on all models. Using Local Fallback.")
                return None
            time.sleep(1)

        ordered = []
        for item in batch_data:
            if item['id'] in final_results_map: ordered.append(final_results_map[item['id']])
            else: return None
        return ordered