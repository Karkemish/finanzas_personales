import pdfplumber
from config.settings import PDF_PASSWORD, INPUTS_DIR

def extract_text_from_pdf(name_pdf: str) -> str:
    pdf_path = INPUTS_DIR / name_pdf
    all_text = ""
    try:
        with pdfplumber.open(pdf_path, password=PDF_PASSWORD) as pdf:
            print(f"✅ PDF opened: {len(pdf.pages)} pages\n")
            for i, page in enumerate(pdf.pages):
                print(f"📄 Extracting text from page {i + 1}...")
                text = page.extract_text(layout=True)
                if text:
                    print(f"✅ Text extracted from page {i + 1}")
                    all_text += text + "\n"
                else:
                    print(f"⚠️ No text found on page {i + 1}")
        return all_text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""