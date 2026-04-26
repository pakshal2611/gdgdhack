# Financial Intelligence Copilot
## Team: 404 Defeat Not Found | Deloitte Hacksplosion 2026

> An AI-powered financial document analysis platform with RAG-based Q&A, automated anomaly detection, multi-sheet Excel export, and an instant demo mode.

---

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt

# Create .env from example and fill in your credentials
cp .env.example .env

uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The app will be available at **http://localhost:5173**

### Database
Create a MySQL database named `fincopilot`:
```sql
CREATE DATABASE fincopilot;
```
Tables are **auto-created** on first backend startup via `init_db()`.

---

## Demo Mode
Click **"🎯 Load Sample Data"** on the home page to instantly load 5 years of synthetic TechCorp India Ltd data (2019–2023) without uploading any file.

---

## Features

- **📄 Document Upload** — PDF, Excel (.xlsx/.xls/.csv), and image files (.png/.jpg)
- **📊 Financial Dashboard** — Revenue, profit, EBITDA charts with year-over-year growth table
- **📈 Financial Ratios** — Revenue growth, profit margin, EBITDA margin, Debt/Equity, Current ratio, 5-yr CAGR
- **🤖 AI-Powered Q&A (RAG)** — Chat with your financial data using TF-IDF retrieval + OpenRouter LLM
- **🧒 ELI15 Mode** — Simplified explanations for non-financial audiences
- **🔍 Anomaly Detection** — Automatically flags revenue spikes, margin compression, cash-flow mismatches
- **📥 Excel Export** — 5-sheet styled workbook: Cover, Raw Data, Ratios, YoY Growth, Anomaly Report
- **🎯 Demo Mode** — One-click synthetic data load for instant demonstration
- **💬 Persistent Chat History** — Full conversation stored per file in MySQL

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Database** | MySQL 8 via `mysql-connector-python` |
| **PDF Parsing** | pdfplumber, pytesseract (OCR fallback), tabula-py |
| **Data Processing** | pandas, numpy |
| **AI / RAG** | TF-IDF (scikit-learn) + OpenRouter (free LLM) |
| **Excel Export** | openpyxl |
| **Frontend** | React 18, Vite, Recharts |
| **Styling** | Plain CSS (custom design system) |

---

## .env Variables Required

```env
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-oss-120b:free
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fincopilot
DB_USER=root
DB_PASSWORD=your_password
```

Get a free OpenRouter API key at [openrouter.ai](https://openrouter.ai).

---

## Project Structure

```
gdghack/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env / .env.example
│   ├── database/
│   │   ├── db.py                # MySQL connection + schema init
│   │   └── models.py            # CRUD helpers
│   ├── routes/
│   │   ├── upload.py            # POST /api/upload
│   │   ├── analysis.py          # GET  /api/analysis/{file_id}
│   │   ├── chat.py              # POST /api/chat
│   │   ├── export.py            # GET  /api/export/{file_id}
│   │   └── demo.py              # POST /api/demo
│   ├── services/
│   │   ├── pdf_extractor.py     # Document text extraction
│   │   ├── data_cleaner.py      # Data normalisation
│   │   ├── financial_engine.py  # Ratio calculation + YoY
│   │   ├── anomaly_detector.py  # Anomaly detection
│   │   ├── rag_pipeline.py      # TF-IDF RAG + OpenRouter
│   │   └── ai_insights.py       # AI narrative generation
│   └── uploads/                 # Uploaded & exported files
└── frontend/
    ├── index.html
    ├── src/
    │   ├── App.jsx
    │   ├── pages/
    │   │   ├── UploadPage.jsx
    │   │   ├── Dashboard.jsx
    │   │   └── ChatPage.jsx
    │   ├── components/
    │   │   ├── FileUploader.jsx
    │   │   ├── Charts.jsx
    │   │   ├── RatioCards.jsx
    │   │   ├── DataTable.jsx
    │   │   ├── YoYTable.jsx
    │   │   ├── AnomalyPanel.jsx
    │   │   └── ChatBox.jsx
    │   ├── services/
    │   │   └── api.js
    │   └── styles/
    │       └── main.css
    └── package.json
```

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload and process a financial document |
| `GET` | `/api/analysis/{file_id}` | Get full analysis for a file |
| `POST` | `/api/chat` | Ask a question about a file |
| `GET` | `/api/chat/history/{file_id}` | Get chat history |
| `GET` | `/api/export/{file_id}` | Download Excel report |
| `POST` | `/api/demo` | Load synthetic demo data |
| `GET` | `/api/files` | List all uploaded files |
