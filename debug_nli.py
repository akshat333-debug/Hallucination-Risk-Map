from sentence_transformers import CrossEncoder

def check_nli():
    model_name = 'cross-encoder/nli-deberta-v3-base'
    print(f"Loading {model_name}...")
    model = CrossEncoder(model_name)
    
    pairs = [
        ("A man is eating rice.", "A man is eating."), # Entailment
        ("A man is eating rice.", "A man is sleeping."), # Contradiction
        ("A man is eating rice.", "The weather is nice today."), # Neutral (irrelevant)
    ]
    
    scores = model.predict(pairs, apply_softmax=True)
    
    print("\nResults (indices [0, 1, 2]):")
    for pair, score in zip(pairs, scores):
        print(f"P: {pair[0]}")
        print(f"H: {pair[1]}")
        print(f"Scores: {score}")
        print("-" * 30)

if __name__ == "__main__":
    check_nli()
