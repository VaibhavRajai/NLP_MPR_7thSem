import re
from typing import List, Dict, Any, Set
import spacy
from backend.app.core.logging import logger

# Medical domain dictionaries & vocabularies
BIOMEDICAL_VOCAB = {
    "Disease": [
        "diabetes mellitus", "type 2 diabetes", "type 1 diabetes", "hypertension",
        "alzheimer's disease", "parkinson's disease", "covid-19", "sars-cov-2",
        "myocardial infarction", "heart failure", "stroke", "atherosclerosis",
        "breast cancer", "lung adenocarcinoma", "colorectal cancer", "melanoma",
        "glioblastoma", "leukemia", "lymphoma", "asthma", "copd", "pneumonia",
        "acute respiratory distress syndrome", "ards", "sepsis", "septic shock",
        "rheumatoid arthritis", "systemic lupus erythematosus", "crohn's disease",
        "ulcerative colitis", "chronic kidney disease", "acute kidney injury",
        "depression", "major depressive disorder", "bipolar disorder", "schizophrenia",
        "dyspnea", "arrhythmia", "tachycardia", "bradycardia", "neuropathy",
        "hypoglycemia", "hyperglycemia", "ketoacidosis", "ischemia", "thrombosis"
    ],
    "Medication": [
        "metformin", "semaglutide", "tirzepatide", "insulin glargine", "lispro",
        "atorvastatin", "rosuvastatin", "amlodipine", "lisinopril", "losartan",
        "pembrolizumab", "nivolumab", "trastuzumab", "rituximab", "bevacizumab",
        "remdesivir", "paxlovid", "dexamethasone", "prednisone", "hydrocortisone",
        "aspirin", "clopidogrel", "apixaban", "rivaroxaban", "warfarin", "heparin",
        "cisplatin", "carboplatin", "paclitaxel", "doxorubicin", "methotrexate",
        "adalimumab", "infliximab", "tocilizumab", "chemotherapy", "immunotherapy",
        "radiotherapy", "radiation therapy", "mrna-1273", "bnt162b2", "placebo"
    ],
    "Biomarker": [
        "hba1c", "hemoglobin a1c", "troponin", "troponin i", "troponin t",
        "crp", "c-reactive protein", "her2", "egfr", "kras", "braf", "brca1", "brca2",
        "pdl1", "pd-l1", "il-6", "interleukin-6", "tnf-alpha", "cd4+", "cd8+",
        "bnp", "nt-probnp", "ldl", "ldl-c", "hdl", "triglycerides", "creatinine",
        "egfr", "alanine aminotransferase", "alt", "ast", "d-dimer", "ferritin"
    ],
    "MedicalDevice": [
        "continuous glucose monitor", "cgm", "insulin pump", "pacemaker",
        "implantable cardioverter-defibrillator", "icd", "stent", "drug-eluting stent",
        "ventilator", "mechanical ventilation", "mri", "mri scanner", "ct scanner",
        "computed tomography", "ecg", "electrocardiogram", "pulse oximeter",
        "dialysis machine", "prosthesis", "robotic surgical system", "catheter"
    ],
    "ClinicalOutcome": [
        "overall survival", "progression-free survival", "disease-free survival",
        "mortality", "all-cause mortality", "cardiovascular mortality",
        "remission", "complete response", "partial response", "adverse events",
        "serious adverse events", "hospitalization", "icu admission",
        "glycemic control", "blood pressure reduction", "time to recovery"
    ]
}

# Regex patterns for clinical institutions and statistics
HOSPITAL_KEYWORDS = [
    r"\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+)?(?:Hospital|Medical Center|Clinic|Health System|Infirmary|Foundation Trust|Institute of Medicine|Cancer Center)\b",
    r"\b(?:Mayo Clinic|Johns Hopkins|Cleveland Clinic|Massachusetts General Hospital|Mount Sinai|Stanford Health Care|Memorial Sloan Kettering|Brigham and Women's)\b"
]

POPULATION_PATTERNS = [
    r"\b(?:pediatric|adult|elderly|geriatric|neonatal|adolescent)\s+(?:patients|cohort|population|participants)\b",
    r"\b(?:patients|participants|subjects)\s+aged\s+\d+(?:[-–]\d+)?(?:\s+years)?\b",
    r"\b(?:male|female)\s+(?:patients|participants|cohort)\b",
    r"\b(?:critically ill|outpatient|inpatient|ICU)\s+patients\b"
]

