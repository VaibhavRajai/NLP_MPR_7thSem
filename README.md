# Healthcare Research Paper Summarizer Using NLP

A full-stack, healthcare-exclusive scientific research paper summarization web application built with **React.js**, **FastAPI**, and an advanced **10-stage biomedical NLP pipeline**.

---

## 🌟 Key Features

- **Strict Healthcare Domain Restriction**: Contextual classification, MeSH/ICD-10 clinical vocabularies, title/abstract screening, and biomedical named entity recognition to ensure only valid biomedical, clinical, and healthcare research papers are accepted. Non-healthcare documents are cleanly rejected with clear reasoning, while borderline papers trigger user confirmation.
- **Multi-Format Document Ingestion**:
  - PDF uploads (native text extraction via PyMuPDF with OCR fallback)
  - DOCX uploads
  - Plain TXT uploads
  - Pasted research paper text & abstracts
  - Open-access research paper URLs (with strict SSRF protections against internal/private IP ranges)
- **10-Stage Mandatory NLP Processing Pipeline**:
  1. **Content Extraction**: Structural block extraction preserving pagination, sections, and metadata.
  2. **Text Cleaning & Normalization**: Line-break & hyphenation reconstruction while preserving clinical abbreviations, units (`mg`, `mmol/L`, `mmHg`), negations, and statistical notations (`p < 0.001`, `95% CI`).
  3. **Research-Section Identification**: Heuristic & pattern-based detection for *Title/Abstract*, *Introduction/Background*, *Objectives*, *Methodology/Study Design*, *Results/Findings*, *Discussion*, *Limitations*, and *Conclusion*.
  4. **Linguistic Analysis**: Sentence segmentation with decimal protection, tokenization, lemmatization, POS tagging, and NegEx clinical negation & hedging analysis.
  5. **Biomedical Named Entity Recognition (NER)**: Identifies Diseases & Symptoms, Medications & Treatments, Healthcare Institutions & Hospitals, Biomarkers, Medical Devices, Patient Populations, Clinical Outcomes, and Measurements.
  6. **Contextual & Relationship Analysis**: Detects grounded clinical relationships between entities (e.g. treatment $\rightarrow$ outcome, hospital $\rightarrow$ study location).
  7. **Semantic Representation**: Document chunking by sections and hybrid Sentence-Transformers / TF-IDF semantic embeddings.
  8. **Extractive Summarization (TextRank)**: Graph-based PageRank sentence centrality combined with section weighting and Maximal Marginal Relevance (MMR) for diversity and redundancy reduction.
  9. **Custom Instruction Interpretation**: Interprets user natural-language directives (e.g., focus on methodology, emphasize statistical results, simple language) to adapt retrieval weights and summary depth (`concise`, `balanced`, `detailed`).
  10. **Constructive Summary Generation & Evidence Validation**: Synthesizes verified executive summaries, structured sections, study design parameters, statistical tables, and citations (`[REF-X]`) linking back to original document sentences and page numbers.
- **Interactive Medical UI**:
  - Executive summary and structured sections with clickable citation badges (`[REF-X]`) opening original evidence popups.
  - Tabbed views for **Structured Summary**, **Biomedical Entities**, **Statistical Findings** table, and **Entity Relationships**.
  - Real-time progress stepper displaying genuine stage progress.
  - Strict scope: Focused exclusively on research paper summarization with no conversational chatbot features.

---

## 🏗️ Architecture

