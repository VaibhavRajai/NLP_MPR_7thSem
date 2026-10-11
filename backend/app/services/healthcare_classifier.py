import re
from typing import Dict, Any, List
from backend.app.core.logging import logger

HEALTHCARE_TOPIC_CATEGORIES = {
    "Clinical Trials & Human Studies": [
        "randomized controlled trial", "clinical trial", "phase 3", "phase 2", "cohort study",
        "placebo", "double-blind", "intervention", "patient outcomes", "adverse effects"
    ],
    "Diseases & Pathology": [
        "diabetes", "cancer", "carcinoma", "tumor", "syndrome", "hypertension", "infection",
        "cardiovascular", "alzheimer", "pathology", "disease", "disorder", "neurology", "pulmonary"
    ],
    "Diagnostics & Medical Imaging": [
        "mri", "ct scan", "biopsy", "ultrasound", "mammography", "radiology", "diagnostic accuracy",
        "sensitivity and specificity", "biomarker", "spectroscopy", "screening"
    ],
    "Pharmacology & Therapeutics": [
        "pharmacokinetics", "pharmacodynamics", "drug efficacy", "chemotherapy", "immunotherapy",
        "therapeutic", "dosage", "monoclonal antibody", "antibiotic", "vaccine", "inhibitor"
    ],
    "Epidemiology & Public Health": [
        "epidemiology", "incidence", "prevalence", "mortality rate", "public health",
        "transmission", "surveillance", "pandemic", "morbidity", "relative risk"
    ],
    "Hospital & Clinical Care": [
        "hospital", "intensive care unit", "icu", "inpatient", "outpatient", "clinical practice",
        "surgery", "surgical", "nursing", "physician", "pediatric", "oncology"
    ]
}

# Strong non-healthcare exclusion terms (to detect tech, finance, legal, sports, etc.)
NON_HEALTHCARE_INDICATORS = [
    "stock market", "cryptocurrency", "bitcoin", "blockchain", "software architecture",
    "compiler optimization", "database management", "quantum electrodynamics", "astrophysics",
    "macroeconomic policy", "interest rates", "supply chain logistics", "aerospace engineering",
    "civil engineering concrete", "agricultural harvesting", "video game design"
]

class HealthcareDomainClassifier:
    @staticmethod
    def classify_document(title: str, text: str, sample_length: int = 4000) -> Dict[str, Any]:
        """
        Validates whether the content belongs to the biomedical/healthcare domain.
        Examines title, abstract/introductory text, and contextual biomedical terminology.
        """
        combined_text = f"{title}\n{text[:sample_length]}".lower()

        matched_terms: List[str] = []
        category_matches: Dict[str, int] = {}

        for category, terms in HEALTHCARE_TOPIC_CATEGORIES.items():
            category_count = 0
            for term in terms:
                # Word boundary match
                pattern = r'\b' + re.escape(term) + r'\b'
                matches = len(re.findall(pattern, combined_text))
                if matches > 0:
                    category_count += matches
                    matched_terms.append(term)
            if category_count > 0:
                category_matches[category] = category_count

        # Check non-healthcare indicators
        non_health_hits = []
        for term in NON_HEALTHCARE_INDICATORS:
            if re.search(r'\b' + re.escape(term) + r'\b', combined_text):
                non_health_hits.append(term)

        total_medical_hits = len(matched_terms)
        unique_categories = len(category_matches)

        # Confidence calculation
        # Baseline threshold: at least 3 distinct medical terms across at least 1 category
        reasons = []
        is_healthcare = False
        requires_confirmation = False
        confidence = 0.0
        primary_category = "General Healthcare / Biomedical"

        if category_matches:
            primary_category = max(category_matches.items(), key=lambda x: x[1])[0]

        if total_medical_hits >= 5 and unique_categories >= 2 and len(non_health_hits) == 0:
            is_healthcare = True
            confidence = min(0.99, 0.70 + (total_medical_hits * 0.02) + (unique_categories * 0.05))
            reasons.append(f"Confirmed healthcare research paper focusing on '{primary_category}'.")
            reasons.append(f"Detected {total_medical_hits} distinct biomedical indicators across {unique_categories} clinical domains.")
        elif total_medical_hits >= 3 and len(non_health_hits) == 0:
            is_healthcare = True
            confidence = 0.75
            reasons.append(f"Identified medical/biomedical context ({total_medical_hits} terminology matches).")
        elif total_medical_hits >= 2 and len(non_health_hits) <= 1:
            # Uncertain / Borderline
            is_healthcare = True
            requires_confirmation = True
            confidence = 0.52
            reasons.append("Borderline domain classification: limited clinical terminology detected.")
            reasons.append("Requires confirmation before final analysis.")
        else:
            # Clearly unrelated
            is_healthcare = False
            confidence = 0.15
            reasons.append("Document lacks requisite biomedical, clinical, or healthcare research concepts.")
            if non_health_hits:
                reasons.append(f"Detected non-healthcare topics ({', '.join(non_health_hits[:3])}).")

        return {
            "is_healthcare": is_healthcare,
            "confidence": round(confidence, 2),
            "category": primary_category if is_healthcare else "Non-Healthcare",
            "reasons": reasons,
            "detected_terms": list(set(matched_terms))[:15],
            "requires_confirmation": requires_confirmation
        }
