import re
import unicodedata
from typing import List, Dict, Any, Tuple

# Common medical units and abbreviations to protect
PROTECTED_PATTERNS = [
    r'\b\d+(\.\d+)?\s*(mg|mcg|μg|g|kg|ml|mL|L|mmol/L|mg/dL|mmHg|IU|mEq|bpm|%)\b',
    r'\bp\s*([<>=]|<|>)\s*0?\.\d+\b',
    r'\b95%\s*CI\b',
    r'\b[Hh][Rr]\s*=\s*\d+(\.\d+)?\b',
    r'\b[Oo][Rr]\s*=\s*\d+(\.\d+)?\b',
    r'\b[Rr][Rr]\s*=\s*\d+(\.\d+)?\b',
]

class TextCleaner:
    @staticmethod
    def fix_line_breaks_and_hyphenation(text: str) -> str:
        # Reconnect hyphenated words split across lines: "inter-\nvention" -> "intervention"
        text = re.sub(r'(\b[A-Za-z]+)-\s*\n\s*([a-z]+\b)', r'\1\2', text)
        # Preserve newlines after uppercase section headings like ABSTRACT\n, METHODS\n, etc.
        text = re.sub(r'(?i)\b(abstract|introduction|background|objectives|methods|methodology|results|discussion|limitations|conclusion)\s*\n', r'\1\n\n', text)
        # Soften newline within regular sentence lines
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        return text

    @staticmethod
    def remove_boilerplate_headers_footers(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Count frequency of short identical lines across pages (e.g., running headers, page numbers)
        line_counts = {}
        for b in blocks:
            lines = [l.strip() for l in b["text"].split("\n") if l.strip()]
            for l in lines:
                if len(l) < 80 and not l.endswith('.'):
                    line_counts[l] = line_counts.get(l, 0) + 1

        cleaned_blocks = []
        for b in blocks:
            lines = b["text"].split("\n")
            filtered_lines = []
            for l in lines:
                stripped = l.strip()
                # If a short line appears across 3 or more blocks/pages, it's likely a running header/footer
                if stripped and line_counts.get(stripped, 0) >= 3 and not re.search(r'\b(Methods|Results|Discussion|Abstract|Conclusion)\b', stripped, re.I):
                    continue
                # Also filter standalone page numbers like "Page 3 of 12" or "3"
                if re.match(r'^(page\s*\d+(\s*of\s*\d+)?|\d+)$', stripped, re.IGNORECASE):
                    continue
                filtered_lines.append(l)
                
            new_text = "\n".join(filtered_lines).strip()
            if new_text:
                cleaned_blocks.append({
                    "text": new_text,
                    "page": b["page"],
                    "block_id": b["block_id"],
                    "block_type": b.get("block_type", "paragraph")
                })
        return cleaned_blocks

    @staticmethod
    def clean_text(raw_text: str) -> str:
        # Normalize unicode (NFKC to keep accents while fixing ligatures like fi, fl)
        normalized = unicodedata.normalize("NFKC", raw_text)
        
        # Replace odd quotes, dashes, and bullets with standard ASCII
        normalized = re.sub(r'[\u2018\u2019]', "'", normalized)
        normalized = re.sub(r'[\u201C\u201D]', '"', normalized)
        normalized = re.sub(r'[\u2013\u2014]', '-', normalized)
        normalized = re.sub(r'[\u2022\u25E6\u2023]', '- ', normalized)

        # Fix hyphenation across lines
        normalized = TextCleaner.fix_line_breaks_and_hyphenation(normalized)

        # Normalize multiple spaces and tabs while preserving punctuation & sentences
        normalized = re.sub(r'[ \t]+', ' ', normalized)
        normalized = re.sub(r'\s*\n\s*', '\n', normalized)
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)

        return normalized.strip()

    @staticmethod
    def clean_blocks(blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Remove repeated headers/footers
        deduped = TextCleaner.remove_boilerplate_headers_footers(blocks)
        
        cleaned = []
        for b in deduped:
            cleaned_text = TextCleaner.clean_text(b["text"])
            if len(cleaned_text) > 10:  # Ignore meaningless artifacts
                cleaned.append({
                    "text": cleaned_text,
                    "raw_text": b["text"],
                    "page": b["page"],
                    "block_id": b["block_id"],
                    "block_type": b.get("block_type", "paragraph")
                })
        return cleaned
