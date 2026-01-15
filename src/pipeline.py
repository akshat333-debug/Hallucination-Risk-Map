from src.claim_extraction import extract_claims
from src.retriever import LocalRetriever
from src.nli_verifier import NLIVerifier
from src.aggregator import aggregate_scores

class RiskAnalysisPipeline:
    def __init__(self):
        print("Initializing Strong Local Pipeline...")
        self.retriever = LocalRetriever()
        
        # This now loads the DeBERTa model (The "Logician")
        self.verifier = NLIVerifier() 
        print("✅ Heavy Local Model Ready.")

    def process(self, question: str, answer: str, api_key: str = None):
        # 1. Extract Claims (We still use LLM splitter if available, else Spacy)
        claims = extract_claims(answer, api_key=api_key)
        
        final_results = []
        green_sentences = []

        for claim in claims:
            # 2. Retrieve Evidence
            # Search for the claim text specifically
            evidences = self.retriever.retrieve(claim.text, k=3)
            
            # 3. Local Verification (DeBERTa)
            nli_scores = self.verifier.verify(claim.text, evidences)
            
            # Tag claim text for the Entity Auditor in aggregator
            for score in nli_scores:
                score['claim_text'] = claim.text

            # 4. Math Aggregation (Logic + Entities + Vectors)
            agg = aggregate_scores(evidences, nli_scores)
            
            # Build Result Object
            result_obj = {
                "claim_text": claim.text,
                "evidence": [],
                "analysis": agg
            }
            
            for ev, score in zip(evidences, nli_scores):
                result_obj["evidence"].append({
                    "text": ev["text"],
                    "source": ev["source"],
                    "similarity": ev["similarity"],
                    "nli": score
                })
            
            final_results.append(result_obj)
            
            if agg["color"] == "green":
                green_sentences.append(claim.text)

        return {
            "claims": final_results,
            "safest_answer": " ".join(green_sentences),
            "stats": {
                "total_claims": len(claims),
                "green_count": len(green_sentences)
            }
        }