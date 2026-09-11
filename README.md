# 🎯 AI Interview Question Generator

> A production-ready, full-stack AI platform that generates customized technical & behavioral interview questions, model answers, hints, and downloadable PDF question packs.

---

## 🌟 Overview

The **AI Interview Question Generator** is an interactive web application built for candidates, recruiters, and hiring managers. It leverages OpenAI's language models (`gpt-3.5-turbo`) to create tailored interview question sets based on specific job roles, skills, experience levels, and difficulty.

The system features a **dual-layer architecture**:
- **AI & Mock Generation**: Connects to OpenAI when an API key is available, or automatically switches to a structured local mock generator.
- **Supabase Cloud & SQLite Fallback**: Syncs data to a cloud Supabase PostgreSQL database when configured, or transparently uses a local SQLite database (`local_interview.db`).

---

## ✨ Features

- **🤖 AI Question Generation**: Generates role-specific questions, ideal answers, hints, and difficulty ratings.
- **⚡ Smart Local Fallbacks**: Works out-of-the-box locally without requiring active API keys or external services.
- **🔐 JWT Authentication**: Complete signup, login, session persistence, and protected routes.
- **📄 Professional PDF Export**: One-click generation and download of formatted interview packs via ReportLab / jsPDF.
- **📊 History & Practice Mode**: Review previously generated interview sets, submit practice answers, and receive evaluation feedback.
- **🎨 Glassmorphism UI**: High-contrast, dark-themed responsive interface powered by React 19 and Tailwind CSS.

---

## 🛠️ Technology Stack

| Layer | Component | Technologies |
| :--- | :--- | :--- |
| **Frontend** | Single Page App | React 19, Vite, Tailwind CSS, Axios, React Router v6, Lucide Icons, jsPDF |
| **Backend** | REST API Service | FastAPI, Python 3.12, Uvicorn, Pydantic v2, PyJWT, ReportLab |
| **Database** | Primary / Fallback | Supabase PostgreSQL (Cloud) / SQLite 3 (Local Runtime) |
| **AI Engine** | AI Question Service| OpenAI API (`gpt-3.5-turbo`) |

---

## 📁 Repository Structure

```
AI-Interview-Question-Generator/
├── backend/
│   ├── app/
│   │   ├── config/          # Application settings & environment loader
│   │   ├── middleware/      # Auth & Security verification middleware
│   │   ├── routes/          # Auth, Questions, Answers, History API routes
│   │   ├── schemas/         # Pydantic data validation models
│   │   ├── services/        # OpenAI, Supabase, PDF Services
│   │   └── utils/           # Password hashing & helper functions
│   ├── .env                 # Backend environment variables
│   ├── main.py              # FastAPI application entrypoint
│   └── requirements.txt     # Python backend dependencies
├── frontend/
│   ├── public/              # Static assets & favicon
│   ├── src/
│   │   ├── components/      # UI components (Navbar, Sidebar, QuestionCard, Footer)
│   │   ├── context/         # AuthContext Provider
│   │   ├── hooks/           # Custom React hooks (useAuth)
│   │   ├── pages/           # Dashboard, History, Results, Login, Register
│   │   ├── services/        # API Client & Supabase SDK integrations
│   │   ├── utils/           # PDF Export & Validators
│   │   ├── App.jsx          # Router & Layout wrapper
│   │   └── main.jsx         # React DOM entrypoint
│   ├── package.json         # Frontend npm dependencies
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── vite.config.js       # Vite development configuration
├── schema.sql               # Supabase PostgreSQL database tables definition
├── vercel.json              # Vercel deployment configuration
└── README.md                # Master documentation
```

---

## 🔑 Default Test Credentials

When running in local SQLite mode (default startup without Supabase credentials), the database is automatically pre-seeded with test admin credentials:

- **Email / Username**: `admin@interview.ai`
- **Password**: `adminpassword`

*(You can also click **Create Account** on the login page to register new accounts).*

---

## ⚙️ Environment Configuration

Environment settings are loaded from [backend/.env](file:///c:/Users/balar/OneDrive/ドキュメント/AI-Interview-Question-Generator/backend/.env):

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Supabase Configuration (Optional - falls back to local SQLite if empty)
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key

# JWT Auth Secret
LOCAL_JWT_SECRET=super-secret-local-key
```

---

## 🏁 Quick Start Guide

### 1. Launch Backend Server

```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```
- **Backend API**: `http://localhost:8000`
- **Interactive Swagger API Docs**: `http://localhost:8000/docs`

### 2. Launch Frontend Application

In a **second terminal window**:
```powershell
cd frontend
npm.cmd run dev
```
- **Frontend App**: `http://localhost:5173`

---

## 📡 API Endpoints Overview

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `POST` | `/api/auth/register` | Register a new user account |
| **Auth** | `POST` | `/api/auth/login` | Authenticate user & return JWT token |
| **Auth** | `GET` | `/api/auth/me` | Fetch authenticated user profile |
| **Questions** | `POST` | `/api/questions/generate` | Generate customized question set |
| **Questions** | `GET` | `/api/questions/set/{set_id}` | Get specific question set details |
| **History** | `GET` | `/api/history/` | Fetch user's saved interview sets |
| **History** | `DELETE` | `/api/history/{set_id}` | Delete an interview set |
| **Answers** | `POST` | `/api/answers/evaluate` | Grade user answer and provide feedback |

---

## 🗄️ Database Setup (Supabase PostgreSQL)

To use Supabase Cloud as your remote database:
1. Create a project at [supabase.com](https://supabase.com).
2. Open the **SQL Editor** in Supabase and run the commands in [schema.sql](file:///c:/Users/balar/OneDrive/ドキュメント/AI-Interview-Question-Generator/schema.sql).
3. Add your `SUPABASE_URL` and `SUPABASE_KEY` to [backend/.env](file:///c:/Users/balar/OneDrive/ドキュメント/AI-Interview-Question-Generator/backend/.env).

---

## 📝 License

This project is licensed under the MIT License.
