from transformers import pipeline
import torch
import os

# Global cache
local_pipe = None

def get_local_pipe():
    global local_pipe
    if local_pipe is None:
        print("⏳ Loading Local LLM (Flan-T5)...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Check for manual download first
        local_path = "local_models/flan-t5-base"
        model_id = local_path if os.path.exists(local_path) else "google/flan-t5-base"

        try:
            local_pipe = pipeline(
                "text2text-generation",
                model=model_id,
                device=-1 if device == "cpu" else 0,
                model_kwargs={"torch_dtype": torch.float32}
            )
            print("✅ Local LLM Ready.")
        except Exception as e:
            print(f"❌ Failed to load local model: {e}")
            return None
    return local_pipe

def local_generate_answer(question: str, context_chunks: list[dict]) -> str:
    """
    Generate an answer using ONLY local CPU/GPU resources.
    """
    pipe = get_local_pipe()
    if not pipe:
        return "Error: Local model failed to load."

    # Flan-T5 has a small context window (512 tokens). 
    # We take only the top 1 or 2 most relevant chunks to avoid crashing.
    top_context = " ".join([c['text'] for c in context_chunks[:2]])
    
    # Prompt Engineering for T5
    prompt = f"Answer based on context: {top_context} \n\nQuestion: {question}"

    try:
        # Generate with slightly more creativity
        output = pipe(prompt, max_length=256, do_sample=True, temperature=0.3)
        return output[0]['generated_text'] + " (Generated Locally)"
    except Exception as e:
        return f"Error generating local answer: {e}"

def local_rewrite(question: str, verified_facts: list[str]) -> str:
    """
    Rewrites bullet points into a paragraph locally.
    """
    pipe = get_local_pipe()
    if not pipe:
        return "\n".join(f"- {f}" for f in verified_facts)

    facts_text = ". ".join(verified_facts)
    prompt = f"Summarize facts into answer: {facts_text} \n\nQuestion: {question}"

    try:
        output = pipe(prompt, max_length=256, do_sample=False)
        return output[0]['generated_text'] + " (Generated Locally)"
    except Exception as e:
        return f"Error rewriting: {e}"