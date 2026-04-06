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
import os # row added for metadata week 4
import time # row added for metadata week 4
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# EXCEL EXTRACTION (original code above and unchanged)

def extract_excel(path: str):
    start = time.time() # row added for metadata week 4
    xls = pd.ExcelFile(path)
    sheets_output = []
    rows_per_sheet = {}  # week 4 row added for metadata 
    columns_per_sheet = {}  # week 4 row added for metadata
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet_name, header=None)
        df = df.fillna("").astype(str)
        rows_per_sheet[sheet_name] = df.shape[0]  # week 4 row added for metadata
        columns_per_sheet[sheet_name] = df.shape[1]  # week 4 row added for metadata
        sheets_output.append({
            "sheet_name": sheet_name,
            "rows": df.values.tolist()
        })
    
    # week 5 metadata section
    metadata = {
        "sheet_count": len(xls.sheet_names),
        "rows_per_sheet": rows_per_sheet,
        "columns_per_sheet": columns_per_sheet,
        "file_size_kb": os.path.getsize(path) / 1024,
        "extraction_time_ms": int((time.time() - start) * 1000)
    }

    #return sheets_output
    # Week 4 modif
    return {
        "tables": sheets_output,
        "metadata": metadata
    }



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
    start = time.time() # Week 4 modif for metadata
    doc = fitz.open(path)
    pages_output = []

    # Week 4 modif
    total_tables = 0
    total_images = 0
    ocr_used = False

    for page_num, page in enumerate(doc):
        #pages_output.append(process_pdf_page(page, page_num))

        # Weeek 4 modifications for Metadata
        page_result = process_pdf_page(page, page_num)
        pages_output.append(page_result)
        # wook 4 - Count tables extracted from OCR
        total_tables += len(page_result.get("image_tables", []))
        # week 4 - Count images processed for meta
        images = extract_images_from_page(page) # week 4  correction due to error during testing
        total_images += len(images)
        # week 4  - If any OCR text was used note it down
        if len(images) > 0:
            ocr_used = True

    metadata = {
        "page_count": len(doc),
        "table_count": total_tables,
        "image_count": total_images,
        "ocr_used": ocr_used,
        "file_size_kb": os.path.getsize(path) / 1024,
        "extraction_time_ms": int((time.time() - start) * 1000)
    }

    return {
        "pages": pages_output,
        "metadata": metadata
    }
    #return pages_output


# --------------------------------------------------------------
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
    start = time.time() # added week 4 for meta data
    doc = Document(file_path)

    text = extract_docx_text(doc)
    tables = extract_docx_tables(doc)
    images = extract_docx_images(file_path)

    # Week 4 - Building  metadata
    metadata = {
        "paragraph_count": len(doc.paragraphs),
        "table_count": len(doc.tables),
        "image_count": len(images),
        "file_size_kb": os.path.getsize(file_path) / 1024,
        "extraction_time_ms": int((time.time() - start) * 1000)
    }


    return {
        "text": text,
        "tables": tables,
        "images": images,
        "metadata": metadata # week 4 meta data additional row
    }


