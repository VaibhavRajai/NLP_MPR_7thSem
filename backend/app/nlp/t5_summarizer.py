from typing import List, Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger

_tokenizer = None
_model = None
_device = None
_load_failed = False


def _load_t5():
    """Lazily loads the fine-tuned T5 model once. Returns (tokenizer, model, device) or None."""
    global _tokenizer, _model, _device, _load_failed
    if _model is not None:
        return _tokenizer, _model, _device
    if _load_failed or not settings.T5_ENABLED:
        return None
    try:
        import torch
        from transformers import AutoTokenizer, T5ForConditionalGeneration

        _device = "cuda" if torch.cuda.is_available() else "cpu"
        _tokenizer = AutoTokenizer.from_pretrained(settings.T5_MODEL_PATH)
        _model = T5ForConditionalGeneration.from_pretrained(settings.T5_MODEL_PATH)
        _model.to(_device)
        _model.eval()
        logger.info(f"T5 summarizer loaded from {settings.T5_MODEL_PATH} on {_device}")
        return _tokenizer, _model, _device
    except Exception as e:
        logger.warning(f"T5 model could not be loaded ({e}); falling back to extractive summary.")
        _load_failed = True
        _tokenizer = _model = None
        return None


class T5Summarizer:
    """Query-aware abstractive summarizer built on the fine-tuned T5 PubMed model.

    The query (topic of interest + user instructions) conditions generation in two ways:
      1. Upstream, the evidence passed in has been re-ranked by relevance to the query.
      2. Optionally (settings.T5_PREPEND_QUERY) the query is prepended to the T5 input.
    """

    PREFIX = "summarize: "

    def __init__(self):
        loaded = _load_t5()
        self.available = loaded is not None
        if loaded:
            self.tokenizer, self.model, self.device = loaded

    def _build_chunks(self, sentences: List[str], query: Optional[str]) -> List[str]:
        """Packs sentences into chunks that fit the 512-token T5 encoder window."""
        prefix = self.PREFIX
        if query and settings.T5_PREPEND_QUERY:
            prefix += f"{query.strip()}. "
        prefix_tokens = len(self.tokenizer.tokenize(prefix))
        budget = max(64, settings.T5_MAX_INPUT_TOKENS - prefix_tokens)

        chunks, current, current_len = [], [], 0
        for sent in sentences:
            n_tok = len(self.tokenizer.tokenize(sent))
            if current and current_len + n_tok > budget:
                chunks.append(prefix + " ".join(current))
                current, current_len = [], 0
            current.append(sent)
            current_len += n_tok
        if current:
            chunks.append(prefix + " ".join(current))
        return chunks

    def _generate(self, text: str, max_new_tokens: int, min_new_tokens: int) -> str:
        import torch

        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        ).to(self.device)
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                min_new_tokens=min_new_tokens,
                num_beams=settings.T5_NUM_BEAMS,
                length_penalty=2.0,
                no_repeat_ngram_size=3,
                early_stopping=True,
            )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

    def summarize(
        self,
        evidence_sentences: List[Dict[str, Any]],
        query: Optional[str] = None,
        detail_level: str = "balanced",
    ) -> Optional[str]:
        """Generates an abstractive summary from query-relevant evidence sentences.

        Long evidence is summarized chunk by chunk (map), then merged with a final
        pass (reduce). Returns None if T5 is unavailable or generation fails.
        """
        if not self.available or not evidence_sentences:
            return None

        length_scale = {"concise": 0.6, "balanced": 1.0, "detailed": 1.4}.get(detail_level, 1.0)
        max_new = int(settings.T5_MAX_NEW_TOKENS * length_scale)
        min_new = int(settings.T5_MIN_NEW_TOKENS * length_scale)

        try:
            sentences = [s["text"] for s in evidence_sentences]
            chunks = self._build_chunks(sentences, query)
            partials = [self._generate(c, max_new, min_new) for c in chunks]

            if len(partials) == 1:
                return partials[0]

            merged_input = self.PREFIX + " ".join(partials)
            return self._generate(merged_input, max_new, min_new)
        except Exception as e:
            logger.warning(f"T5 generation failed ({e}); falling back to extractive summary.")
            return None
