import re
from typing import Dict, Any, List, Optional

class InstructionParser:
    @staticmethod
    def parse_instructions(instructions: Optional[str], default_detail: str = "balanced") -> Dict[str, Any]:
        result = {
            "has_custom_instructions": bool(instructions and instructions.strip()),
            "raw_instruction": instructions or "",
            "focus_sections": [],
            "focus_topics": [],
            "audience_style": "clinical_technical",  # or "simplified_layperson"
            "emphasize_statistics": False,
            "emphasize_institutions": False,
            "emphasize_methodology": False,
            "emphasize_limitations": False,
            "emphasize_treatment": False,
            "detail_level": default_detail,
            "target_sentence_count": 8
        }

        # Detail level adjustment
        if default_detail == "concise":
            result["target_sentence_count"] = 5
        elif default_detail == "detailed":
            result["target_sentence_count"] = 14
        else:
            result["target_sentence_count"] = 8

        if not instructions or not instructions.strip():
            return result

        lower = instructions.lower()

        # Check detail level override in prompt
        if any(w in lower for w in ["brief", "short", "concise", "in a nutshell", "quick summary"]):
            result["detail_level"] = "concise"
            result["target_sentence_count"] = 5
        elif any(w in lower for w in ["comprehensive", "detailed", "in-depth", "thorough", "exhaustive"]):
            result["detail_level"] = "detailed"
            result["target_sentence_count"] = 14

        # Audience style
        if any(w in lower for w in ["simple language", "plain language", "layperson", "layman", "accessible", "easy to understand", "patient friendly"]):
            result["audience_style"] = "simplified_layperson"

        # Methodology & Study design
        if any(w in lower for w in ["method", "design", "protocol", "trial structure", "procedure"]):
            result["emphasize_methodology"] = True
            result["focus_sections"].append("methodology")
            result["focus_topics"].append("methodology")

        # Limitations & Biases
        if any(w in lower for w in ["limitation", "weakness", "bias", "caveat", "shortcoming"]):
            result["emphasize_limitations"] = True
            result["focus_sections"].append("limitations")
            result["focus_topics"].append("limitations")

        # Treatment & Effectiveness
        if any(w in lower for w in ["treatment", "therapy", "drug", "efficacy", "effectiveness", "outcome"]):
            result["emphasize_treatment"] = True
            result["focus_topics"].append("treatment_efficacy")
            if "results" not in result["focus_sections"]:
                result["focus_sections"].append("results")

        # Statistics & Sample size
        if any(w in lower for w in ["statistic", "p-value", "sample size", "cohort size", "numbers", "data", "hazard ratio"]):
            result["emphasize_statistics"] = True
            result["focus_topics"].append("statistics")

        # Hospitals & Institutions
        if any(w in lower for w in ["hospital", "institution", "center", "university", "author affiliation", "location"]):
            result["emphasize_institutions"] = True
            result["focus_topics"].append("institutions")

        # Clinical implications
        if any(w in lower for w in ["implication", "future direction", "clinical impact", "recommendation"]):
            result["focus_sections"].append("discussion")
            result["focus_sections"].append("conclusion")

        return result
