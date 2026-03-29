# WEEK 3 - Data Extraction Scripts
# Initial Extractor for Excel files ONLY
# import pandas as pd

# def extract_excel(path: str):
#     xls = pd.ExcelFile(path)
#     sheets_output = []
#     for sheet_name in xls.sheet_names:
#         df = pd.read_excel(path, sheet_name=sheet_name, header=None)
#         df = df.fillna("").astype(str)
#         sheets_output.append({
#             "sheet_name": sheet_name,
#             "rows": df.values.tolist()
#         })

#     return sheets_output


# WEEK 3 - Data Extraction Scripts
# Now with PDF aded giving Excel + PDF (text + image + OCR) extraction

import pandas as pd
import fitz  # PyMuPDF
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"




# EXCEL EXTRACTION (original code above and unchanged)

def extract_excel(path: str):
    xls = pd.ExcelFile(path)
    sheets_output = []
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet_name, header=None)
        df = df.fillna("").astype(str)
        sheets_output.append({
            "sheet_name": sheet_name,
            "rows": df.values.tolist()
        })
    return sheets_output


# ---------------------------------------------------------
# PDF SECTION 
# various helpers

def page_has_text(page):
    text = page.get_text("text")
    return bool(text.strip())


def extract_text_from_page(page):
    return page.get_text("text")


def extract_images_from_page(page):
    images = []
    for img in page.get_images(full=True):
        xref = img[0]
        pix = fitz.Pixmap(page.parent, xref)

        # RGB or grayscale
        if pix.n < 5:
            #images.append(pix.get_pil_image()) # obsolete version replaced below
            images.append(pix.pil_image())
        else:
            # CMYK → convert to RGB
            pix = fitz.Pixmap(fitz.csRGB, pix)
            images.append(pix.get_pil_image())

    return images


def ocr_image(image):
    return pytesseract.image_to_string(image)


def parse_table_from_text(text):
    rows = []
    for line in text.split("\n"):
        cells = [c.strip() for c in line.split() if c.strip()]
        if cells:
            rows.append(cells)
    return rows



# PDF EXTRACTION
def process_pdf_page(page, page_num):
    result = {
        "page": page_num + 1,
        "text": None,
        "image_tables": []
    }

    # Look for text
    if page_has_text(page):
        result["text"] = extract_text_from_page(page)

    # look for images and OCR read them
    images = extract_images_from_page(page)
    for img in images:
        ocr_text = ocr_image(img)
        table = parse_table_from_text(ocr_text)
        if table:
            result["image_tables"].append(table)

    return result


def extract_pdf(path: str):
    doc = fitz.open(path)
    pages_output = []

    for page_num, page in enumerate(doc):
        pages_output.append(process_pdf_page(page, page_num))

    return pages_output

# ---------------------------------------------------------
# WORD SECTION 

# Text and paragraphs section
from docx import Document
import base64
import io

def pil_image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def extract_docx_text(doc):
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

#Tables section
def extract_docx_tables(doc):
    tables_output = []

    for table in doc.tables:
        table_data = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            table_data.append(cells)
        tables_output.append(table_data)

    return tables_output

# Images section
import zipfile
from PIL import Image
import io

def extract_docx_images(file_path):
    images = []

    with zipfile.ZipFile(file_path, 'r') as docx_zip:
        for file in docx_zip.namelist():
            if file.startswith("word/media/"):
                image_data = docx_zip.read(file)
                image = Image.open(io.BytesIO(image_data))
                #images.append(image)
                images.append(pil_image_to_base64(image)) 

    return images

# merge all word part results
def extract_docx(file_path):
    doc = Document(file_path)

    text = extract_docx_text(doc)
    tables = extract_docx_tables(doc)
    images = extract_docx_images(file_path)

    return {
        "text": text,
        "tables": tables,
        "images": images
    }

