import re
from typing import List, Dict, Any, Tuple, Optional

class EvidenceValidator:
    @staticmethod
    def extract_statistical_findings(sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        findings = []
        seen = set()

        # Patterns for p-value, sample size, hazard ratio, confidence intervals
        p_val_pat = r'\bp\s*([<>=]|<|>)\s*(0?\.\d+)\b'
        n_pat = r'\b[nN]\s*=\s*(\d+(?:,\d+)?)\b'
        hr_pat = r'\b([Hh][Rr]|[Oo][Rr]|[Rr][Rr])\s*=\s*(\d+(?:\.\d+)?)\b'
        ci_pat = r'\b95%\s*CI\s*[:=\s]\s*([\d\.]+\s*[-–]\s*[\d\.]+)\b'

        for s in sentences:
            text = s["text"]
            has_p = re.search(p_val_pat, text)
            has_hr = re.search(hr_pat, text)
            has_ci = re.search(ci_pat, text)
            has_n = re.search(n_pat, text)

            if has_p or has_hr or has_ci or has_n:
                metric_name = "Statistical Significance" if has_p else "Clinical Metric"
                val_str = ""
                p_val = has_p.group(0) if has_p else None
                ci_val = has_ci.group(0) if has_ci else None
                sample_size = has_n.group(0) if has_n else None

                if has_hr:
                    metric_name = f"Effect Size ({has_hr.group(1).upper()})"
                    val_str = has_hr.group(2)
                elif has_p:
                    val_str = p_val
                else:
                    val_str = sample_size or "Documented Metric"

                key = (s["page"], text[:40])
                if key not in seen:
                    seen.add(key)
                    findings.append({
                        "metric": metric_name,
                        "value": val_str,
                        "sample_size": sample_size,
                        "p_value": p_val,
                        "confidence_interval": ci_val,
                        "context_sentence": text,
                        "section": s["section"],
                        "page": s["page"]
                    })
        return findings

    @staticmethod
    def extract_methodology_details(sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
        methods_info = {
            "study_type": "Observational / Clinical Investigation",
            "sample_size": None,
            "duration": None,
            "controls_or_groups": None,
            "primary_endpoint": None,
            "statistical_methods": []
        }

        # Check for randomized controlled trial, cohort study, meta-analysis, etc.
        study_types = [
            ("Randomized Controlled Trial (RCT)", r"\brandomized(?:\s+controlled)?\s+trial\b"),
            ("Double-Blind Placebo-Controlled Trial", r"\bdouble-blind\b"),
            ("Prospective Cohort Study", r"\bprospective\s+cohort\b"),
            ("Retrospective Observational Study", r"\bretrospective(?:\s+cohort|\s+study|\s+chart\s+review)\b"),
            ("Systematic Review and Meta-Analysis", r"\bmeta-analysis|systematic\s+review\b"),
            ("Phase 3 Clinical Trial", r"\bphase\s+(?:3|III)\b"),
            ("Phase 2 Clinical Trial", r"\bphase\s+(?:2|II)\b"),
            ("Phase 1 Clinical Trial", r"\bphase\s+(?:1|I)\b"),
            ("Cross-Sectional Study", r"\bcross-sectional\b")
        ]

        # Scan methods or whole text
        all_text = " ".join([s["text"] for s in sentences])
        lower_all = all_text.lower()

        for label, pat in study_types:
            if re.search(pat, lower_all):
                methods_info["study_type"] = label
                break

        # Check sample size
        n_match = re.search(r'\b(?:enrolled|included|randomized|cohort of)\s+(\d+(?:,\d+)?)\s+(?:patients|participants|subjects|individuals)\b', lower_all)
        if n_match:
            methods_info["sample_size"] = f"N = {n_match.group(1)} participants"
        else:
            n_simple = re.search(r'\b[nN]\s*=\s*(\d+(?:,\d+)?)\b', lower_all)
            if n_simple:
                methods_info["sample_size"] = f"N = {n_simple.group(1)}"

        # Check duration
        dur_match = re.search(r'\b(\d+(?:[-–]\d+)?\s+(?:weeks?|months?|years?|days?))\s+(?:follow-up|duration|period|trial)\b', lower_all)
        if dur_match:
            methods_info["duration"] = dur_match.group(0)

        # Statistical tests detected
        stat_tests = [
            ("Kaplan-Meier survival analysis", r"\bkaplan-meier\b"),
            ("Cox proportional hazards regression", r"\bcox\s+(?:proportional\s+hazards|regression)\b"),
            ("Student's t-test", r"\bt-test\b"),
            ("Chi-square test", r"\bchi-square\b"),
            ("ANOVA", r"\banova\b"),
            ("Multivariable logistic regression", r"\blogistic\s+regression\b")
        ]
        for test_name, pat in stat_tests:
            if re.search(pat, lower_all):
                methods_info["statistical_methods"].append(test_name)

        return methods_info

    @staticmethod
    def construct_grounded_summary(
        selected_sentences: List[Dict[str, Any]],
        parsed_instructions: Dict[str, Any],
        paper_title: str
    ) -> Dict[str, Any]:
        """
        Organizes selected evidence into constructive summary sections,
        preserving citations and factual grounding.
        """
        # Map citations
        citations = []
        for idx, s in enumerate(selected_sentences):
            cit_id = f"REF-{idx+1}"
            citations.append({
                "citation_id": cit_id,
                "sentence_id": s["id"],
                "section": s["section"],
                "page": s["page"],
                "original_text": s["text"]
            })

        # Categorize selected sentences into summary sections
        sec_buckets = {
            "overview": [],
            "objectives": [],
            "methodology": [],
            "findings": [],
            "limitations": [],
            "implications": []
        }

        for idx, s in enumerate(selected_sentences):
            sec_name = s.get("section", "other")
            cit_id = f"REF-{idx+1}"
            annotated_sent = f"{s['text']} [{cit_id}]"

            if sec_name in ["abstract", "introduction"]:
                sec_buckets["overview"].append((annotated_sent, cit_id))
            elif sec_name == "objectives":
                sec_buckets["objectives"].append((annotated_sent, cit_id))
            elif sec_name == "methodology":
                sec_buckets["methodology"].append((annotated_sent, cit_id))
            elif sec_name in ["results"]:
                sec_buckets["findings"].append((annotated_sent, cit_id))
            elif sec_name == "limitations":
                sec_buckets["limitations"].append((annotated_sent, cit_id))
            elif sec_name in ["discussion", "conclusion"]:
                sec_buckets["implications"].append((annotated_sent, cit_id))
            else:
                sec_buckets["findings"].append((annotated_sent, cit_id))

        # Assemble structured sections
        structured_sections = []
        
        # 1. Overview
        if sec_buckets["overview"]:
            text_block = " ".join([t[0] for t in sec_buckets["overview"]])
            cits = [t[1] for t in sec_buckets["overview"]]
            structured_sections.append({
                "title": "Research Overview & Context",
                "content": text_block,
                "key_points": [t[0] for t in sec_buckets["overview"]],
                "citation_ids": cits
            })

        # 2. Objectives (if present)
        if sec_buckets["objectives"]:
            text_block = " ".join([t[0] for t in sec_buckets["objectives"]])
            cits = [t[1] for t in sec_buckets["objectives"]]
            structured_sections.append({
                "title": "Research Objectives & Hypotheses",
                "content": text_block,
                "key_points": [t[0] for t in sec_buckets["objectives"]],
                "citation_ids": cits
            })

        # 3. Methodology
        if sec_buckets["methodology"]:
            text_block = " ".join([t[0] for t in sec_buckets["methodology"]])
            cits = [t[1] for t in sec_buckets["methodology"]]
            structured_sections.append({
                "title": "Study Design & Methodology",
                "content": text_block,
                "key_points": [t[0] for t in sec_buckets["methodology"]],
                "citation_ids": cits
            })

        # 4. Key Findings
        if sec_buckets["findings"]:
            text_block = " ".join([t[0] for t in sec_buckets["findings"]])
            cits = [t[1] for t in sec_buckets["findings"]]
            structured_sections.append({
                "title": "Key Findings & Evidence",
                "content": text_block,
                "key_points": [t[0] for t in sec_buckets["findings"]],
                "citation_ids": cits
            })

        # 5. Limitations
        if sec_buckets["limitations"]:
            text_block = " ".join([t[0] for t in sec_buckets["limitations"]])
            cits = [t[1] for t in sec_buckets["limitations"]]
            structured_sections.append({
                "title": "Study Limitations & Constraints",
                "content": text_block,
                "key_points": [t[0] for t in sec_buckets["limitations"]],
                "citation_ids": cits
            })

        # 6. Clinical Implications & Conclusions
        if sec_buckets["implications"]:
            text_block = " ".join([t[0] for t in sec_buckets["implications"]])
            cits = [t[1] for t in sec_buckets["implications"]]
            structured_sections.append({
                "title": "Clinical Implications & Future Directions",
                "content": text_block,
                "key_points": [t[0] for t in sec_buckets["implications"]],
                "citation_ids": cits
            })

        # Executive summary narrative
        executive_summary = " ".join([s["text"] for s in selected_sentences[:4]])

        return {
            "executive_summary": executive_summary,
            "structured_sections": structured_sections,
            "citations": citations
        }
