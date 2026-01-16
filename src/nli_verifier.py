from sentence_transformers import CrossEncoder
import torch

class NLIVerifier:
    def __init__(self):
        # Default to None, lazy load
        self.model = None
        self.current_model_name = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # DeBERTa labels: 0=Contradiction, 1=Entailment, 2=Neutral
        self.label_map = {0: 'contradiction', 1: 'entailment', 2: 'neutral'}

    def load_model(self, model_key):
        """
        Loads the specified model if not already loaded.
        model_key: 'base' or 'auto' (uses base)
        """
        target_name = 'cross-encoder/nli-deberta-v3-base'
        
        if self.current_model_name != target_name:
            print(f"⚖️ Loading NLI Model: {target_name} on {self.device}...")
            # If switching, simple reassignment lets Python GC the old one eventually
            self.model = CrossEncoder(target_name, device=self.device)
            self.current_model_name = target_name

    def verify(self, claim: str, evidence_list: list, model_selection="base"):
        """
        Runs NLI with the selected model. 
        If model_selection='auto', runs Base + Symbolic Logic.
        """
        # Ensure model is ready (Default to base for auto)
        actual_model = 'base' if model_selection == 'auto' else model_selection
        self.load_model(actual_model)
        
        if not evidence_list:
            return []
        
        # Create pairs: (Evidence, Claim) - Standard NLI format
        pairs = [[ev['text'], claim] for ev in evidence_list]
        
        # Predict scores
        scores = self.model.predict(pairs, apply_softmax=True)
        
        results = []
        for i, score_dist in enumerate(scores):
            label_idx = score_dist.argmax()
            
            # --- SYMBOLIC LOGIC OVERRIDE (AUTO MODE) ---
            if model_selection == 'auto':
                from src.symbolic_verifier import SymbolicVerifier
                if not hasattr(self, 'sym_verifier'):
                    self.sym_verifier = SymbolicVerifier() # Lazy Init
                
                # Check for Hard Logic
                evidence_text = evidence_list[i]['text']
                
                # Check Contradiction (Strongest signal)
                contra = self.sym_verifier.check_contradiction(claim, evidence_text)
                if contra == 'CONTRADICTED':
                    # Force Contradiction stats
                    score_dist = [0.99, 0.0, 0.0] 
                    label_idx = 0
                else:
                    # Check Entailment (Unit conversions, etc)
                    entail = self.sym_verifier.check_entailment(claim, evidence_text)
                    if entail == 'ENTAILED':
                        # Force Entailment stats
                        score_dist = [0.0, 0.99, 0.0]
                        label_idx = 1
            
            results.append({
                "p_contradiction": float(score_dist[0]),
                "p_entailment": float(score_dist[1]),
                "p_neutral": float(score_dist[2]),
                "label": self.label_map[label_idx]
            })
            
        return results