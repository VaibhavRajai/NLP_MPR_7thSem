import numpy as np
import networkx as nx
from typing import List, Dict, Any, Optional
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.nlp.embeddings import SemanticEncoder
from backend.app.core.logging import logger

# Section prior importance weights
SECTION_WEIGHTS = {
    "abstract": 1.4,
    "results": 1.5,
    "conclusion": 1.3,
    "methodology": 1.1,
    "discussion": 1.1,
    "limitations": 1.2,
    "objectives": 1.1,
    "introduction": 0.8,
    "title_metadata": 0.5,
    "other": 0.7
}

class TextRankSummarizer:
    def __init__(self):
        self.encoder = SemanticEncoder()

    def rank_sentences(
        self,
        sentences: List[Dict[str, Any]],
        instruction_bias_vector: Optional[np.ndarray] = None,
        damping: float = 0.85,
        max_iter: int = 100,
        query: Optional[str] = None,
        query_weight: float = 2.0
    ) -> List[Dict[str, Any]]:
        if not sentences:
            return []

        n = len(sentences)
        if n == 1:
            res = dict(sentences[0])
            res["textrank_score"] = 1.0
            return [res]

        texts = [s["text"] for s in sentences]
        sim_matrix = self.encoder.compute_similarity_matrix(texts)

        # Graph construction
        graph = nx.Graph()
        for i in range(n):
            graph.add_node(i)

        for i in range(n):
            for j in range(i + 1, n):
                weight = float(sim_matrix[i][j])
                # Filter out weak or noisy edges
                if weight > 0.15:
                    graph.add_edge(i, j, weight=weight)

        # Node personalization priors: combine section weight + entity density
        priors = {}
        for i, s in enumerate(sentences):
            sec_w = SECTION_WEIGHTS.get(s.get("section", "other"), 1.0)
            # Favor sentences with statistical values or biomedical terms
            stat_bonus = 1.3 if ("p <" in s["text"] or "%" in s["text"] or "CI" in s["text"]) else 1.0
            # Length penalty for very short or excessively long run-ons
            words = len(s["text"].split())
            length_factor = 1.0 if (12 <= words <= 45) else 0.8

            priors[i] = sec_w * stat_bonus * length_factor

        # Query conditioning: boost sentences semantically related to the user's query/topic
        query_sims = None
        if query and query.strip():
            try:
                vecs = self.encoder.encode_sentences([query] + texts)
                q_vec = vecs[0].reshape(1, -1)
                query_sims = np.clip(cosine_similarity(q_vec, vecs[1:])[0], 0.0, None)
                for i in range(n):
                    priors[i] *= (1.0 + query_weight * float(query_sims[i]))
            except Exception as e:
                logger.warning(f"Query-aware ranking skipped: {e}")

        # Normalize personalization vector
        total_prior = sum(priors.values())
        if total_prior > 0:
            for k in priors:
                priors[k] /= total_prior
        else:
            priors = None

        try:
            scores = nx.pagerank(graph, alpha=damping, personalization=priors, max_iter=max_iter, weight="weight")
        except Exception as e:
            logger.warning(f"PageRank iteration note: {e}, falling back to uniform score")
            scores = {i: 1.0 / n for i in range(n)}

        scored_sentences = []
        for i, s in enumerate(sentences):
            item = dict(s)
            item["textrank_score"] = float(scores.get(i, 0.0))
            if query_sims is not None:
                item["query_similarity"] = float(query_sims[i])
            scored_sentences.append(item)

        scored_sentences.sort(key=lambda x: x["textrank_score"], reverse=True)
        return scored_sentences

    def select_diverse_summary(
        self,
        ranked_sentences: List[Dict[str, Any]],
        num_sentences: int = 8,
        diversity_lambda: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Maximal Marginal Relevance (MMR) selection to avoid redundant sentences.
        """
        if len(ranked_sentences) <= num_sentences:
            # Sort back into chronological / section order
            return sorted(ranked_sentences, key=lambda x: x["sentence_index"])

        selected = [ranked_sentences[0]]
        candidates = ranked_sentences[1:]

        selected_texts = [selected[0]["text"]]
        selected_vectors = self.encoder.encode_sentences(selected_texts)

        while len(selected) < num_sentences and candidates:
            cand_texts = [c["text"] for c in candidates]
            cand_vectors = self.encoder.encode_sentences(cand_texts)

            best_idx = -1
            best_mmr_score = -float("inf")

            for i, cand in enumerate(candidates):
                relevance = cand["textrank_score"]
                # Maximum similarity to already selected sentences
                cand_vec = cand_vectors[i].reshape(1, -1)
                sims = [float(np.dot(cand_vec, sel_v.reshape(-1, 1))[0][0]) for sel_v in selected_vectors]
                max_redundancy = max(sims) if sims else 0.0

                mmr = diversity_lambda * relevance - (1 - diversity_lambda) * max_redundancy
                if mmr > best_mmr_score:
                    best_mmr_score = mmr
                    best_idx = i

            chosen = candidates.pop(best_idx)
            selected.append(chosen)
            selected_vectors = np.vstack([selected_vectors, cand_vectors[best_idx]])

        # Maintain coherent document flow (ordered by original document sentence index)
        selected.sort(key=lambda x: x["sentence_index"])
        return selected
