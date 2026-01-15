import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import re

class LocalRetriever:
    def __init__(self):
        # Load all components
        if not os.path.exists("vector_index.faiss"):
            raise FileNotFoundError("Index missing. Please build index first.")
            
        self.index = faiss.read_index("vector_index.faiss")
        
        with open("corpus_metadata.pkl", 'rb') as f:
            self.metadata = pickle.load(f)
            
        with open("bm25_index.pkl", 'rb') as f:
            self.bm25 = pickle.load(f)
            
        # Use the stronger model matching index_builder
        self.model = SentenceTransformer('all-mpnet-base-v2') 

    def simple_tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def retrieve(self, query: str, k: int = 3):
        # 1. Vector Search (Semantic)
        query_vec = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vec)
        v_scores, v_indices = self.index.search(query_vec, k * 2) # Get more candidates
        
        # 2. BM25 Search (Keyword)
        tokenized_query = self.simple_tokenize(query)
        # Get top N BM25 scores
        bm25_scores = self.bm25.get_scores(tokenized_query)
        # Get indices of top k*2
        bm25_indices = np.argsort(bm25_scores)[::-1][:k*2]
        
        # 3. Hybrid Fusion (Reciprocal Rank Fusion - RRF)
        # We combine the two lists. If a doc appears in both, it shoots to the top.
        combined_scores = {}
        
        # Helper to add scores
        def add_rank(indices, weight=1.0):
            for rank, idx in enumerate(indices):
                if idx == -1: continue
                if idx not in combined_scores: combined_scores[idx] = 0.0
                # RRF Formula: 1 / (k + rank)
                combined_scores[idx] += (1.0 / (60 + rank)) * weight

        add_rank(v_indices[0], weight=1.0) # Vector weight
        add_rank(bm25_indices, weight=1.5) # Boost Keyword weight slightly (trust exact matches more)
        
        # Sort by combined score
        sorted_indices = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        results = []
        for idx, score in sorted_indices:
            doc = self.metadata[idx]
            # We calculate a 'pseudo-similarity' for display purposes based on vector score
            # (Just finding the original vector score for UI consistency)
            orig_sim = 0.0
            if idx in v_indices[0]:
                pos = np.where(v_indices[0] == idx)[0][0]
                orig_sim = float(v_scores[0][pos])
            else:
                orig_sim = 0.5 # Default for BM25-only matches
                
            results.append({
                "text": doc["text"],
                "source": doc.get("source", "Unknown"),
                "similarity": orig_sim
            })
            
        return results