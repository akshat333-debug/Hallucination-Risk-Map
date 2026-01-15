import json
import os
import sys

sys.path.append(os.getcwd())

from src.index_builder import build_index_from_documents

def rebuild():
    print("Loading corpus_data.json...")
    if not os.path.exists("corpus_data.json"):
        print("Error: corpus_data.json not found!")
        return

    with open("corpus_data.json", "r") as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} documents.")
    build_index_from_documents(data)
    print("Index rebuilt successfully.")

if __name__ == "__main__":
    rebuild()
