
import sys
import os
import torch
from sentence_transformers import CrossEncoder
from tqdm import tqdm
from src.nli_verifier import NLIVerifier

# Ensure we can import local modules
sys.path.append(os.getcwd())
from sample_data.benchmark_300 import BENCHMARK_300

def evaluate_model(model_key, dataset):
    print(f"\n⚖️  Testing Strategy: {model_key.upper()}...")
    
    # We must use NLIVerifier to get the 'auto' logic
    verifier = NLIVerifier()
    
    # Pre-load correct model (or mock base for auto)
    target_model = 'base' if model_key == 'auto' else ('cross-encoder/nli-deberta-v3-base' if model_key == 'base' else 'cross-encoder/nli-deberta-v3-large')
    real_key = 'base' if model_key == 'base' else ('large' if model_key == 'large' else 'base')
    
    try:
        verifier.load_model(real_key)  
    except Exception as e:
        print(f"Skipping {model_key} due to load error (maybe model removed?): {e}")
        return 0.0, []

    label_map = {0: 'CONTRADICTED', 1: 'ENTAILED', 2: 'NEUTRAL'}
    correct = 0
    results = []
    
    print(f"📊 Running inference on {len(dataset)} items...")
    
    for i, item in enumerate(tqdm(dataset)):
        ev_objs = [{"text": item['evidence'], "source": "bench", "similarity": 1.0}]
        
        # Run Verification
        try:
            nli_res = verifier.verify(item['claim'], ev_objs, model_selection=model_key)
            if not nli_res:
                predicted_label = "NEUTRAL" # Default fallback
            else:
                res = nli_res[0]
                predicted_label = res['label'].upper() 
                if predicted_label == 'ENTAILMENT': predicted_label = 'ENTAILED'
                if predicted_label == 'CONTRADICTION': predicted_label = 'CONTRADICTED'
        except Exception as e:
            # Fallback for removed large model or errors
            predicted_label = "ERROR"

        expected_label = item['expected']
        
        is_correct = (predicted_label == expected_label)
        if is_correct:
            correct += 1
            
        results.append({
            "id": i,
            "claim": item['claim'],
            "evidence": item['evidence'],
            "expected": expected_label,
            "predicted": predicted_label,
            "is_correct": is_correct
        })
        
    accuracy = (correct / len(dataset)) * 100
    return accuracy, results

def main():
    print("🚀 Starting Model Comparison on BENCHMARK 300 (Messy)\n")
    
    # Run evaluation
    base_acc, base_results = evaluate_model("base", BENCHMARK_300)
    # We removed Large, so we skip it or expectation is it fails/skips gracefully
    
    auto_acc, auto_results = evaluate_model("auto", BENCHMARK_300)
    
    print("\n" + "="*60)
    print("🏆 FINAL RESULTS (300 Mixed Items)")
    print("="*60)
    print(f"🔹 Base Model Accuracy:  {base_acc:.2f}%")
    print(f"✨ Auto Model Accuracy:  {auto_acc:.2f}%")
    print("="*60)
    
    print("\n🔍 Interesting Fixes in Auto Mode:")
    for b_res, a_res in zip(base_results, auto_results):
        if not b_res['is_correct'] and a_res['is_correct']:
             print(f"[Item #{b_res['id']+1}] FIXED: {b_res['claim'][:50]}... vs {b_res['evidence'][:50]}...")
             print(f"   Base: {b_res['predicted']} -> Auto: {a_res['predicted']} (Expected: {b_res['expected']})")

    print("\n⚠️ Regressions (Auto broke these):")
    for b_res, a_res in zip(base_results, auto_results):
        if b_res['is_correct'] and not a_res['is_correct']:
             print(f"[Item #{b_res['id']+1}] BROKE: {b_res['claim'][:50]}... vs {b_res['evidence'][:50]}...")
             print(f"   Base: {b_res['predicted']} -> Auto: {a_res['predicted']} (Expected: {b_res['expected']})")

if __name__ == "__main__":
    main()
