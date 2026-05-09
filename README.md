<div align="center">
  <img src="https://img.icons8.com/color/96/000000/law.png" alt="Logo">
  <h1>⚖️ VakeelIt / LegalSahayak</h1>
  <p><strong>AI-Powered Legal Assistant & Drafting Engine for the Indian Legal System</strong></p>

  <p>
    <img alt="React Native" src="https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
    <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" />
    <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img alt="Docker" src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
    <img alt="MongoDB" src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" />
  </p>
</div>

---

VakeelIt bridges the gap between complex legal jargon and common users. It provides automated document analysis, case strategy generation, step-by-step legal procedures, and **court-ready automated PDF drafting**.

## ✨ Core Features

### 📝 Automated Legal Drafting & PDF Generation
- **Instant Drafting:** Generate court-ready documents like *Vakalatnamas*, Bail Applications, Legal Notices, Affidavits, and MOUs based on user input.
- **Bilingual Support:** Outputs high-quality PDFs in formal English or **Hindi (Devanagari script)** using integrated local fonts.
- **Dedicated PDF Worker:** A containerized backend worker using `WeasyPrint` handles heavy CSS layout and HTML-to-PDF rendering without blocking the main API.

### 📄 Smart Contract Analysis
- **Multi-Modal Uploads:** Upload rental agreements, corporate contracts, or notices via PDF, Image (via Tesseract OCR), or raw text.
- **Red Flag Detection:** Automatically identifies malicious clauses, hidden fees, and legal loopholes.
- **Plain English / Hinglish:** Translates dense legal jargon into an easy-to-understand summary.

### 🧑‍⚖️ Intelligent Case Strategy
- **Auto-Detection:** Upload an FIR or court order—our AI automatically detects the case type and generates a title.
- **Deep Analysis:** Generates actionable legal strategy, outlining your case's **Strengths**, **Weaknesses**, and **Loopholes**.
- **Lawyer Prep:** Prepares a list of smart, relevant questions for you to ask your advocate.

### 💬 Contextual Legal Chat
- **Follow-up Q&A:** Open any analyzed case and ask follow-up questions in a real-time chat interface.
- **Context-Aware:** The AI remembers your entire case details and previous analyses when answering.

---

## 🏗️ System Architecture

This application uses a scalable **Microservices** pattern to isolate heavy processing from fast user interactions:

1. **Frontend (`/frontend`)** 🌐
   - **Tech:** React Native & Expo Web
   - **Hosting:** **Vercel** (Edge network delivery)
2. **API Orchestrator (`/api`)** 🧠
   - **Tech:** Python, FastAPI, MongoDB (Motor), Google Gemini AI
   - **Role:** Handles Auth, Database read/writes, and AI prompting.
   - **Hosting:** **Render** (Web Service)
3. **PDF & OCR Worker (`/pdf-worker`)** 🖨️
   - **Tech:** Python, FastAPI, Docker, WeasyPrint, Tesseract-OCR
   - **Role:** Handles extreme CPU-bound tasks like rendering dynamic HTML to PDF and running image OCR.
   - **Hosting:** **Render** (Docker Container)

---

## 🚀 Upcoming Features

* **🔍 IRAC Research Tool:** A dedicated research tab that outputs landmark Supreme Court and High Court judgements in strict **I**ssue, **R**ule, **A**pplication, and **C**onclusion format.
* **🤝 Lawyer Discovery Network:** Connect with verified legal professionals. Search by specialization, read client reviews, and book consultations directly within the app.

---

## 💻 Local Development Setup

### 1. Setup the Database & Env Variables
Create an `.env` file in the `/api` directory with:
```env
MONGO_URL=your_mongodb_atlas_url
DB_NAME=vakeelit_db
JWT_SECRET=your_secret_hash
GOOGLE_API_KEY=your_gemini_api_key
```

### 2. Start the Backend (API)
```bash
cd api
pip install -r requirements.txt
uvicorn index:app --reload --port 8000
```

### 3. Start the PDF Worker
```bash
cd pdf-worker
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### 4. Start the Frontend
```bash
cd frontend
npm install
npx expo start
```

---

## ☁️ Deployment (Infrastructure as Code)
Deploying the backend services is automated via the `render.yaml` Blueprint.
1. Connect this repository to Render.
2. Select **New Blueprint**.
3. Render will automatically provision both the API and the PDF-Worker, dynamically injecting internal environment variables.

> **⚠️ Disclaimer:** VakeelIt is a legal research and drafting assistant for informational purposes only. It does not constitute legal advice. Always consult a qualified advocate for final legal decisions.
