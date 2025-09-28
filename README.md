# Digital Evidence Manager

**Digital Evidence Manager** is a secure platform designed to track, store, and manage digital evidence efficiently. It provides authorized personnel with a reliable and organized way to handle sensitive digital files while maintaining integrity and accountability.

## Features
- Secure Login: Users authenticate with hashed passwords (PBKDF2) for enhanced security.
- Evidence Management: Upload, view, and organize digital evidence by case.
- Access Control: Only authorized staff can download or manage files.
- PDF Report Generation: Automatically generate downloadable reports for cases.
- File Storage: Centralized storage for all uploaded evidence.

## Technology Stack
- Backend: Python, FastAPI
- Database: SQLite
- Frontend: HTML, CSS templates
- Reporting: FPDF for PDF generation
- Version Control: Git & GitHub

## Installation & Usage
Clone the repository and run the application locally:

```bash
git clone https://github.com/JosephKizito254/DigitalEvidenceManager.git
cd DigitalEvidenceManager
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
