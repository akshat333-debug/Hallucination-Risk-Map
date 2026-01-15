import json
import os
import sys

# Ensure src can be imported
sys.path.append(os.getcwd())

from src.pipeline import RiskAnalysisPipeline

def run_accuracy_check():
    print("Loading evaluation set...")
    with open("evaluation_set.json", "r") as f:
        eval_data = json.load(f)

    print("Initializing Pipeline...")
    pipeline = RiskAnalysisPipeline()

    correct_predictions = 0
    total_samples = len(eval_data)
    
    results_log = []

    print("\nStarting Evaluation...\n")
    print(f"{'Question':<30} | {'Expected':<10} | {'Predicted':<10} | {'Result'}")
    print("-" * 70)

    for case in eval_data:
        question = case["question"]
        answer = case["answer"]
        expected = case["expected_risk"]

        # Run pipeline
        # We pass the answer as the "generated_answer" to be verified
        # The pipeline returns detailed analysis
        result = pipeline.process(question, answer)
        
        # Determine overall risk of the answer
        # If ANY claim is red/orange, we consider the whole answer "Risky" (red) for this binary check
        # If ALL claims are green, it's "Safe" (green)
        
        claims = result["claims"]
        if not claims:
            # No claims found? If expected was green (safe), this is ambiguous. 
            # But usually empty means no factual claim to verify.
            # Let's assume 'green' if no risk detected, but print warning.
            predicted = "green" 
        else:
            # Simple heuristic: If any claim is NOT green, the whole statment has hallucinations
            predicted = "green"
            for c in claims:
                if c['analysis']['color'] != 'green':
                    predicted = "red"
                    break
        
        is_correct = (predicted == expected)
        if is_correct:
            correct_predictions += 1
            status = "✅"
            print(f"{question[:30]:<30} | {expected:<10} | {predicted:<10} | {status}")
        else:
            status = "❌"
            print(f"{question[:30]:<30} | {expected:<10} | {predicted:<10} | {status}")
            print(f"   [DEBUG] Answer: {answer}")
            for c in claims:
                print(f"   [CLAIM] {c['claim_text']} -> {c['analysis']['color']}")
                for ev in c['evidence']:
                    print(f"      [EVIDENCE] ({ev['similarity']:.2f}) {ev['text'][:100]}...")
                    print(f"      [NLI] {ev['nli']}")

        
        results_log.append({
            "question": question,
            "expected": expected,
            "predicted": predicted,
            "is_correct": is_correct
        })

    accuracy = (correct_predictions / total_samples) * 100
    print("-" * 70)
    print(f"\nTotal Samples: {total_samples}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    run_accuracy_check()
