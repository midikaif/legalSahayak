# ⚖️ LegalSahayak - AI-Powered Legal Assistant

An intelligent, cross-platform legal tech application built specifically for the **Indian Legal System**. LegalSahayak bridges the gap between complex legal jargon and common users by providing automated document analysis, case strategy generation, and step-by-step legal procedures.

---

## ✨ Current Features

### 📄 Smart Contract Analysis
- **Multi-Modal Uploads:** Upload rental agreements, corporate contracts, or notices via PDF, Image (OCR), or raw text.
- **Red Flag Detection:** Automatically identifies malicious clauses, hidden fees, and legal loopholes.
- **Plain English / Hinglish:** Translates dense legal jargon into an easy-to-understand summary.
- **Legal Dictionary:** Extracts complex terms and provides simple definitions.

### 🧑‍⚖️ Intelligent Case Strategy
- **Auto-Detection:** Upload an FIR or court order—our AI automatically detects the case type (Civil, Criminal, Property, etc.) and generates a title.
- **Deep Analysis:** Generates actionable legal strategy, outlining your case's **Strengths**, **Weaknesses**, and **Loopholes**.
- **Lawyer Prep:** Prepares a list of smart, relevant questions for you to ask your advocate.

### 💬 Contextual Legal Chat
- **Follow-up Q&A:** Open any analyzed case and ask follow-up questions in a real-time chat interface.
- **Context-Aware:** The AI remembers your entire case details and previous analyses when answering.

### 📜 Step-by-Step Procedures
- Select a case type (e.g., Civil, Family, Consumer) to get a comprehensive timeline.
- Includes required documents, court hierarchy, and estimated timeframes.

### 🇮🇳 Built for India
- Heavily instructed with an Indian legal persona (IPC, CrPC, Indian Contract Act 1872).
- **Bilingual Support:** Generate any analysis or procedure in English or conversational **Hinglish**.

---

## 🚀 Upcoming Features

* **📝 Automated Legal Drafting:** Instantly generate formatted *Vakalatnamas*, Bail Applications, Legal Notices, and Affidavits based on user input.
* **🔍 IRAC Research Tool:** A dedicated research tab that outputs landmark Supreme Court and High Court judgements in strict **I**ssue, **R**ule, **A**pplication, and **C**onclusion format.
* **🤝 Lawyer Discovery Network:** Connect with verified legal professionals. Search by specialization, read client reviews, and book consultations directly within the app.

---

## 🛠️ Tech Stack

**Frontend (Mobile & Web)**
- React Native & Expo Router
- TypeScript
- Expo Document & Image Picker

**Backend (API & AI)**
- Python & FastAPI (Async Architecture)
- Google Gemini 2.5 Flash API (LLM)
- PyPDF2 & Tesseract OCR (Document Ingestion)
- MongoDB & Motor (Async Database)
- JWT Auth & bcrypt (Security)

---

## 💻 Getting Started

### 1. Start the Backend
Ensure your Python environment is set up and MongoDB is running.
```bash
cd api
pip install -r requirements.txt
uvicorn index:app --reload --port 8000
```

### 2. Start the Frontend
Ensure you have Node.js installed.
```bash
cd frontend
npm install
npx expo start
```

> **Disclaimer:** LegalSahayak is a legal research and drafting assistant for informational purposes only. It does not constitute legal advice. Always consult a qualified advocate for final legal decisions.
