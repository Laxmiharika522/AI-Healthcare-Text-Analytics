# AI Healthcare Text Analytics Platform

![Dashboard](https://raw.githubusercontent.com/Laxmiharika522/AI-Healthcare-Text-Analytics/ec6ed2ece7fd11c33a085d275f0bb9ca531771d0/DashBoard3.png)
![Dashboard](https://github.com/Laxmiharika522/AI-Healthcare-Text-Analytics/blob/3992cce0ec84e3825036270dc1595058002c847f/DashBoard2.png)

## Overview
The AI Healthcare Text Analytics Platform is a comprehensive web application designed to assist medical professionals by analyzing clinical texts, predicting disease risks, searching medical documents, and summarizing clinical reports. It integrates a powerful AI-driven backend with a modern, responsive frontend dashboard.

## Features
- **Clinical Text Analyzer**: Extract insights, entities, and sentiments from raw clinical notes.
- **Disease Risk Prediction**: Predict potential diseases based on patient symptoms using Machine Learning models (e.g., Random Forest, XGBoost).
- **Medical Document Search**: Efficiently search through medical records and research papers.
- **Clinical Report Summarization**: Generate concise summaries of lengthy clinical reports using NLP techniques (TF-IDF, LSA, LexRank).
- **Medical Research Assistant (QA)**: An intelligent Q&A system for medical queries.
- **Analytics Dashboard**: Visualize patient statistics, disease distributions, and analytics using interactive charts.
- **Patient & Notes Management**: Full CRUD operations for managing patient records and clinical notes.

## Tech Stack
### Frontend
- **Framework**: React 19 with Vite
- **Styling & UI**: Lucide React (Icons), Recharts (Data Visualization)
- **Routing & HTTP**: React Router DOM, Axios

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite
- **Machine Learning & NLP**: Scikit-Learn, XGBoost, NLTK, spaCy, Sumy
- **Utilities**: Flask-CORS, SQLAlchemy, Werkzeug

## Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- Python 3.8+
- npm or yarn

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask server:
   ```bash
   python app.py
   ```
   *The backend will automatically initialize and seed the SQLite database on startup.*
   *The server runs at `http://localhost:5000`.*

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will be accessible at the local URL provided by Vite (usually `http://localhost:5173`).*

## Project Structure
```text
.
├── backend/               # Flask API backend
│   ├── app.py             # Main application entry point
│   ├── database/          # SQLite DB and seeding scripts
│   ├── models/            # Saved ML models
│   ├── modules/           # Core AI/ML logic (NLP, prediction, search)
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/               # React components, pages, and services
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
└── README.md              # Project documentation
```

