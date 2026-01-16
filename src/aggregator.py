import re

def calculate_overlap(claim_text, evidence_text):
    stopwords = {"the", "is", "at", "which", "on", "and", "a", "an", "of", "in", "to", "for", "with", "it", "this", "that", "from", "by", "as", "be", "are"}
    def clean(text): return set(re.findall(r'\b\w+\b', text.lower())) - stopwords
    
    c_words = clean(claim_text)
    e_words = clean(evidence_text)
    
    if not c_words: return 0.0
    return len(c_words.intersection(e_words)) / len(c_words)

def aggregate_scores(retrieval_results, nli_results, thresholds=None):
    if not thresholds:
        thresholds = {"sim_threshold": 0.6, "entail_threshold": 0.6}
        
    sim_thresh = thresholds.get("sim_threshold", 0.6)
    entail_thresh = thresholds.get("entail_threshold", 0.7)

    if not retrieval_results:
        return {"risk_label": "No Evidence", "score": 0.0, "color": "red"}

    best_score = 0.0
    final_analysis = None
    
    for res, nli in zip(retrieval_results, nli_results):
        
        sim_score = max(0, res['similarity'])
        entail_score = nli['p_entailment']
        contra_score = nli['p_contradiction']
        neutral_score = nli['p_neutral']
        
        claim_fn = nli.get('claim_text', '')
        overlap = calculate_overlap(claim_fn, res['text'])
        
        # --- ROBUST LOGIC v2 (Adaptive) ---
        
        # 1. The "Undeniable Truth" (Super High NLI)
        # If the model is > 85% sure, we trust it even if wording is different (e.g. 1 year vs 12 months)
        if entail_score > 0.85:
            trust_score = 0.95
            
        # 2. The "Corroborated Truth" (Moderate NLI + Keyword Overlap)
        # If model is > 60% sure AND keywords match significantly (e.g. 50%), trust it.
        # This filters out "Alloy" vs "Aluminum" (low overlap) if NLI is only 75%.
        elif entail_score > 0.60 and overlap > 0.5:
             trust_score = 0.90
             
        # 3. The "Contradiction"
        elif contra_score > 0.5:
            trust_score = 0.1


        # 3. The "Mixed Signals"
        # Neutral NLI but decent keyword overlap
        elif neutral_score > 0.4 and overlap > 0.5:
            trust_score = 0.80 
            
        # 4. The "Semantic Match"
        # NLI says Neutral, but Similarity is strong (User Configured)
        elif neutral_score > 0.4 and sim_score > sim_thresh:
            trust_score = 0.75
            
        # 5. The "Hard Contradiction"
        elif contra_score > 0.5:
            trust_score = 0.1
            
        # 6. Fallback
        else:
            trust_score = 0.35

        # Keep best
        if trust_score > best_score:
            best_score = trust_score
            
            # Labeling
            if trust_score >= 0.8:
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