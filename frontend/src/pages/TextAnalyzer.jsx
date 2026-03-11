import React, { useState } from 'react';
import axios from 'axios';
import { FileText, Zap, Tag, BarChart2, Book } from 'lucide-react';
import Header from '../components/Header';

const API = 'http://localhost:5000/api';

const SAMPLE_TEXT = `Patient presents with increased thirst, frequent urination, fatigue, and blurred vision. Blood glucose level measured at 320 mg/dL. HbA1c is 9.2%. Patient has a family history of diabetes mellitus. Prescribed Metformin 500mg twice daily and recommended dietary modifications including low sugar intake. Follow-up in 4 weeks for blood pressure monitoring and kidney function tests.`;

const CHIP_COLORS = {
  diseases: 'chip-disease',
  symptoms: 'chip-symptom',
  medications: 'chip-medication',
  treatments: 'chip-treatment',
  anatomy: 'chip-anatomy',
  measurements: 'chip-measurements',
};
const ENTITY_LABELS = {
  diseases: '🦠 Diseases',
  symptoms: '🩺 Symptoms',
  medications: '💊 Medications',
  treatments: '⚕️ Treatments',
  anatomy: '🫀 Anatomy',
  measurements: '📊 Measurements',
};

export default function TextAnalyzer() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('entities');

  const analyze = async () => {
    if (!text.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await axios.post(`${API}/analyze`, { text });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Analysis failed. Is the backend running?');
    } finally { setLoading(false); }
  };

  const loadSample = () => setText(SAMPLE_TEXT);

  return (
    <div>
      <Header title="Clinical Text Analyzer" subtitle="NLP preprocessing + Medical Named Entity Recognition" />
      <div className="page-body">
        <div className="page-header">
          <h1>Clinical Text Analyzer</h1>
          <p>Extract medical entities, perform tokenization, stemming, and lemmatization on clinical text.</p>
        </div>

        <div className="grid-2">
          <div className="card">
            <div className="section-title"><FileText size={18} /> Input Text</div>
            <div className="input-group">
              <textarea
                rows={10}
                placeholder="Enter clinical notes, patient records, or any medical text..."
                value={text}
                onChange={e => setText(e.target.value)}
              />
              <div className="textarea-footer">{text.length} characters</div>
            </div>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={analyze} disabled={loading || !text.trim()}>
                <Zap size={16} /> {loading ? 'Analyzing...' : 'Analyze Text'}
              </button>
              <button className="btn btn-secondary" onClick={loadSample}>Load Sample</button>
              <button className="btn btn-secondary" onClick={() => { setText(''); setResult(null); }}>Clear</button>
            </div>
            {error && <div className="error-msg">⚠️ {error}</div>}
          </div>

          {/* Stats panel */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {result ? (
              <>
                <div className="grid-2" style={{ gap: '12px' }}>
                  {[
                    { label: 'Words', value: result.preprocessing?.word_count, color: '#00d4ff' },
                    { label: 'Sentences', value: result.preprocessing?.sentence_count, color: '#10b981' },
                    { label: 'Entities', value: result.entities?.total_entities, color: '#f59e0b' },
                    { label: 'Characters', value: result.text_length, color: '#8b5cf6' },
                  ].map(({ label, value, color }) => (
                    <div className="stat-card" key={label}>
                      <div className="stat-value" style={{ color }}>{value ?? '—'}</div>
                      <div className="stat-label">{label}</div>
                    </div>
                  ))}
                </div>

                {/* Word frequency */}
                {result.word_frequency?.length > 0 && (
                  <div className="card" style={{ padding: '16px' }}>
                    <div className="result-title" style={{ marginBottom: '12px' }}><BarChart2 size={16} /> Top Keywords</div>
                    <div className="score-bar-container">
                      {result.word_frequency.slice(0, 6).map(([word, count]) => (
                        <div className="score-bar-item" key={word}>
                          <div className="score-bar-label">
                            <span className="score-bar-text">{word}</span>
                            <span className="score-bar-value">{count}</span>
                          </div>
                          <div className="score-bar-track">
                            <div className="score-bar-fill" style={{ width: `${(count / (result.word_frequency[0][1] || 1)) * 100}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', color: 'var(--text-muted)', flexDirection: 'column', gap: '12px' }}>
                <FileText size={40} opacity={0.3} />
                <span>Enter text and click Analyze</span>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className="result-section">
            <div className="tabs">
              {['entities', 'preprocessing', 'spacy'].map(t => (
                <button key={t} className={`tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
                  {t === 'entities' ? '🏷️ Entities' : t === 'preprocessing' ? '⚙️ Preprocessing' : '🤖 SpaCy NER'}
                </button>
              ))}
            </div>

            {activeTab === 'entities' && (
              <div className="card">
                <div className="result-title"><Tag size={16} /> Medical Entities Extracted</div>
                {Object.entries(result.entities?.entities || {}).map(([category, items]) =>
                  items.length > 0 && (
                    <div key={category} style={{ marginBottom: '20px' }}>
                      <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '10px' }}>
                        {ENTITY_LABELS[category] || category}
                        <span style={{ marginLeft: '8px', background: 'rgba(0,212,255,0.12)', borderRadius: '10px', padding: '1px 8px', fontSize: '11px', color: 'var(--accent-cyan)' }}>{items.length}</span>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {items.map((item, i) => (
                          <span key={i} className={`chip ${CHIP_COLORS[category]}`}>
                            {item.entity} <span style={{ opacity: 0.6 }}>×{item.count}</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )
                )}
                {result.entities?.total_entities === 0 && (
                  <p style={{ color: 'var(--text-muted)' }}>No medical entities found. Try more detailed clinical text.</p>
                )}
              </div>
            )}

            {activeTab === 'preprocessing' && (
              <div className="grid-2">
                {[
                  { title: '🔤 Tokens (Clean)', data: result.preprocessing?.filtered_tokens?.slice(0, 30), color: '#00d4ff' },
                  { title: '📐 Stemmed', data: result.preprocessing?.stemmed?.slice(0, 30), color: '#f59e0b' },
                  { title: '📝 Lemmatized', data: result.preprocessing?.lemmatized?.slice(0, 30), color: '#10b981' },
                  { title: '📖 Sentences', data: result.preprocessing?.sentences, color: '#8b5cf6', limitLen: true },
                ].map(({ title, data, color, limitLen }) => (
                  <div className="card" key={title}>
                    <div className="result-title" style={{ color }}>{title}</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', maxHeight: '180px', overflowY: 'auto' }}>
                      {data?.map((item, i) => (
                        <span key={i} style={{ background: 'rgba(255,255,255,0.05)', borderRadius: '6px', padding: '3px 8px', fontSize: '12px', color: 'var(--text-primary)' }}>
                          {limitLen ? item.substring(0, 70) + (item.length > 70 ? '…' : '') : item}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'spacy' && (
              <div className="card">
                <div className="result-title">🤖 SpaCy Named Entities</div>
                {result.entities?.spacy_entities?.length > 0 ? (
                  <div style={{ overflowX: 'auto' }}>
                    <table className="data-table">
                      <thead><tr><th>Entity Text</th><th>Label</th><th>Description</th></tr></thead>
                      <tbody>
                        {result.entities.spacy_entities.map((ent, i) => (
                          <tr key={i}>
                            <td><strong>{ent.text}</strong></td>
                            <td><span className="badge badge-note">{ent.label}</span></td>
                            <td style={{ color: 'var(--text-secondary)' }}>{ent.description}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-muted)' }}>SpaCy not available or no entities found. Install <code>python -m spacy download en_core_web_sm</code>.</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
