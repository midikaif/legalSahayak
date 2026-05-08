# Project Memory - LegalSahayak

## PDF Generation
- Migrated `pdf-worker` from `xhtml2pdf` to `ReportLab` for better Hindi (Devanagari) support.
- Using `Mukta` font family for both English and Hindi text.
- Font files are stored in `pdf-worker/assets/fonts/`.
- ReportLab implementation provides more professional legal formatting with headers, footers, and proper justification.

## Backend API
- All core endpoints verified (Auth, Lawyers, History).
- Added `/api/draft/generate` to the comprehensive test suite.
- Fixed singular vs plural in lawyer search endpoints (`/api/lawyer/search`).

## Known Issues
- Gemini AI service (version 2.5 Flash) intermittently returns 503 during high demand periods.
- Current tests may fail AI-dependent steps if quota or service availability is low.