MEASUREMENT_STAT_PATTERNS = [
    r"\bp\s*[<>=]\s*0?\.\d+\b",
    r"\b(?:HR|OR|RR)\s*=\s*\d+(?:\.\d+)?(?:\s*,\s*95%\s*CI\s*[:=\s]\s*[\d\.]+\s*[-–]\s*[\d\.]+)?\b",
    r"\b95%\s*CI\s*[:=\s]\s*[\d\.]+\s*[-–]\s*[\d\.]+\b",
    r"\bn\s*=\s*\d+(?:,\d+)?\b",
    r"\bN\s*=\s*\d+(?:,\d+)?\b",
    r"\b\d+(?:\.\d+)?\s*(?:mg|mcg|g|kg|ml|mL|IU|mmol/L|mg/dL|mmHg|%)\b"
]

class BiomedicalEntityRecognizer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            import en_core_web_sm
            self.nlp = en_core_web_sm.load()

    def extract_entities(self, sentences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        extracted_entities = []
        seen_keys: Set[str] = set()

        for sent in sentences:
            text = sent["text"]
            section = sent["section"]
            page = sent["page"]
            lower_text = text.lower()

            # 1. Dictionary-based biomedical terminology matching
            for category, terms in BIOMEDICAL_VOCAB.items():
                for term in terms:
                    pattern = r'\b' + re.escape(term) + r'\b'
                    for match in re.finditer(pattern, lower_text):
                        start, end = match.span()
                        original_cased_term = text[start:end]
                        unique_key = f"{category}:{original_cased_term.lower()}:{page}:{start}"
                        
                        if unique_key not in seen_keys:
                            seen_keys.add(unique_key)
                            extracted_entities.append({
                                "text": original_cased_term,
                                "category": category,
                                "start_char": start,
                                "end_char": end,
                                "section": section,
                                "page": page,
                                "sentence_id": sent["id"],
                                "confidence": 0.95
                            })

            # 2. Healthcare institutions / Hospitals
            for pat in HOSPITAL_KEYWORDS:
                for match in re.finditer(pat, text):
                    matched_text = match.group().strip()
                    if len(matched_text) > 4 and matched_text.lower() not in ["hospital", "clinic"]:
                        unique_key = f"Hospital:{matched_text.lower()}:{page}:{match.start()}"
                        if unique_key not in seen_keys:
                            seen_keys.add(unique_key)
                            extracted_entities.append({
                                "text": matched_text,
                                "category": "Hospital",
                                "start_char": match.start(),
                                "end_char": match.end(),
                                "section": section,
                                "page": page,
                                "sentence_id": sent["id"],
                                "confidence": 0.88
                            })

            # 3. Patient population
            for pat in POPULATION_PATTERNS:
                for match in re.finditer(pat, text, re.IGNORECASE):
                    matched_text = match.group().strip()
                    unique_key = f"PatientPopulation:{matched_text.lower()}:{page}:{match.start()}"
                    if unique_key not in seen_keys:
                        seen_keys.add(unique_key)
                        extracted_entities.append({
                            "text": matched_text,
                            "category": "PatientPopulation",
                            "start_char": match.start(),
                            "end_char": match.end(),
                            "section": section,
                            "page": page,
                            "sentence_id": sent["id"],
                            "confidence": 0.90
                        })

            # 4. Statistical measurements
            for pat in MEASUREMENT_STAT_PATTERNS:
                for match in re.finditer(pat, text):
                    matched_text = match.group().strip()
                    unique_key = f"Measurement:{matched_text.lower()}:{page}:{match.start()}"
                    if unique_key not in seen_keys:
                        seen_keys.add(unique_key)
                        extracted_entities.append({
                            "text": matched_text,
                            "category": "Measurement",
                            "start_char": match.start(),
                            "end_char": match.end(),
                            "section": section,
                            "page": page,
                            "sentence_id": sent["id"],
                            "confidence": 0.98
                        })

            # 5. Spacy GPE for locations
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "GPE":
                    unique_key = f"Location:{ent.text.lower()}:{page}:{ent.start_char}"
                    if unique_key not in seen_keys:
                        seen_keys.add(unique_key)
                        extracted_entities.append({
                            "text": ent.text,
                            "category": "Location",
                            "start_char": ent.start_char,
                            "end_char": ent.end_char,
                            "section": section,
                            "page": page,
                            "sentence_id": sent["id"],
                            "confidence": 0.85
                        })

        return extracted_entities

    @staticmethod
    def group_entities_by_category(entities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        # Keep deduplicated unique entities per category
        seen_per_category: Dict[str, Set[str]] = {}

        for ent in entities:
            cat = ent["category"]
            if cat not in grouped:
                grouped[cat] = []
                seen_per_category[cat] = set()

            norm_text = ent["text"].lower()
            if norm_text not in seen_per_category[cat]:
                seen_per_category[cat].add(norm_text)
                grouped[cat].append(ent)

        return grouped
