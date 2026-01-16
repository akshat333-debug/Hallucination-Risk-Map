from src.symbolic_verifier import SymbolicVerifier

def test_symbolic_logic():
    verifier = SymbolicVerifier()
    
    test_cases = [
        {
            "claim": "Cost is $99.99.",
            "evidence": "The price is one hundred dollars.",
            "expected": "CONTRADICTED" # Exact mismatch
        },
        {
            "claim": "Guest limit is 3 days.",
            "evidence": "Guests may stay no longer than 72 hours.",
            "expected": "ENTAILED" # Logic match
        },
        {
            "claim": "Profit was $10M.",
            "evidence": "Profit was $10M.",
            "expected": None # Base model handles this fine
        },
        {
             "claim": "Release date is 2024.",
             "evidence": "Release date is 2025.",
             "expected": "CONTRADICTED"
        }
    ]
    
    print("🚀 Testing Symbolic Verifier...\n")
    
    for i, case in enumerate(test_cases):
        print(f"Case {i+1}: '{case['claim']}' vs '{case['evidence']}'")
        
        # Check Contradiction
        contra = verifier.check_contradiction(case['claim'], case['evidence'])
        entail = verifier.check_entailment(case['claim'], case['evidence'])
        
        result = contra if contra else (entail if entail else "NEUTRAL/PASS")
        
        status = "✅" if result == case['expected'] or (case['expected'] is None and result == "NEUTRAL/PASS") else "❌"
        print(f"   -> Result: {result} | Expected: {case['expected']} {status}\n")

if __name__ == "__main__":
    test_symbolic_logic()