```
d:\NLP MPR\
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint
│   │   ├── core/
│   │   │   ├── config.py            # Environment & app configuration
│   │   │   └── logging.py           # Logging setup
│   │   ├── api/
│   │   │   ├── schemas/             # Pydantic schemas (document.py, analysis.py)
│   │   │   └── routes/              # API endpoints (documents.py, analysis.py)
│   │   ├── services/
│   │   │   ├── document_service.py      # Ingestion & storage coordinator
│   │   │   ├── healthcare_classifier.py # Domain restriction classifier
│   │   │   └── summary_service.py       # 10-stage pipeline orchestrator
│   │   ├── nlp/
│   │   │   ├── extraction.py            # PDF, DOCX, TXT, URL ingestion
│   │   │   ├── cleaning.py              # Medical text normalization
│   │   │   ├── section_detection.py     # Section segmenter
│   │   │   ├── linguistic_analysis.py   # NegEx & sentence analysis
│   │   │   ├── entity_recognition.py    # Biomedical NER
│   │   │   ├── relation_extraction.py   # Predicate relation extraction
│   │   │   ├── embeddings.py            # Sentence embeddings & TF-IDF
│   │   │   ├── retrieval.py             # Semantic search & chunking
│   │   │   ├── textrank.py              # TextRank & MMR diversity
│   │   │   ├── instruction_parser.py    # Natural language instruction parser
│   │   │   └── evidence_validation.py   # Evidence grounding & citations
│   │   ├── storage/
│   │   │   └── repository.py            # Document & status store
│   │   └── tests/                       # Automated test suite (15 passing tests)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx               # Clinical branding header
│   │   │   ├── DocumentInput.tsx        # Upload, paste, URL & instruction inputs
│   │   │   ├── ProcessingProgress.tsx   # Genuine 10-stage progress monitor
│   │   │   ├── SummaryView.tsx          # Multi-tab research summary dashboard
│   │   │   └── CitationModal.tsx        # Source citation verification modal
│   │   ├── api.ts                       # Axios client
│   │   ├── types.ts                     # TypeScript definitions
│   │   ├── App.tsx                      # Root component
│   │   └── index.css                    # Tailwind CSS v4 styling
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## 🚀 Running the Project Locally

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Navigate to backend directory or workspace root
cd "d:\NLP MPR"

# Install backend dependencies
python -m pip install -r backend/requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Start FastAPI server with Uvicorn
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*The FastAPI backend and interactive OpenAPI documentation will be live at `http://127.0.0.1:8000/docs`.*

### 3. Frontend Setup
```bash
# Open a separate terminal and navigate to frontend
cd "d:\NLP MPR\frontend"

# Install dependencies
npm install

# Run Vite development server
npm run dev
```
*Open your browser and navigate to `http://localhost:5173`.*

---

## 🧪 Automated Testing

Automated tests cover all pipeline stages, positive and negative domain classifications, extraction formats, TextRank ranking, custom instruction parsing, and API error cases:

```bash
cd "d:\NLP MPR"
python -m pytest backend/app/tests/ -v
```

All 15 automated test suites pass cleanly:
- `test_api_health`
- `test_text_ingestion_and_analysis_flow`
- `test_non_healthcare_paper_rejection`
- `test_empty_or_too_short_text`
- `test_ssrf_blocked_url`
- `test_healthcare_domain_classifier_positive`
- `test_healthcare_domain_classifier_negative`
- `test_document_extraction_pdf`
- `test_document_extraction_docx`
- `test_document_extraction_txt`
- `test_text_cleaning_and_section_detection`
- `test_linguistic_analysis_negation_and_uncertainty`
- `test_biomedical_entity_recognition`
- `test_relation_extraction`
- `test_textrank_and_custom_instruction_interpretation`

---

## 🛡️ Security & Reliability

- **Healthcare-Only Filtering**: Reject non-healthcare papers before running intensive downstream pipelines.
- **SSRF Mitigation**: Outgoing requests for URL ingestion reject private and loopback subnets (`localhost`, `127.0.0.1`, `10.*`, `192.168.*`, `169.254.169.254`).
- **File Validation**: Strict file extension checking (`.pdf`, `.docx`, `.txt`) and 30MB file size quotas.
- **Evidence Grounding**: Prevents hallucination by requiring summary claims and statistics to map to extracted sentences and section identifiers.
"# NLP_MPR_7thSem" 
