import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import TextAnalyzer from './pages/TextAnalyzer';
import DiseasePredictor from './pages/DiseasePredictor';
import DocumentSearch from './pages/DocumentSearch';
import ReportSummarizer from './pages/ReportSummarizer';
import ResearchAssistant from './pages/ResearchAssistant';
import Patients from './pages/Patients';
import './index.css';

export default function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<AnalyticsDashboard />} />
            <Route path="/analyzer" element={<TextAnalyzer />} />
            <Route path="/predictor" element={<DiseasePredictor />} />
            <Route path="/search" element={<DocumentSearch />} />
            <Route path="/summarizer" element={<ReportSummarizer />} />
            <Route path="/assistant" element={<ResearchAssistant />} />
            <Route path="/patients" element={<Patients />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
