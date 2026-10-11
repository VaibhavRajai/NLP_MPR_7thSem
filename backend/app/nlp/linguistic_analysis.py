import spacy
from typing import List, Dict, Any, Tuple
import re
from backend.app.core.logging import logger

# Load Spacy English model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import en_core_web_sm
    nlp = en_core_web_sm.load()

# Clinical negation triggers
NEGATION_PRE_TRIGGERS = [
    r"\bno\b", r"\bnot\b", r"\bnone\b", r"\bnever\b", r"\bwithout\b",
    r"\bno evidence of\b", r"\babsence of\b", r"\bdenies\b", r"\bdenied\b",
    r"\bfailed to (?:show|demonstrate|prove|observe|indicate)\b",
    r"\brules? out\b", r"\bruled out\b", r"\bunlikely\b", r"\bnegative for\b",
    r"\bdid not\b", r"\bdoes not\b", r"\bcannot\b", r"\bneither\b", r"\bnor\b"
]

# Uncertainty / Hedging cues
UNCERTAINTY_TRIGGERS = [
    r"\bmay (?:suggest|indicate|reflect|explain|contribute)\b",
    r"\bmight (?:suggest|indicate|reflect)\b",
    r"\bcould (?:be|represent|suggest)\b",
    r"\bpossibly\b", r"\bpotentially\b", r"\bhypothesized\b",
    r"\bpreliminary\b", r"\bputative\b", r"\bwarrants further\b",
    r"\buncertain\b", r"\binconclusive\b"
]

class LinguisticAnalyzer:
    @staticmethod
    def split_sentences_safely(text: str) -> List[str]:
        # Temporarily mask medical decimal numbers and common abbreviations
        # e.g. "p < 0.05", "Fig. 1", "et al.", "i.e.", "e.g."
        masked = text
        masked = re.sub(r'\bet al\.', 'et_al_dot', masked, flags=re.I)
        masked = re.sub(r'\bFig\.', 'Fig_dot', masked, flags=re.I)
        masked = re.sub(r'\bi\.e\.', 'i_e_dot', masked, flags=re.I)
        masked = re.sub(r'\be\.g\.', 'e_g_dot', masked, flags=re.I)
        masked = re.sub(r'\bvs\.', 'vs_dot', masked, flags=re.I)
        masked = re.sub(r'\bNo\.', 'No_dot', masked, flags=re.I)
        masked = re.sub(r'(\d+)\.(\d+)', r'\1_dot_\2', masked)

        doc = nlp(masked)
        sentences = []
        for sent in doc.sents:
            s_text = sent.text.strip()
            # Unmask
            s_text = s_text.replace('et_al_dot', 'et al.')
            s_text = s_text.replace('Fig_dot', 'Fig.')
            s_text = s_text.replace('i_e_dot', 'i.e.')
            s_text = s_text.replace('e_g_dot', 'e.g.')
            s_text = s_text.replace('vs_dot', 'vs.')
            s_text = s_text.replace('No_dot', 'No.')
            s_text = re.sub(r'(\d+)_dot_(\d+)', r'\1.\2', s_text)
            if len(s_text) > 10:
                sentences.append(s_text)
        return sentences

    @staticmethod
    def detect_negation(sentence_text: str) -> Dict[str, Any]:
        lower = sentence_text.lower()
        matched_negations = []
        for pat in NEGATION_PRE_TRIGGERS:
            match = re.search(pat, lower)
            if match:
                matched_negations.append(match.group())
        return {
            "has_negation": len(matched_negations) > 0,
            "negation_cues": matched_negations
        }

    @staticmethod
    def detect_uncertainty(sentence_text: str) -> Dict[str, Any]:
        lower = sentence_text.lower()
        matched_cues = []
        for pat in UNCERTAINTY_TRIGGERS:
            match = re.search(pat, lower)
            if match:
                matched_cues.append(match.group())
        return {
            "is_uncertain": len(matched_cues) > 0,
            "uncertainty_cues": matched_cues
        }

    @staticmethod
    def analyze_sentences(segmented_sections: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        analyzed_sentences = []
        sentence_idx = 0

        for section_name, blocks in segmented_sections.items():
            for block in blocks:
                page = block.get("page", 1)
                block_id = block.get("block_id", 0)
                text = block.get("text", "")
                
                sents = LinguisticAnalyzer.split_sentences_safely(text)
                for sent_str in sents:
                    sentence_idx += 1
                    neg_info = LinguisticAnalyzer.detect_negation(sent_str)
                    unc_info = LinguisticAnalyzer.detect_uncertainty(sent_str)
                    
                    # Quick POS and token analysis for linguistic stats
                    spacy_doc = nlp(sent_str)
                    lemmas = [tok.lemma_.lower() for tok in spacy_doc if not tok.is_stop and tok.is_alpha]
                    pos_tags = [(tok.text, tok.pos_) for tok in spacy_doc[:10]]  # sample

                    analyzed_sentences.append({
                        "id": f"s_{sentence_idx}",
                        "sentence_index": sentence_idx,
                        "text": sent_str,
                        "section": section_name,
                        "page": page,
                        "block_id": block_id,
                        "lemmas": lemmas,
                        "pos_tags": pos_tags,
                        "has_negation": neg_info["has_negation"],
                        "negation_cues": neg_info["negation_cues"],
                        "is_uncertain": unc_info["is_uncertain"],
                        "uncertainty_cues": unc_info["uncertainty_cues"],
                        "char_length": len(sent_str),
                        "word_count": len(sent_str.split())
                    })

        return analyzed_sentences
