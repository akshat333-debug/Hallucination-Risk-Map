"""
Benchmark: High Accuracy Ensemble v5 (200 Claims).
"""
from sample_data.benchmark_200 import BENCHMARK_200
import high_accuracy_ensemble
import time

print("🚀 Starting Massive Benchmark: 200 Claims")
print(f"📦 Dataset Size: {len(BENCHMARK_200)} claims\n")

start_time = time.time()
results = []

for i, item in enumerate(BENCHMARK_200):
    if i % 20 == 0: print(f"  Processed {i}/{len(BENCHMARK_200)}...")
    try:
        res = high_accuracy_ensemble.verify_claim(item["claim"], [item["evidence"]])
        results.append(res["verdict"])
    except Exception as e:
        print(f"Error: {e}")
        results.append("ERR")

end_time = time.time()
duration = end_time - start_time

# Print results table
print("\n" + "=" * 80)
print(f"{'Claim':<50} | {'Exp':<8} | {'Verdict':<10} | Match?")
print("=" * 80)

correct = 0
for i, item in enumerate(BENCHMARK_200):
    exp = item["expected"][:8]
    got = results[i][:10] if len(results[i]) > 10 else results[i]
    match = "✅" if got.startswith(exp[:4]) else "❌"
    if got.startswith(exp[:4]): correct += 1
    
    # Highlight failures
    if not got.startswith(exp[:4]):
        match = "🔴 FAIL"
        # Print extra debug info for failures
        # print(f"   [FAIL] Claim: {item['claim']}")
        # print(f"   [FAIL] Evidence: {item['evidence']}")
        # print(f"   [FAIL] Expected: {item['expected']} Got: {results[i]}")
    
    print(f"{item['claim'][:50]:<50} | {exp:<8} | {got:<10} | {match}")

print("-" * 80)
print(f"Final Accuracy: {correct}/{len(BENCHMARK_200)} ({100*correct/len(BENCHMARK_200):.1f}%)")
print(f"Total Time: {duration:.2f}s (Avg: {duration/len(BENCHMARK_200):.2f}s/claim)")
print("-" * 80)
