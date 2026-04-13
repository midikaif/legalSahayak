# LegalSahayak - Product Requirements Document

## Overview
LegalSahayak is a mobile app that simplifies legal contracts, provides case analysis, step-by-step legal procedures, and connects users with lawyers. Focused on the Indian legal system.

## User Types
1. **Common User** - People seeking legal help and guidance
2. **Lawyer** - Legal professionals offering services

## Core Features

### 1. Authentication
- Registration with email/password
- User type selection (Common User / Lawyer)
- Lawyer-specific fields: specialization, bar council number, experience, location, bio
- JWT-based authentication with 30-day token expiry

### 2. Contract Analysis
- Upload contracts via text input, PDF, or image
- AI-powered simplification using Gemini 2.5 Flash
- Key points extraction, risk identification
- Legal terms explained in plain language
- Analysis history per user

### 3. Case Analysis
- Input case title, type, and description
- AI analysis of strengths and weaknesses
- Legal strategy recommendations
- Questions to ask lawyers
- Loophole identification
- Case history tracking

### 4. Legal Procedure Guide
- Step-by-step procedures for different case types
- Required documents checklist
- Court hierarchy information
- Timeline estimations

### 5. Lawyer Finder
- Search by specialization and location
- Detailed lawyer profiles
- Contact information

### 6. Profile Management
- View/edit profile information
- Logout functionality

## Tech Stack
- **Frontend**: React Native (Expo Router)
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI**: Gemini 2.5 Flash via Emergent LLM Key
- **Auth**: JWT + bcrypt

## API Endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/contract/analyze
- GET /api/contract/history/{user_id}
- POST /api/case/analyze
- GET /api/case/history/{user_id}
- GET /api/procedure/{case_type}
- GET /api/lawyers/search
- GET /api/lawyer/{lawyer_id}
- GET /api/health

## Business Enhancement Ideas
- **Premium tier**: Offer unlimited AI analyses for a monthly subscription
- **Lawyer verification badges**: Verified lawyers get more visibility
- **Case outcome predictions**: AI-powered win probability estimates
- **Document templates**: Pre-built legal document templates
