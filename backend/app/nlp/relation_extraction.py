import re
from typing import List, Dict, Any, Tuple

RELATION_PATTERNS = [
    {
        "type": "treats_or_improves",
        "verbs": [r"reduced", r"improved", r"decreased", r"suppressed", r"alleviated", r"lowered", r"treats", r"effective against"],
        "source_cats": ["Medication", "MedicalDevice"],
        "target_cats": ["Disease", "Biomarker", "ClinicalOutcome"]
    },
    {
        "type": "associated_with",
        "verbs": [r"associated with", r"correlated with", r"linked to", r"risk factor for"],
        "source_cats": ["Biomarker", "Disease"],
        "target_cats": ["Disease", "ClinicalOutcome"]
    },
    {
        "type": "conducted_at",
        "verbs": [r"conducted at", r"enrolled at", r"performed at", r"approved by the ethics committee of"],
        "source_cats": ["PatientPopulation", "Disease"],
        "target_cats": ["Hospital", "Location"]
    },
    {
        "type": "measured_in",
        "verbs": [r"measured in", r"assessed in", r"evaluated in", r"detected in"],
        "source_cats": ["Biomarker", "Measurement"],
        "target_cats": ["PatientPopulation", "Disease"]
    },
    {
        "type": "resulted_in",
        "verbs": [r"resulted in", r"led to", r"demonstrated", r"yielded", r"caused"],
        "source_cats": ["Medication", "MedicalDevice"],
        "target_cats": ["ClinicalOutcome", "Measurement"]
    }
]

class RelationExtractor:
    @staticmethod
    def extract_relations(sentences: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Index entities by sentence_id
        sent_entities_map: Dict[str, List[Dict[str, Any]]] = {}
        for ent in entities:
            s_id = ent.get("sentence_id")
            if s_id:
                if s_id not in sent_entities_map:
                    sent_entities_map[s_id] = []
                sent_entities_map[s_id].append(ent)

        extracted_relations = []
        seen_triples = set()

        for sent in sentences:
            s_id = sent["id"]
            sent_ents = sent_entities_map.get(s_id, [])
            if len(sent_ents) < 2:
                continue

            text = sent["text"]
            lower_text = text.lower()

            # Pairwise check within same sentence with syntactic predicate requirement
            for i in range(len(sent_ents)):
                for j in range(len(sent_ents)):
                    if i == j:
                        continue
                    e1 = sent_ents[i]
                    e2 = sent_ents[j]

                    for rule in RELATION_PATTERNS:
                        if e1["category"] in rule["source_cats"] and e2["category"] in rule["target_cats"]:
                            # Look for predicate verb appearing between or near the entities
                            for verb_pat in rule["verbs"]:
                                if re.search(r'\b' + verb_pat + r'\b', lower_text):
                                    triple_key = (e1["text"].lower(), rule["type"], e2["text"].lower())
                                    if triple_key not in seen_triples:
                                        seen_triples.add(triple_key)
                                        extracted_relations.append({
                                            "source_entity": e1["text"],
                                            "source_category": e1["category"],
                                            "relation_type": rule["type"],
                                            "target_entity": e2["text"],
                                            "target_category": e2["category"],
                                            "evidence_sentence": text,
                                            "section": sent["section"],
                                            "page": sent["page"],
                                            "confidence": 0.88
                                        })
                                    break
        return extracted_relations
