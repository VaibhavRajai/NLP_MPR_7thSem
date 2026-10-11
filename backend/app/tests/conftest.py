import pytest
import os
import fitz
from docx import Document as DocxDocument

SYNTHETIC_HEALTHCARE_PAPER = """
CLINICAL TRIAL REPORT: EVALUATION OF SEMAGLUTIDE IN PATIENTS WITH TYPE 2 DIABETES AND HYPERTENSION

ABSTRACT
Background: Type 2 diabetes is a major metabolic disease often complicated by hypertension. We investigated the clinical efficacy of once-weekly semaglutide.
Methods: We conducted a double-blind, randomized controlled trial involving N = 1,200 adult patients across 14 hospital centers including Massachusetts General Hospital and Mayo Clinic. Patients received either 1.0 mg semaglutide or placebo.
Results: Semaglutide significantly reduced HbA1c levels compared to placebo (mean reduction -1.4%, p < 0.001, 95% CI 1.2-1.6). Hazard ratio for major cardiovascular events was HR = 0.74 (95% CI 0.58-0.94, p = 0.012). No evidence of severe pancreatitis was observed.
Conclusion: Semaglutide demonstrated superior glycemic control and reduced cardiovascular outcomes in patients with diabetes.

INTRODUCTION
Diabetes mellitus continues to be a leading cause of cardiovascular mortality worldwide. Although metformin is frequently prescribed as first-line therapy, adjunctive treatments are urgently needed.

OBJECTIVES
The primary aim of this multicenter clinical trial was to assess glycemic control and long-term cardiovascular safety in diabetic cohorts.

METHODS
Between January 2023 and December 2024, 1,200 participants aged 18 to 75 years were enrolled. Continuous glucose monitors (CGM) were used to record glucose fluctuations. Statistical analysis was performed using Kaplan-Meier survival curves and Cox proportional hazards models.

RESULTS
A total of 600 patients received semaglutide and 600 received placebo. The semaglutide cohort achieved a median HbA1c reduction of 1.4% (p < 0.001). Serious adverse events were reported in 4.2% of semaglutide patients vs 5.1% of placebo recipients. Troponin I biomarkers showed a downward trend.

DISCUSSION
These findings indicate that GLP-1 receptor agonists offer robust dual-action cardioprotective and glycemic benefits.

LIMITATIONS
The follow-up duration was limited to 18 months, which may restrict assessment of ultra-long-term renal outcomes. The trial was predominantly conducted in urban tertiary healthcare institutions.

CONCLUSION
Semaglutide 1.0 mg provides clinically meaningful reductions in HbA1c and reduces cardiovascular risk in patients with type 2 diabetes.
"""

SYNTHETIC_NON_HEALTHCARE_PAPER = """
A COMPARATIVE STUDY ON COMPILER OPTIMIZATION TECHNIQUES FOR DISTRIBUTED BITCOIN MINING NETWORKS

ABSTRACT
Decentralized blockchain algorithms require high-throughput compiler optimizations. In this paper, we evaluate LLVM intermediate representations for GPU cryptocurrency miners and proof-of-work hash calculations.
Results show a 14% improvement in SHA-256 block hashing throughput.
"""

@pytest.fixture
def synthetic_paper_text():
    return SYNTHETIC_HEALTHCARE_PAPER

@pytest.fixture
def non_healthcare_text():
    return SYNTHETIC_NON_HEALTHCARE_PAPER

@pytest.fixture
def temp_sample_pdf(tmp_path):
    pdf_path = str(tmp_path / "sample_cardio_trial.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), SYNTHETIC_HEALTHCARE_PAPER)
    doc.save(pdf_path)
    doc.close()
    return pdf_path

@pytest.fixture
def temp_sample_docx(tmp_path):
    docx_path = str(tmp_path / "sample_cardio_trial.docx")
    doc = DocxDocument()
    for para in SYNTHETIC_HEALTHCARE_PAPER.split("\n\n"):
        if para.strip():
            doc.add_paragraph(para.strip())
    doc.save(docx_path)
    return docx_path
