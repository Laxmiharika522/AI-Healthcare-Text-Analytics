import React, { useState } from 'react';
import axios from 'axios';
import { HelpCircle, Send, BookOpen, FileText, Database } from 'lucide-react';
import Header from '../components/Header';

const API = 'http://localhost:5000/api';

const SAMPLE_QUESTIONS = [
  'What are the symptoms of pneumonia?',
  'How is diabetes mellitus treated?',
  'What drugs are used for hypertension?',
  'What is deep learning in medical imaging?',
  'What is the treatment for sepsis?',
];

const SOURCE_ICONS = {
  'Research Paper': <BookOpen size={14} color="#8b5cf6" />,
  'Clinical Note': <FileText size={14} color="#00d4ff" />,
  'Disease Database': <Database size={14} color="#10b981" />,
};
const SOURCE_BADGE = {
  'Research Paper': 'badge-paper',
  'Clinical Note': 'badge-note',
  'Disease Database': 'badge-disease',
};

export default function ResearchAssistant() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState('');

  const ask = async (q = question) => {
    if (!q.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await axios.post(`${API}/qa`, { question: q, top_k: 6 });
      setResult(res.data);
      setHistory(prev => [{ q, answers: res.data.answers?.length || 0, ts: new Date().toLocaleTimeString() }, ...prev.slice(0, 4)]);
    } catch (e) {
      setError(e.response?.data?.error || 'QA failed. Is the backend running?');
    } finally { setLoading(false); }
  };

  const handleKey = e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), ask());

  return (
    <div>
      <Header title="Medical Research Assistant" subtitle="Question Answering from medical documents & knowledge base" />
      <div className="page-body">
        <div className="page-header">
          <h1>Medical Research Assistant</h1>
          <p>Ask medical questions and retrieve relevant answers from research papers, clinical notes, and the disease database.</p>
        </div>

        <div className="grid-2">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Question input */}
            <div className="card">
              <div className="section-title"><HelpCircle size={18} /> Ask a Medical Question</div>
              <div className="input-group">
                <textarea
                  rows={4}
                  placeholder="e.g., What are the symptoms and treatment options for rheumatoid arthritis?"
                  value={question}
                  onChange={e => setQuestion(e.target.value)}
                  onKeyDown={handleKey}
                />
              </div>
              <button className="btn btn-primary" onClick={() => ask()} disabled={loading || !question.trim()} style={{ width: '100%', justifyContent: 'center' }}>
                <Send size={16} /> {loading ? 'Searching…' : 'Get Answer'}
              </button>
              {error && <div className="error-msg">⚠️ {error}</div>}
            </div>

            {/* Sample questions */}
            <div className="card" style={{ padding: '16px' }}>
              <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '12px' }}>💡 Sample Questions</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {SAMPLE_QUESTIONS.map(q => (
                  <button key={q} className="btn btn-secondary" style={{ textAlign: 'left', fontSize: '13px', padding: '8px 12px' }}
                    onClick={() => { setQuestion(q); ask(q); }}>
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* History */}
            {history.length > 0 && (
              <div className="card" style={{ padding: '16px' }}>
                <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '10px' }}>🕐 Recent Queries</div>
                {history.map((h, i) => (
                  <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
                    <span style={{ color: 'var(--text-primary)' }}>{h.q.substring(0, 50)}…</span>
                    <span style={{ color: 'var(--accent-cyan)' }}>{h.answers} ans</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Answers */}
          <div>
            {loading && <div className="card loading-state"><div className="loading-spinner" /><span>Searching knowledge base…</span></div>}

            {result && !loading && (
              <>
                <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '14px', fontWeight: '700' }}>"{result.question}"</div>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{result.total_passages_searched} passages searched</span>
                </div>

                {result.answers?.length > 0 ? (
                  result.answers.map((ans, i) => (
                    <div className="result-card" key={i} style={{ marginBottom: '14px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                          <span style={{ width: '22px', height: '22px', background: 'rgba(0,212,255,0.15)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '11px', fontWeight: '800', color: 'var(--accent-cyan)' }}>{i + 1}</span>
                          {SOURCE_ICONS[ans.source_type]}
                          <span className={`badge ${SOURCE_BADGE[ans.source_type]}`}>{ans.source_type}</span>
                        </div>
                        <span style={{ color: 'var(--accent-cyan)', fontWeight: '800', fontSize: '15px' }}>{ans.relevance}%</span>
                      </div>

                      {/* Answer text */}
                      <p style={{ fontSize: '14px', lineHeight: '1.7', color: 'var(--text-primary)', marginBottom: '10px' }}>
                        {ans.answer}
                      </p>

                      <div className="divider" style={{ margin: '8px 0' }} />

                      {/* Source */}
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        <strong style={{ color: 'var(--text-primary)' }}>{ans.source_title}</strong>
                        {ans.source_info && <span> — {ans.source_info}</span>}
                      </div>

                      <div className="relevance-bar" style={{ width: `${ans.relevance}%`, marginTop: '8px' }} />
                    </div>
                  ))
                ) : (
                  <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                    <HelpCircle size={40} opacity={0.3} style={{ margin: '0 auto 12px' }} />
                    <p>No relevant answers found. Try rephrasing your question.</p>
                  </div>
                )}
              </>
            )}

            {!result && !loading && (
              <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px', flexDirection: 'column', gap: '12px', color: 'var(--text-muted)' }}>
                <HelpCircle size={50} opacity={0.3} />
                <p style={{ textAlign: 'center' }}>Ask a medical question to retrieve relevant answers from our knowledge base</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
