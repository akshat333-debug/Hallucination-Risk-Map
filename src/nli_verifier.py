from sentence_transformers import CrossEncoder
import torch

class NLIVerifier:
    def __init__(self):
        # UPGRADE: Using DeBERTa v3 (The best open-source NLI model currently)
        # It understands "not", "except", and paraphrasing much better than RoBERTa.
        model_name = 'cross-encoder/nli-deberta-v3-base'
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"⚖️ Loading Heavy Local Model: {model_name} on {device}...")
        self.model = CrossEncoder(model_name, device=device)
        
        # DeBERTa labels: 0=Contradiction, 1=Entailment, 2=Neutral
        self.label_map = {0: 'contradiction', 1: 'entailment', 2: 'neutral'}

    def verify(self, claim: str, evidence_list: list):
        if not evidence_list:
            return []
        
        # Create pairs: (Evidence, Claim) - Standard NLI format
        # Premise = Evidence, Hypothesis = Claim
        pairs = [[ev['text'], claim] for ev in evidence_list]
        
        # Predict scores (Apply Softmax to get probabilities 0.0 - 1.0)
        scores = self.model.predict(pairs, apply_softmax=True)
        
        results = []
        for i, score_dist in enumerate(scores):
            # DeBERTa Output: [Contradiction, Entailment, Neutral]
            results.append({
                "p_contradiction": float(score_dist[0]),
                "p_entailment": float(score_dist[1]),
                "p_neutral": float(score_dist[2]),
                # Label is the index of the highest score
                "label": self.label_map[score_dist.argmax()]
            })
            
        return results