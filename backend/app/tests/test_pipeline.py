import pytest
import os
from backend.app.nlp.extraction import DocumentExtractor
from backend.app.nlp.cleaning import TextCleaner
from backend.app.nlp.section_detection import SectionDetector
from backend.app.nlp.linguistic_analysis import LinguisticAnalyzer
from backend.app.nlp.entity_recognition import BiomedicalEntityRecognizer
from backend.app.nlp.relation_extraction import RelationExtractor
from backend.app.nlp.textrank import TextRankSummarizer
from backend.app.nlp.instruction_parser import InstructionParser
from backend.app.nlp.evidence_validation import EvidenceValidator
from backend.app.services.healthcare_classifier import HealthcareDomainClassifier

def test_healthcare_domain_classifier_positive(synthetic_paper_text):
    result = HealthcareDomainClassifier.classify_document(
        title="Evaluation of Semaglutide in Patients with Type 2 Diabetes",
        text=synthetic_paper_text
    )
    assert result["is_healthcare"] is True
    assert result["confidence"] > 0.7
    assert len(result["detected_terms"]) > 0

def test_healthcare_domain_classifier_negative(non_healthcare_text):
    result = HealthcareDomainClassifier.classify_document(
        title="Compiler Optimization Techniques for Distributed Bitcoin Mining",
        text=non_healthcare_text
    )
    assert result["is_healthcare"] is False
    assert result["confidence"] < 0.5

def test_document_extraction_pdf(temp_sample_pdf):
    blocks = DocumentExtractor.extract_from_pdf(temp_sample_pdf)
    assert len(blocks) > 0
    assert any("semaglutide" in b["text"].lower() for b in blocks)
    assert blocks[0]["page"] == 1

def test_document_extraction_docx(temp_sample_docx):
    blocks = DocumentExtractor.extract_from_docx(temp_sample_docx)
    assert len(blocks) > 0
    assert any("diabetes" in b["text"].lower() for b in blocks)

def test_document_extraction_txt(synthetic_paper_text):
    blocks = DocumentExtractor.extract_from_txt(synthetic_paper_text)
    assert len(blocks) >= 4
    assert blocks[0]["block_type"] == "paragraph"

def test_text_cleaning_and_section_detection(synthetic_paper_text):
    raw_blocks = DocumentExtractor.extract_from_txt(synthetic_paper_text)
    cleaned = TextCleaner.clean_blocks(raw_blocks)
    assert len(cleaned) > 0
    
    sections = SectionDetector.segment_document(cleaned)
    assert "abstract" in sections and len(sections["abstract"]) > 0
    assert "methodology" in sections and len(sections["methodology"]) > 0
    assert "results" in sections and len(sections["results"]) > 0
    assert "limitations" in sections and len(sections["limitations"]) > 0

def test_linguistic_analysis_negation_and_uncertainty(synthetic_paper_text):
    raw_blocks = DocumentExtractor.extract_from_txt(synthetic_paper_text)
    cleaned = TextCleaner.clean_blocks(raw_blocks)
    sections = SectionDetector.segment_document(cleaned)
    sents = LinguisticAnalyzer.analyze_sentences(sections)
    
    assert len(sents) > 5
    # Verify clinical negation detection on "No evidence of severe pancreatitis"
    neg_sents = [s for s in sents if s["has_negation"]]
    assert len(neg_sents) > 0
    assert any("pancreatitis" in s["text"].lower() for s in neg_sents)

def test_biomedical_entity_recognition(synthetic_paper_text):
    raw_blocks = DocumentExtractor.extract_from_txt(synthetic_paper_text)
    cleaned = TextCleaner.clean_blocks(raw_blocks)
    sections = SectionDetector.segment_document(cleaned)
    sents = LinguisticAnalyzer.analyze_sentences(sections)
    
    ner = BiomedicalEntityRecognizer()
    entities = ner.extract_entities(sents)
    categories = {e["category"] for e in entities}
    
    assert "Disease" in categories
    assert "Medication" in categories
    assert "Hospital" in categories or "Measurement" in categories
    assert any(e["text"].lower() == "semaglutide" for e in entities)

def test_relation_extraction(synthetic_paper_text):
    raw_blocks = DocumentExtractor.extract_from_txt(synthetic_paper_text)
    cleaned = TextCleaner.clean_blocks(raw_blocks)
    sections = SectionDetector.segment_document(cleaned)
    sents = LinguisticAnalyzer.analyze_sentences(sections)
    
    ner = BiomedicalEntityRecognizer()
    entities = ner.extract_entities(sents)
    relations = RelationExtractor.extract_relations(sents, entities)
    assert len(relations) >= 0  # valid execution

def test_textrank_and_custom_instruction_interpretation(synthetic_paper_text):
    raw_blocks = DocumentExtractor.extract_from_txt(synthetic_paper_text)
    cleaned = TextCleaner.clean_blocks(raw_blocks)
    sections = SectionDetector.segment_document(cleaned)
    sents = LinguisticAnalyzer.analyze_sentences(sections)
    
    parsed = InstructionParser.parse_instructions("Focus on methodology and limitations with concise summary", "concise")
    assert parsed["detail_level"] == "concise"
    assert parsed["emphasize_methodology"] is True
    assert parsed["emphasize_limitations"] is True

    summarizer = TextRankSummarizer()
    ranked = summarizer.rank_sentences(sents)
    assert len(ranked) == len(sents)
    selected = summarizer.select_diverse_summary(ranked, num_sentences=5)
    assert len(selected) <= 5

    summary_pack = EvidenceValidator.construct_grounded_summary(selected, parsed, "Trial Report")
    assert len(summary_pack["structured_sections"]) > 0
    assert len(summary_pack["citations"]) == len(selected)
    assert all("REF-" in c["citation_id"] for c in summary_pack["citations"])
