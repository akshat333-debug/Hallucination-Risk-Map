import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
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
            
        # Bi-Encoder for Initial Retrieval (Fast)
        self.model = SentenceTransformer('all-mpnet-base-v2') 
        
        # Cross-Encoder for Re-Ranking (Accurate)
        # MS MARCO MiniLM is fast and trained for relevance ranking
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def simple_tokenize(self, text):
        return re.findall(r'\b\w+\b', text.lower())

    def retrieve(self, query: str, k: int = 5):
        # --- STAGE 1: BROAD SEARCH (Retrieve 50 candidates) ---
        initial_k = 50 
        
        # 1. Vector Search
        query_vec = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vec)
        v_scores, v_indices = self.index.search(query_vec, initial_k)
        
        # 2. BM25 Search
        tokenized_query = self.simple_tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:initial_k]
        
        # 3. Hybrid Fusion (RRF)
        combined_scores = {}
        
        def add_rank(indices, weight=1.0):
            for rank, idx in enumerate(indices):
                if idx == -1: continue
                if idx not in combined_scores: combined_scores[idx] = 0.0
                combined_scores[idx] += (1.0 / (60 + rank)) * weight

        add_rank(v_indices[0], weight=1.0)
        add_rank(bm25_indices, weight=1.5)
        
        # Get top 50 candidates from Hybrid Fusion
        broad_candidates = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:initial_k]
        
        # --- STAGE 2: RE-RANKING (Cross-Encoder) ---
        if not broad_candidates: return []
        
        # Prepare pairs for Cross-Encoder: [ [Query, Doc1], [Query, Doc2], ... ]
        pairs = []
        candidate_indices = []
        
        for idx, _ in broad_candidates:
            doc_text = self.metadata[idx]["text"]
            pairs.append([query, doc_text])
            candidate_indices.append(idx)
            
        # Predict scores (Logits)
        ce_scores = self.reranker.predict(pairs)
        
        # Sort by Cross-Encoder score
        # Zip indices with their new CE scores
        reranked = sorted(zip(candidate_indices, ce_scores), key=lambda x: x[1], reverse=True)[:k]
        
        results = []
        for idx, score in reranked:
            doc = self.metadata[idx]
            
            # Normalize logit to 0-1 for UI consistency (Sigmoid)
            # This allows the Aggregator to still work with "sim_score > 0.6" logic
            normalized_score = 1 / (1 + np.exp(-score))
            
            results.append({
                "text": doc["text"],
                "source": doc.get("source", "Unknown"),
                "similarity": float(normalized_score) # High quality relevance score
            })
            
        return results