import re

def calculate_overlap(claim_text, evidence_text):
    stopwords = {"the", "is", "at", "which", "on", "and", "a", "an", "of", "in", "to", "for", "with", "it", "this", "that", "from", "by", "as", "be", "are"}
    def clean(text): return set(re.findall(r'\b\w+\b', text.lower())) - stopwords
    
    c_words = clean(claim_text)
    e_words = clean(evidence_text)
    
    if not c_words: return 0.0
    return len(c_words.intersection(e_words)) / len(c_words)

def aggregate_scores(retrieval_results, nli_results):
    if not retrieval_results:
        return {"risk_label": "No Evidence", "score": 0.0, "color": "red"}

    best_score = 0.0
    final_analysis = None
    
    for res, nli in zip(retrieval_results, nli_results):
        
        sim_score = max(0, res['similarity'])
        entail_score = nli['p_entailment']
        contra_score = nli['p_contradiction']
        neutral_score = nli['p_neutral']
        
        overlap = calculate_overlap(nli.get('claim_text', ''), res['text'])
        
        # --- ROBUST LOGIC ---
        
        # 1. The "Perfect Match"
        # High Entailment + Good Similarity
        if entail_score > 0.8:
            trust_score = 0.95
        
        # 2. The "Keyword Rescue"
        # NLI is confused (Neutral), but words match perfectly (Dates/Names)
        elif neutral_score > 0.6 and overlap > 0.6:
            trust_score = 0.85 # Trust the keywords
            
        # 3. The "Semantic Match"
        # NLI says Neutral, but Similarity is extremely high (Paraphrased perfectly)
        elif neutral_score > 0.5 and sim_score > 0.7:
            trust_score = 0.75
            
        # 4. The "Hard Contradiction"
        elif contra_score > 0.5:
            trust_score = 0.1
            
        # 5. The "Vague/Weak"
        else:
            trust_score = 0.4
            
        # Keep best
        if trust_score > best_score:
            best_score = trust_score
            
            # Labeling
            if trust_score > 0.8:
                label = "Verified"
                color = "green"
            elif trust_score > 0.6:
                label = "Likely True"
                color = "green" # Lenient Green
            elif trust_score > 0.4:
                label = "Uncertain"
                color = "orange"
            else:
                label = "Contradicted/Hallucinated"
                color = "red"
                
            final_analysis = {
                "score": round(trust_score, 2),
                "risk_label": label,
                "color": color,
                "contradiction_strength": round(contra_score, 2),
                "entailment_strength": round(entail_score, 2)
            }
            
    if not final_analysis:
         # Fallback
         return {"risk_label": "No Match", "score": 0.0, "color": "red", "contradiction_strength":0, "entailment_strength":0}

    return final_analysis