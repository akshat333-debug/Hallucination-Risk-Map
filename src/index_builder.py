import os
# --- CRITICAL FIX FOR MACOS SEGFAULT ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# ---------------------------------------

import json
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from rank_bm25 import BM25Okapi # New keyword searcher
import re

# Constants
INDEX_FILE = "vector_index.faiss"
METADATA_FILE = "corpus_metadata.pkl"
BM25_FILE = "bm25_index.pkl"
# UPGRADE: Stronger embedding model (slower but much smarter)
MODEL_NAME = 'all-mpnet-base-v2' 

def simple_tokenize(text):
    # Simple tokenizer for BM25
    return re.findall(r'\b\w+\b', text.lower())

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text_chunks = []
    
    # Improved Chunking: Sliding Window (Overlap)
    # 500 chars with 100 char overlap ensures we don't cut sentences in half
    chunk_size = 500
    overlap = 100
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            text = text.replace('\n', ' ').strip()
            # Create sliding windows
            for start in range(0, len(text), chunk_size - overlap):
                end = start + chunk_size
                chunk = text[start:end]
                # Only keep chunks with actual content
                if len(chunk) > 50:
                    filename = os.path.basename(pdf_path).replace("temp_", "")
                    text_chunks.append({
                        "text": chunk,
                        "source": f"{filename} (Page {i+1})"
                    })
    return text_chunks

def build_index_from_documents(docs, model_name=MODEL_NAME):
    if not docs:
        print("No documents to index.")
        return

    print(f"Indexing {len(docs)} passages...")
    
    # 1. Build Vector Index (Semantic)
    model = SentenceTransformer(model_name)
    passages = [d['text'] for d in docs]
    embeddings = model.encode(passages, convert_to_numpy=True, show_progress_bar=True)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_FILE)
    
    # 2. Build BM25 Index (Keyword) - NEW
    tokenized_corpus = [simple_tokenize(doc) for doc in passages]
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Save Metadata & BM25
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(docs, f)
        
    with open(BM25_FILE, 'wb') as f:
        pickle.dump(bm25, f)
        
    print("Hybrid Indexing complete.")

def process_uploaded_file(uploaded_file):
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        data = []
        if temp_path.endswith(".pdf"):
            data = extract_text_from_pdf(temp_path)
        elif temp_path.endswith(".json"):
            with open(temp_path, "r") as f:
                data = json.load(f)
        else:
            with open(temp_path, "r") as f:
                text = f.read()
                data = [{"text": t, "source": "Text"} for t in text.split('\n\n') if t]

        # --- NEW LOGIC: APPEND TO INDEX ---
        existing_docs = []
        if os.path.exists(METADATA_FILE):
             try:
                 with open(METADATA_FILE, 'rb') as f:
                     existing_docs = pickle.load(f)
             except: pass
        
        # Check for duplicates (basic check by source filename)
        # If we re-upload the same file, we should probably remove old chunks of that file first
        # based on the source string starting with the filename.
        new_filename = uploaded_file.name
        
        # Filter out old chunks of this file if present (Update logic)
        existing_docs = [d for d in existing_docs if new_filename not in d['source']]
        
        # Combine
        combined_docs = existing_docs + data
        
        build_index_from_documents(combined_docs)
        return len(combined_docs)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def get_indexed_files():
    if not os.path.exists(METADATA_FILE):
        return []
    
    with open(METADATA_FILE, 'rb') as f:
        docs = pickle.load(f)
    
    # Extract unique sources
    sources = set()
    for d in docs:
        sources.add(d.get("source", "Unknown"))
        
    return sorted(list(sources))