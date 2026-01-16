from huggingface_hub import snapshot_download
import os

model_name = "cross-encoder/nli-deberta-v3-base"
print(f"🚀 Starting Download: {model_name}")

try:
    path = snapshot_download(
        repo_id=model_name, 
        resume_download=True,
        tqdm_class=None
    )
    print(f"\n✅ Download Complete! Saved to: {path}")
except Exception as e:
    print(f"\n❌ Download Failed: {e}")
