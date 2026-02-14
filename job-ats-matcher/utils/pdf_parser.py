
import PyPDF2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path):

    try:
        text = ""
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            logger.info(f"Processing {num_pages} pages")
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        logger.info(f"Extracted {len(text)} characters")
        return text
    
    except FileNotFoundError:
        logger.error(f"File not found")
        return ""
    except Exception as e:
        logger.error(f"Error {e}")
        return ""


def clean_text(text):

    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = ' '.join(text.split())
    
    return text


if __name__ == "__main__":
    # Test with a sample PDF
    import os
    
    pdf_path = "data/resume.pdf"
    
    if os.path.exists(pdf_path):
        print(f"Testing PDF extraction")
        text = extract_text_from_pdf(pdf_path)
        cleaned = clean_text(text)
        
        print(f"\nExtracted text (first 500 chars):")
        print(cleaned[:500])
    else:
        print(f"No test PDF found")