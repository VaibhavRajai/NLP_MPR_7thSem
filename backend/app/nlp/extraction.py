import os
import re
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from docx import Document as DocxDocument
import requests
from bs4 import BeautifulSoup
from backend.app.core.logging import logger

class ExtractionBlock:
    def __init__(self, text: str, page: int, block_id: int, block_type: str = "paragraph"):
        self.text = text
        self.page = page
        self.block_id = block_id
        self.block_type = block_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "page": self.page,
            "block_id": self.block_id,
            "block_type": self.block_type
        }

class DocumentExtractor:
    @staticmethod
    def extract_from_pdf(file_path: str) -> List[Dict[str, Any]]:
        blocks = []
        block_counter = 0
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Extract text blocks with layout preservation
                page_blocks = page.get_text("blocks")
                for b in page_blocks:
                    # b: (x0, y0, x1, y1, text, block_no, block_type)
                    text = b[4].strip()
                    if text:
                        block_counter += 1
                        blocks.append(ExtractionBlock(
                            text=text,
                            page=page_num + 1,
                            block_id=block_counter,
                            block_type="paragraph"
                        ).to_dict())
            doc.close()
        except Exception as e:
            logger.error(f"Error extracting PDF with fitz: {e}")
            raise ValueError(f"Failed to extract PDF content: {str(e)}")
            
        # OCR fallback if virtually no text was extracted (e.g., scanned PDF)
        if len(blocks) == 0 or sum(len(b["text"]) for b in blocks) < 100:
            try:
                import pytesseract
                from PIL import Image
                import io
                doc = fitz.open(file_path)
                ocr_blocks = []
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(dpi=150)
                    img = Image.open(io.BytesIO(pix.tobytes("png")))
                    ocr_text = pytesseract.image_to_string(img).strip()
                    if ocr_text:
                        block_counter += 1
                        ocr_blocks.append(ExtractionBlock(
                            text=ocr_text,
                            page=page_num + 1,
                            block_id=block_counter,
                            block_type="ocr_text"
                        ).to_dict())
                doc.close()
                if ocr_blocks:
                    return ocr_blocks
            except Exception as ocr_err:
                logger.warning(f"OCR fallback was not possible or failed: {ocr_err}")

        return blocks

    @staticmethod
    def extract_from_docx(file_path: str) -> List[Dict[str, Any]]:
        blocks = []
        block_counter = 0
        try:
            doc = DocxDocument(file_path)
            current_page = 1
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    block_counter += 1
                    # Rough page estimation if page breaks occur
                    blocks.append(ExtractionBlock(
                        text=text,
                        page=current_page,
                        block_id=block_counter,
                        block_type="heading" if para.style.name.startswith("Heading") else "paragraph"
                    ).to_dict())
            # Also extract tables if present
            for table in doc.tables:
                table_text_rows = []
                for row in table.rows:
                    row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                    if row_text:
                        table_text_rows.append(row_text)
                if table_text_rows:
                    block_counter += 1
                    blocks.append(ExtractionBlock(
                        text="\n".join(table_text_rows),
                        page=current_page,
                        block_id=block_counter,
                        block_type="table"
                    ).to_dict())
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise ValueError(f"Failed to extract DOCX content: {str(e)}")
        return blocks

    @staticmethod
    def extract_from_txt(content: str) -> List[Dict[str, Any]]:
        blocks = []
        raw_paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if not raw_paragraphs:
            raw_paragraphs = [line.strip() for line in content.split("\n") if line.strip()]
            
        for idx, para in enumerate(raw_paragraphs):
            blocks.append(ExtractionBlock(
                text=para,
                page=1 + (idx // 10),  # Rough virtual pagination
                block_id=idx + 1,
                block_type="paragraph"
            ).to_dict())
        return blocks

    @staticmethod
    def extract_from_url(url: str) -> List[Dict[str, Any]]:
        # SSRF mitigation: disallow local/private IP ranges
        lower_url = url.lower()
        if any(h in lower_url for h in ["localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "internal", "192.168.", "10."]):
            raise ValueError("URL host is restricted for security reasons.")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HealthcareResearchSummarizer/1.0"}
            resp = requests.get(url, headers=headers, timeout=12)
            resp.raise_for_status()
            
            content_type = resp.headers.get("Content-Type", "")
            if "pdf" in content_type or url.endswith(".pdf"):
                temp_pdf = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "temp_web.pdf")
                with open(temp_pdf, "wb") as f:
                    f.write(resp.content)
                result = DocumentExtractor.extract_from_pdf(temp_pdf)
                if os.path.exists(temp_pdf):
                    os.remove(temp_pdf)
                return result

            # Parse HTML
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove scripts, styles, nav, footer
            for el in soup(["script", "style", "nav", "footer", "header", "aside"]):
                el.decompose()

            # Target main article or body
            article = soup.find("article") or soup.find("main") or soup.body
            paragraphs = []
            if article:
                for el in article.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
                    text = el.get_text().strip()
                    if len(text) > 20:
                        paragraphs.append(text)
            
            if not paragraphs:
                paragraphs = [p.get_text().strip() for p in soup.find_all("p") if len(p.get_text().strip()) > 20]
                
            blocks = []
            for idx, p in enumerate(paragraphs):
                blocks.append(ExtractionBlock(
                    text=p,
                    page=1 + (idx // 8),
                    block_id=idx + 1,
                    block_type="web_content"
                ).to_dict())
            return blocks
        except Exception as e:
            logger.error(f"Error fetching/extracting URL {url}: {e}")
            raise ValueError(f"Could not extract content from URL: {str(e)}")
