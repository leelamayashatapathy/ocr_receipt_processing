# Receipt Processing API

A Django REST API for uploading, validating, and extracting information from receipt PDFs using Tesseract OCR.

## Features

- Upload PDF receipts
- Validate PDF files
- Extract merchant name, date, and total amount using Tesseract OCR
- List and retrieve processed receipts
- Duplicate file detection by hash and name
- Handles multi-page PDFs
- Returns detailed error messages for invalid or corrupt files

## Requirements

- Python 3.8+
- [Poppler](http://blog.alivate.com.au/poppler-windows/) (for PDF to image conversion)
- Tesseract OCR (install from https://github.com/tesseract-ocr/tesseract)
- The following Python packages (see `requirements.txt`):

  ```
  Django
  djangorestframework
  pdf2image
  pillow
  pytesseract
  python-dotenv
  PyMuPDF
  ```

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/leelamayashatapathy/ocr_receipt_processing.git
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Install Poppler and Tesseract:**
   - Download and install Poppler for your OS.
   - Download and install Tesseract for your OS.
   - Make sure both are in your system PATH, or update the code to point to their locations (see `poppler_path` in the code).

5. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```

6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```

## API Endpoints

- `POST /upload/` — Upload a PDF receipt
- `POST /validate/` — Validate a receipt file
- `POST /process/` — Extract data from a receipt using Tesseract
- `GET /receipts/` — List all processed receipts
- `GET /receipts/<id>/` — Get details of a specific receipt

### Example: Upload and Process a Receipt

1. **Upload a PDF:**
   ```sh
   POST "file=@your_receipt.pdf" http://127.0.0.1:8000/upload/
   ```
   Response will include a `file_id`.

2. **Validate the PDF:**
   ```sh
   POST "Content-Type: application/json" -d '{"file_id": 1}' http://127.0.0.1:8000/validate/
   ```

3. **Process the PDF:**
   ```sh
   POST "Content-Type: application/json" -d '{"file_id": 1}' http://127.0.0.1:8000/process/
   ```

4. **List all receipts:**
   ```sh
   GET   http://127.0.0.1:8000/receipts/
   ```

## Troubleshooting

- **Poppler or Tesseract not found:**
  - Ensure both are installed and their paths are correctly set in your system or in the code.
- **PDF not processing:**
  - Check that the file is a valid PDF and not corrupted.
- **Tesseract accuracy:**
  - OCR results depend on scan quality. Try to use high-resolution scans for best results.

## Notes

- Make sure the `MEDIA_ROOT` directory is writable for file uploads.
- The API expects PDF files for upload.
- Tesseract and Poppler must be installed and accessible for OCR and PDF conversion.
- You can customize the `poppler_path` in the code if Poppler is not in your PATH.
