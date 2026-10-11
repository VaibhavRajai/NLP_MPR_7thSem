import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.nlp.embeddings import SemanticEncoder
from backend.app.core.logging import logger

class EvidenceRetriever:
    def __init__(self):
        self.encoder = SemanticEncoder()

    def rank_sentences_by_query(
        self, 
        sentences: List[Dict[str, Any]], 
        query: str, 
        top_k: int = 15
    ) -> List[Dict[str, Any]]:
        if not sentences or not query.strip():
            return sentences[:top_k]

        texts = [s["text"] for s in sentences]
        all_texts = [query] + texts
        
        vectors = self.encoder.encode_sentences(all_texts)
        query_vec = vectors[0].reshape(1, -1)
        doc_vecs = vectors[1:]

        sims = cosine_similarity(query_vec, doc_vecs)[0]

        scored_sentences = []
        for idx, s in enumerate(sentences):
            item = dict(s)
            item["query_similarity"] = float(sims[idx])
            scored_sentences.append(item)

        scored_sentences.sort(key=lambda x: x["query_similarity"], reverse=True)
        return scored_sentences[:top_k]

    @staticmethod
    def chunk_document_by_sections(sentences: List[Dict[str, Any]], max_chunk_sentences: int = 5) -> List[Dict[str, Any]]:
        chunks = []
        current_chunk_sents = []
        current_section = None
        current_page = 1

        for s in sentences:
            if current_section is None:
                current_section = s["section"]
                current_page = s["page"]

            # Break chunk on section change or maximum sentence count
            if s["section"] != current_section or len(current_chunk_sents) >= max_chunk_sentences:
                if current_chunk_sents:
                    chunk_text = " ".join([sent["text"] for sent in current_chunk_sents])
                    chunks.append({
                        "chunk_id": f"chunk_{len(chunks)+1}",
                        "section": current_section,
                        "page": current_page,
                        "text": chunk_text,
                        "sentence_ids": [sent["id"] for sent in current_chunk_sents],
                        "sentence_count": len(current_chunk_sents)
                    })
                current_chunk_sents = [s]
                current_section = s["section"]
                current_page = s["page"]
            else:
                current_chunk_sents.append(s)

        if current_chunk_sents:
            chunk_text = " ".join([sent["text"] for sent in current_chunk_sents])
            chunks.append({
                "chunk_id": f"chunk_{len(chunks)+1}",
                "section": current_section,
                "page": current_page,
                "text": chunk_text,
                "sentence_ids": [sent["id"] for sent in current_chunk_sents],
                "sentence_count": len(current_chunk_sents)
            })

        return chunks
