import asyncio
from typing import Dict, Any, Optional
from fastapi import HTTPException
from backend.app.core.logging import logger
from backend.app.storage.repository import repository
from backend.app.nlp.linguistic_analysis import LinguisticAnalyzer
from backend.app.nlp.entity_recognition import BiomedicalEntityRecognizer
from backend.app.nlp.relation_extraction import RelationExtractor
from backend.app.nlp.embeddings import SemanticEncoder
from backend.app.nlp.retrieval import EvidenceRetriever
from backend.app.nlp.textrank import TextRankSummarizer
from backend.app.nlp.instruction_parser import InstructionParser
from backend.app.nlp.evidence_validation import EvidenceValidator

class SummaryService:
    @staticmethod
    def run_pipeline(
        doc_id: str,
        instructions: Optional[str] = None,
        topic_of_interest: Optional[str] = None,
        detail_level: str = "balanced",
        confirm_healthcare_override: bool = False
    ) -> Dict[str, Any]:
        doc = repository.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        domain_val = doc.get("domain_validation", {})
        if not domain_val.get("is_healthcare", False) and not confirm_healthcare_override:
            raise HTTPException(
                status_code=422,
                detail="Document was rejected: It is not identified as a healthcare, biomedical, or clinical research paper."
            )

        existing_status = repository.get_status(doc_id) or {}
        stage_records = list(existing_status.get("stage_records", []))
        stages_completed = ["Stage 1: Content extraction", "Stage 2: Text cleaning and normalization", "Stage 3: Research-section identification"]

        # Helper to update or append stage record
        def update_stage_record(stage_id: str, stage_name: str, status: str, summary: str, details: str, metrics: dict):
            for rec in stage_records:
                if rec["stage_id"] == stage_id:
                    rec["status"] = status
                    rec["summary"] = summary
                    rec["details"] = details
                    rec["metrics"] = metrics
                    return
            stage_records.append({
                "stage_id": stage_id,
                "stage_name": stage_name,
                "status": status,
                "summary": summary,
                "details": details,
                "metrics": metrics
            })

        # STAGE 4: Linguistic Analysis
        update_stage_record(
            "Stage 4: Linguistic analysis",
            "Linguistic Analysis",
            "running",
            "Segmenting sentences, detecting NegEx negations and clinical hedging markers...",
            "Analyzing clinical grammar, tokenization, and sentence boundaries with decimal protections.",
            {}
        )
        repository.update_status(
            doc_id,
            status="processing",
            current_stage="Stage 4: Linguistic analysis",
            stages_completed=stages_completed,
            progress=30,
            message="Performing sentence segmentation, POS tagging, negation & uncertainty analysis",
            stage_records=stage_records
        )

        segmented_sections = doc["segmented_sections"]
        analyzed_sentences = LinguisticAnalyzer.analyze_sentences(segmented_sections)
        neg_count = sum(1 for s in analyzed_sentences if s.get("has_negation"))
        hedge_count = sum(1 for s in analyzed_sentences if s.get("has_hedging"))
        stages_completed.append("Stage 4: Linguistic analysis")
        update_stage_record(
            "Stage 4: Linguistic analysis",
            "Linguistic Analysis",
            "completed",
            f"Segmented {len(analyzed_sentences)} clinical sentences. Identified {neg_count} negated statements and {hedge_count} hedging/uncertainty expressions.",
            "Tokenized sentences with decimal and abbreviation safeguards. Evaluated NegEx clinical negation patterns and uncertainty tags.",
            {"total_sentences": len(analyzed_sentences), "negated_statements": neg_count, "hedged_statements": hedge_count}
        )

        # STAGE 5: Biomedical NER
        update_stage_record(
            "Stage 5: Biomedical named entity recognition",
            "Biomedical Named Entity Recognition",
            "running",
            "Extracting diseases, treatments, institutions, biomarkers, and medical devices...",
            "Scanning biomedical vocabularies, clinical entities, and taxonomy classes.",
            {}
        )
        repository.update_status(
            doc_id,
            status="processing",
            current_stage="Stage 5: Biomedical named entity recognition",
            stages_completed=stages_completed,
            progress=45,
            message="Extracting biomedical entities (diseases, drugs, institutions, biomarkers, devices)",
            stage_records=stage_records
        )
        ner = BiomedicalEntityRecognizer()
        extracted_entities = ner.extract_entities(analyzed_sentences)
        grouped_entities = ner.group_entities_by_category(extracted_entities)
        stages_completed.append("Stage 5: Biomedical named entity recognition")
        
        top_cats = ", ".join([f"{len(v)} {k.lower()}s" for k, v in grouped_entities.items() if len(v) > 0][:4])
        update_stage_record(
            "Stage 5: Biomedical named entity recognition",
            "Biomedical Named Entity Recognition",
            "completed",
            f"Extracted {len(extracted_entities)} biomedical entities across {len(grouped_entities)} categories ({top_cats}).",
            f"Classified entities into diseases ({len(grouped_entities.get('Disease', []))}), medications ({len(grouped_entities.get('Medication', []))}), biomarkers ({len(grouped_entities.get('Biomarker', []))}), institutions ({len(grouped_entities.get('Hospital', []))}), and devices ({len(grouped_entities.get('MedicalDevice', []))}).",
            {"total_entities": len(extracted_entities), "categories": {k: len(v) for k, v in grouped_entities.items()}}
        )

        # STAGE 6: Contextual & Relationship Analysis
        update_stage_record(
            "Stage 6: Contextual and relationship analysis",
            "Contextual and Relationship Analysis",
            "running",
            "Mapping clinical relationships between treatments, outcomes, and institutions...",
            "Analyzing entity co-occurrences, dependencies, and relational predicates.",
            {}
        )
        repository.update_status(
            doc_id,
            status="processing",
            current_stage="Stage 6: Contextual and relationship analysis",
            stages_completed=stages_completed,
            progress=58,
            message="Analyzing entity associations, treatment outcomes, and institutional affiliations",
            stage_records=stage_records
        )
        relations = RelationExtractor.extract_relations(analyzed_sentences, extracted_entities)
        stages_completed.append("Stage 6: Contextual and relationship analysis")
        update_stage_record(
            "Stage 6: Contextual and relationship analysis",
            "Contextual and Relationship Analysis",
            "completed",
            f"Extracted {len(relations)} grounded clinical relationships and predicate links.",
            "Formed semantic relationships linking treatments to clinical outcomes, diseases to symptoms, and institutions to clinical trials.",
            {"total_relationships": len(relations)}
        )

        # STAGE 7: Semantic Representation & Retrieval
        update_stage_record(
            "Stage 7: Semantic representation",
            "Semantic Representation",
            "running",
            "Computing semantic embeddings and section representations...",
            "Generating TF-IDF representations and semantic vectors across section blocks.",
            {}
        )
        repository.update_status(
            doc_id,
            status="processing",
            current_stage="Stage 7: Semantic representation",
            stages_completed=stages_completed,
            progress=70,
            message="Generating semantic sentence embeddings and section representations",
            stage_records=stage_records
        )
        retriever = EvidenceRetriever()
        chunks = retriever.chunk_document_by_sections(analyzed_sentences)
        stages_completed.append("Stage 7: Semantic representation")
        update_stage_record(
            "Stage 7: Semantic representation",
            "Semantic Representation",
            "completed",
            f"Formed {len(chunks)} contextual section chunks with dense semantic embeddings.",
            "Prepared sentence vectors and section-level representations for ranking and similarity matching.",
            {"chunks_count": len(chunks)}
        )

        # STAGE 9: Custom Instruction Interpretation
        update_stage_record(
            "Stage 9: Custom instruction interpretation",
            "Custom Instruction Interpretation",
            "running",
            "Interpreting user directives and adjusting summarization parameters...",
            "Parsing natural-language instructions to bias section selection and target lengths.",
            {}
        )
        repository.update_status(
            doc_id,
            status="processing",
            current_stage="Stage 9: Custom instruction interpretation",
            stages_completed=stages_completed,
            progress=78,
            message="Interpreting custom user directives and setting retrieval focus",
            stage_records=stage_records
        )
        parsed_instructions = InstructionParser.parse_instructions(instructions, detail_level)
        
        focus_query = instructions or ""
        if topic_of_interest:
            focus_query = f"{topic_of_interest} {focus_query}".strip()

        filtered_sentences = analyzed_sentences
        if parsed_instructions["focus_sections"]:
            matched_sec_sents = [s for s in analyzed_sentences if s["section"] in parsed_instructions["focus_sections"]]
            if len(matched_sec_sents) >= 4:
                filtered_sentences = matched_sec_sents + [s for s in analyzed_sentences if s["section"] not in parsed_instructions["focus_sections"]]

        stages_completed.append("Stage 9: Custom instruction interpretation")
        focus_topics_str = ", ".join(parsed_instructions.get("focus_topics", [])) or "general clinical synthesis"
        update_stage_record(
            "Stage 9: Custom instruction interpretation",
            "Custom Instruction Interpretation",
            "completed",
            f"Configured retrieval parameters: focus on '{focus_topics_str}' with '{detail_level}' depth ({parsed_instructions['target_sentence_count']} target sentences).",
            f"Interpreted natural language directives: prioritized sections {', '.join(parsed_instructions['focus_sections']) if parsed_instructions['focus_sections'] else 'all'} with targeted sentence budget.",
            {"focus_topics": parsed_instructions.get("focus_topics", []), "target_sentences": parsed_instructions['target_sentence_count'], "focus_sections": parsed_instructions['focus_sections']}
        )

        # STAGE 8: Extractive Summarization (TextRank)
        update_stage_record(
            "Stage 8: Extractive summarization",
            "Extractive Summarization (TextRank)",
            "running",
            "Computing TextRank graph centrality and selecting non-redundant evidence (MMR)...",
            "Constructing sentence similarity graph and executing PageRank algorithm.",
            {}
        )
        repository.update_status(
            doc_id,
            status="processing",
            current_stage="Stage 8: Extractive summarization",
            stages_completed=stages_completed,
            progress=88,
            message="Computing TextRank graph centrality and selecting non-redundant evidence (MMR)",
            stage_records=stage_records
        )
        summarizer = TextRankSummarizer()
        ranked = summarizer.rank_sentences(filtered_sentences)
        
        target_count = parsed_instructions["target_sentence_count"]
        selected_evidence = summarizer.select_diverse_summary(ranked, num_sentences=target_count)
        stages_completed.append("Stage 8: Extractive summarization")
        update_stage_record(
            "Stage 8: Extractive summarization",
            "Extractive Summarization (TextRank)",
            "completed",
            f"Constructed TextRank graph of {len(filtered_sentences)} sentences; selected top {len(selected_evidence)} diverse evidence sentences using MMR.",
            "Computed sentence cosine similarity graph, iterated PageRank centrality to convergence, and applied Maximal Marginal Relevance (lambda=0.7) for diversity.",
            {"graph_nodes": len(filtered_sentences), "selected_sentences": len(selected_evidence)}
        )

        # STAGE 10: Constructive Summary Generation & Evidence Validation
        update_stage_record(
            "Stage 10: Constructive summary generation & validation",
            "Summary Generation and Citation Validation",
            "running",
            "Constructing structured synthesis, extracting statistics, and validating citations...",
            "Mapping extracted summary claims to source sentences and verified page coordinates.",
            {}
        )
        repository.update_status(
            doc_id,
            status="processing",
            current_stage="Stage 10: Constructive summary generation & validation",
            stages_completed=stages_completed,
            progress=95,
            message="Constructing grounded sections, validating claims, statistics, and citations",
            stage_records=stage_records
        )
        summary_pack = EvidenceValidator.construct_grounded_summary(
            selected_sentences=selected_evidence,
            parsed_instructions=parsed_instructions,
            paper_title=doc["title"]
        )

        stat_findings = EvidenceValidator.extract_statistical_findings(analyzed_sentences)
        methodology_info = EvidenceValidator.extract_methodology_details(analyzed_sentences)

        limitations = [
            s["text"] for s in analyzed_sentences 
            if s["section"] == "limitations" or ("limitation" in s["text"].lower() and len(s["text"].split()) > 7)
        ][:4]

        clinical_implications = [
            s["text"] for s in analyzed_sentences 
            if (s["section"] in ["conclusion", "discussion"] and any(k in s["text"].lower() for k in ["suggest", "indicate", "implications", "future", "clinical practice"]))
        ][:4]

        key_findings = [s["text"] for s in selected_evidence if s["section"] in ["results", "abstract"]][:5]
        if not key_findings:
            key_findings = [s["text"] for s in selected_evidence[:4]]

        stages_completed.append("Stage 10: Constructive summary generation & validation")
        update_stage_record(
            "Stage 10: Constructive summary generation & validation",
            "Summary Generation and Citation Validation",
            "completed",
            f"Generated validated synthesis with {len(summary_pack['citations'])} evidence citations [REF-X] and {len(stat_findings)} statistical data points.",
            "Grounded executive summary and structured sections against source sentences and verified page numbers. Extracted p-values, 95% CIs, and methodology parameters.",
            {"citations": len(summary_pack['citations']), "statistics": len(stat_findings)}
        )

        analysis_result = {
            "document_id": doc_id,
            "title": doc["title"],
            "executive_summary": summary_pack["executive_summary"],
            "structured_sections": summary_pack["structured_sections"],
            "key_findings": key_findings,
            "methodology": methodology_info,
            "statistical_findings": stat_findings[:10],
            "entities_by_category": grouped_entities,
            "entity_relationships": relations[:15],
            "study_limitations": limitations,
            "clinical_implications": clinical_implications,
            "citations": summary_pack["citations"],
            "processing_stages_completed": stages_completed,
            "domain_validation": domain_val,
            "instruction_focus_applied": instructions if instructions else "Default balanced synthesis",
            "stage_records": stage_records
        }

        repository.save_analysis(doc_id, analysis_result)
        repository.update_status(
            doc_id,
            status="completed",
            current_stage="Completed",
            stages_completed=stages_completed,
            progress=100,
            message="Healthcare research paper summarized and validated successfully.",
            stage_records=stage_records
        )

        return analysis_result
