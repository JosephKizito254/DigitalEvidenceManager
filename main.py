import os
import json
import sqlite3
from datetime import datetime
from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fpdf import FPDF
import uvicorn

# ---------------------------
# Setup
# ---------------------------
app = FastAPI()
UPLOAD_DIR = "uploads"
DB_FILE = "evidence.db"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------
# Database setup
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT,
                    description TEXT,
                    filename TEXT,
                    staff_name TEXT,
                    uploaded_at TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# Save uploaded evidence
# ---------------------------
@app.post("/upload")
async def upload(
    file: UploadFile,
    case_id: str = Form(...),
    description: str = Form(...),
    staff_name: str = Form(...)
):
    # Ensure filename is valid (not None)
    filename = file.filename or f"unnamed_{datetime.now().timestamp()}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(await file.read())

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO evidence (case_id, description, filename, staff_name, uploaded_at) VALUES (?,?,?,?,?)",
              (case_id, description, filename, staff_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return {"status": "ok"}

# ---------------------------
# Generate PDF
# ---------------------------
@app.get("/report")
async def report():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT case_id, description, filename, staff_name, uploaded_at FROM evidence")
    rows = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Digital Evidence Report", ln=True, align="C")

    pdf.set_font("Arial", size=12)
    for row in rows:
        case_id, desc, filename, staff, uploaded_at = row
        pdf.multi_cell(0, 10, f"Case ID: {case_id}\nDescription: {desc}\nFile: {filename}\nUploaded By: {staff}\nUploaded At: {uploaded_at}\n{'-'*50}")

    report_file = "Evidence_Report.pdf"
    pdf.output(report_file)
    return FileResponse(report_file, media_type="application/pdf", filename=report_file)

# ---------------------------
# HTML Interface
# ---------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, case_id, description, filename, staff_name, uploaded_at FROM evidence ORDER BY uploaded_at DESC")
    evidence = c.fetchall()
    conn.close()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Digital Evidence Manager</title>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: radial-gradient(circle at top left, #0a0f1a, #000);
                color: #f5f5f5;
                height: 100vh;
                overflow-x: hidden;
            }}
            h1 {{
                text-align: center;
                padding: 20px;
                color: #00e6ff;
                text-shadow: 0 0 10px #00e6ff;
            }}
            .container {{
                width: 90%;
                margin: auto;
            }}
            .upload-box {{
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 30px;
                box-shadow: 0 0 15px rgba(0, 230, 255, 0.3);
                transition: transform 0.3s ease;
            }}
            .upload-box:hover {{
                transform: scale(1.02);
            }}
            input, button {{
                padding: 10px;
                margin: 5px;
                border-radius: 8px;
                border: none;
                outline: none;
            }}
            button {{
                background: #00e6ff;
                color: #000;
                font-weight: bold;
                cursor: pointer;
                transition: 0.3s;
            }}
            button:hover {{
                background: #0099cc;
                color: #fff;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                border-bottom: 1px solid #333;
                text-align: left;
            }}
            th {{
                color: #00e6ff;
            }}
            tr:hover {{
                background: rgba(0, 230, 255, 0.1);
            }}
            .search-box {{
                margin: 20px 0;
                text-align: center;
            }}
            .search-box input {{
                width: 50%;
                padding: 12px;
            }}
        </style>
    </head>
    <body>
        <h1>🔍 Digital Evidence Manager</h1>
        <div class="container">
            <div class="upload-box">
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="text" name="case_id" placeholder="Case ID" required>
                    <input type="text" name="description" placeholder="Description" required>
                    <input type="text" name="staff_name" placeholder="Staff Name" required>
                    <input type="file" name="file" required>
                    <button type="submit">Upload Evidence</button>
                </form>
            </div>
            <div class="search-box">
                <input type="text" id="search" placeholder="Filter evidence...">
                <button onclick="window.location.href='/report'">Generate PDF Report</button>
            </div>
            <table id="evidenceTable">
                <thead>
                    <tr>
                        <th>Case ID</th>
                        <th>Description</th>
                        <th>File</th>
                        <th>Staff</th>
                        <th>Uploaded At</th>
                    </tr>
                </thead>
                <tbody>
    """
    for ev in evidence:
        _, case_id, desc, filename, staff, uploaded_at = ev
        html += f"<tr><td>{case_id}</td><td>{desc}</td><td>{filename}</td><td>{staff}</td><td>{uploaded_at}</td></tr>"

    html += """
                </tbody>
            </table>
        </div>
        <script>
            const search = document.getElementById('search');
            search.addEventListener('keyup', function() {
                let filter = search.value.toLowerCase();
                let rows = document.querySelectorAll("#evidenceTable tbody tr");
                rows.forEach(row => {
                    row.style.display = row.innerText.toLowerCase().includes(filter) ? "" : "none";
                });
            });

            document.addEventListener("mousemove", e => {
                document.body.style.background = `radial-gradient(circle at ${e.clientX}px ${e.clientY}px, #0a0f1a, #000)`;
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# ---------------------------
# Run server
# ---------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
