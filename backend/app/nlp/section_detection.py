import re
from typing import List, Dict, Any, Optional, Tuple

SECTION_PATTERNS = {
    "abstract": [
        r"^(?:abstract|summary|structured\s+abstract|capsule\s+summary)\b",
        r"^(?:importance|background\s+and\s+rationale)\b"
    ],
    "introduction": [
        r"^(?:\d+\.?\s*)?(?:introduction|background|literature\s+review)\b",
        r"^(?:\d+\.?\s*)?(?:context|prior\s+work)\b"
    ],
    "objectives": [
        r"^(?:\d+\.?\s*)?(?:objective[s]?|aim[s]?|research\s+question[s]?|purpose|hypothesis)\b",
        r"^(?:study\s+goals?)\b"
    ],
    "methodology": [
        r"^(?:\d+\.?\s*)?(?:methods?|methodology|materials\s+and\s+methods|patients\s+and\s+methods|study\s+design|experimental\s+procedures|cohort\s+selection|statistical\s+analysis)\b",
        r"^(?:\d+\.?\s*)?(?:interventions?|participants?|protocol)\b"
    ],
    "results": [
        r"^(?:\d+\.?\s*)?(?:results?|findings|data\s+analysis|primary\s+outcomes?|clinical\s+outcomes?|observations)\b",
        r"^(?:\d+\.?\s*)?(?:efficacy\s+and\s+safety)\b"
    ],
    "discussion": [
        r"^(?:\d+\.?\s*)?(?:discussion|interpretation|comments|clinical\s+implications)\b"
    ],
    "limitations": [
        r"^(?:\d+\.?\s*)?(?:limitations?|study\s+limitations?|potential\s+biases?|caveats)\b"
    ],
    "conclusion": [
        r"^(?:\d+\.?\s*)?(?:conclusions?|concluding\s+remarks|summary\s+and\s+conclusions?)\b"
    ]
}

class SectionDetector:
    @staticmethod
    def identify_heading(text: str) -> Optional[Tuple[str, str]]:
        """
        Returns (section_key, remaining_body_text) if heading detected, else None.
        """
        first_line = text.split("\n")[0].strip()
        cleaned_line = re.sub(r'^[0-9\.\-\s]+', '', first_line).lower()

        # Check whole first line if short (< 85 chars)
        if len(first_line) < 85:
            for section_key, patterns in SECTION_PATTERNS.items():
                for pat in patterns:
                    if re.search(pat, cleaned_line, re.IGNORECASE):
                        remaining = "\n".join(text.split("\n")[1:]).strip()
                        return (section_key, remaining)

        # Check inline prefix heading e.g. "ABSTRACT: ...", "ABSTRACT Background: ..."
        for section_key, patterns in SECTION_PATTERNS.items():
            for pat in patterns:
                m = re.match(pat + r'[:\.\s\-]+', text, re.IGNORECASE)
                if m:
                    remaining = text[m.end():].strip()
                    return (section_key, remaining)

        return None

    @staticmethod
    def segment_document(cleaned_blocks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        sections: Dict[str, List[Dict[str, Any]]] = {
            "title_metadata": [],
            "abstract": [],
            "introduction": [],
            "objectives": [],
            "methodology": [],
            "results": [],
            "discussion": [],
            "limitations": [],
            "conclusion": [],
            "other": []
        }

        current_section = "title_metadata"

        for idx, block in enumerate(cleaned_blocks):
            text = block["text"]
            heading_info = SectionDetector.identify_heading(text)

            if heading_info:
                section_key, remaining_text = heading_info
                current_section = section_key
                if remaining_text:
                    block_copy = dict(block)
                    block_copy["text"] = remaining_text
                    block_copy["section"] = current_section
                    sections[current_section].append(block_copy)
                continue

            # Fallback heuristic for unstructured papers:
            # If still in title_metadata after first block or 2, switch to abstract or introduction
            if current_section == "title_metadata" and idx > 0:
                lower = text.lower()
                if "we conducted" in lower or "methods" in lower or "patients were" in lower:
                    current_section = "methodology"
                elif "we found" in lower or "results indicated" in lower or "p <" in lower or "hazard ratio" in lower:
                    current_section = "results"
                elif "in this study" in lower or "background" in lower:
                    current_section = "introduction"
                else:
                    if idx >= 2 and len(sections["abstract"]) == 0:
                        current_section = "abstract"
                    elif idx >= 4:
                        current_section = "introduction"

            block_copy = dict(block)
            block_copy["section"] = current_section
            sections[current_section].append(block_copy)

        return sections

    @staticmethod
    def extract_paper_title(blocks: List[Dict[str, Any]]) -> str:
        if not blocks:
            return "Untitled Healthcare Research Paper"
        
        # Look for the first prominent block on page 1
        for b in blocks[:3]:
            lines = [l.strip() for l in b["text"].split("\n") if l.strip()]
            for line in lines:
                # Title shouldn't be "Abstract" or copyright
                if len(line) > 15 and len(line) < 250 and not re.search(r'\b(abstract|issn|doi|journal|volume|published|copyright)\b', line, re.I):
                    return line
        return blocks[0]["text"][:120].strip()
