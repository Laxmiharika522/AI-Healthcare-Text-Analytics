import React, { useState } from 'react';
import axios from 'axios';
import { Brain, Zap, FileText, ChevronRight } from 'lucide-react';
import Header from '../components/Header';

const API = 'http://localhost:5000/api';
const SAMPLE = `Deep learning has emerged as a transformative technology in medical image analysis. Convolutional neural networks (CNNs) have demonstrated remarkable performance in tasks such as lesion detection, organ segmentation, and disease classification across various imaging modalities including magnetic resonance imaging (MRI), computed tomography (CT), and X-ray radiographs. Recent advances in transformer architectures have further expanded the capabilities of deep learning models in medical imaging, enabling better capture of long-range dependencies and contextual information. Transfer learning has proven particularly valuable in medical domains where labeled data is scarce, allowing models pre-trained on large natural image datasets to be fine-tuned on smaller medical datasets with strong performance. Federated learning approaches have emerged to address data privacy concerns, enabling collaborative model training across multiple institutions without sharing patient data. Despite these advances, several challenges remain including the need for large annotated datasets, model interpretability, and domain shift across different hospitals and equipment manufacturers. This survey provides a comprehensive overview of deep learning applications in radiology, pathology, ophthalmology, and dermatology, analyzing both technical contributions and clinical validation studies.`;

export default function ReportSummarizer() {
  const [text, setText] = useState('');
  const [numSentences, setNumSentences] = useState(4);
  const [method, setMethod] = useState('tfidf');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const summarize = async () => {
    if (!text.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await axios.post(`${API}/summarize`, { text, num_sentences: numSentences, method });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Summarization failed. Is the backend running?');
    } finally { setLoading(false); }
  };

  const compressionPct = result ? Math.round((1 - result.compression_ratio) * 100) : 0;

  return (
    <div>
      <Header title="Clinical Report Summarizer" subtitle="Extractive text summarization for medical documents" />
      <div className="page-body">
        <div className="page-header">
          <h1>Clinical Report Summarizer</h1>
          <p>Auto-summarize long clinical reports, research articles, and medical notes into concise summaries.</p>
        </div>

        <div className="grid-2" style={{ marginBottom: '24px' }}>
          {/* Input */}
          <div className="card">
            <div className="section-title"><FileText size={18} /> Input Document</div>
            <div className="input-group">
              <textarea
                rows={12}
                placeholder="Paste a long clinical report, research abstract, or medical document..."
                value={text}
                onChange={e => setText(e.target.value)}
              />
              <div className="textarea-footer">{text.split(/\s+/).filter(Boolean).length} words</div>
            </div>
            <div className="grid-2" style={{ gap: '12px', marginBottom: '16px' }}>
              <div className="input-group" style={{ marginBottom: 0 }}>
                <label className="input-label">Summary Sentences</label>
                <select value={numSentences} onChange={e => setNumSentences(Number(e.target.value))}>
                  {[2, 3, 4, 5, 6, 8].map(n => <option key={n} value={n}>{n} sentences</option>)}
                </select>
              </div>
              <div className="input-group" style={{ marginBottom: 0 }}>
                <label className="input-label">Method</label>
                <select value={method} onChange={e => setMethod(e.target.value)}>
                  <option value="tfidf">TF-IDF Extractive</option>
                  <option value="lsa">LSA (sumy)</option>
                  <option value="lexrank">LexRank (sumy)</option>
                </select>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-primary" onClick={summarize} disabled={loading || !text.trim()}>
                <Brain size={16} /> {loading ? 'Summarizing…' : 'Summarize'}
              </button>
              <button className="btn btn-secondary" onClick={() => setText(SAMPLE)}>Load Sample</button>
              <button className="btn btn-secondary" onClick={() => { setText(''); setResult(null); }}>Clear</button>
            </div>
            {error && <div className="error-msg">⚠️ {error}</div>}
          </div>

          {/* Stats */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {result ? (
              <>
                <div className="grid-2" style={{ gap: '12px' }}>
                  {[
                    { label: 'Original Words', value: result.original_word_count, color: '#f59e0b' },
                    { label: 'Summary Words', value: result.summary_word_count, color: '#10b981' },
                    { label: 'Sentences Kept', value: `${result.sentences_summary}/${result.sentences_original}`, color: '#00d4ff' },
                    { label: 'Compressed By', value: `${compressionPct}%`, color: '#8b5cf6' },
                  ].map(({ label, value, color }) => (
                    <div className="stat-card" key={label}>
                      <div className="stat-value" style={{ color, fontSize: '24px' }}>{value}</div>
                      <div className="stat-label">{label}</div>
                    </div>
                  ))}
                </div>

                {/* Compression visual */}
                <div className="card" style={{ padding: '16px' }}>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '10px', fontWeight: '600' }}>Compression Ratio</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Original</div>
                      <div style={{ height: '10px', background: 'rgba(245,158,11,0.3)', borderRadius: '5px' }} />
                    </div>
                    <ChevronRight size={16} color="var(--text-muted)" />
                    <div style={{ flex: result.compression_ratio }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>Summary</div>
                      <div style={{ height: '10px', background: 'linear-gradient(90deg, var(--accent-cyan), var(--accent-blue))', borderRadius: '5px' }} />
                    </div>
                  </div>
                  <div style={{ textAlign: 'center', marginTop: '10px', fontSize: '22px', fontWeight: '800', color: 'var(--accent-cyan)' }}>
                    {compressionPct}% reduction
                  </div>
                </div>
              </>
            ) : (
              <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '250px', flexDirection: 'column', gap: '12px', color: 'var(--text-muted)' }}>
                <Brain size={40} opacity={0.3} />
                <span>Paste a document and click Summarize</span>
              </div>
            )}
          </div>
        </div>

        {/* Summary Output */}
        {result?.summary && (
          <div className="result-section">
            <div className="card">
              <div className="result-title"><Zap size={16} /> Generated Summary</div>
              <div style={{ background: 'rgba(0,212,255,0.04)', border: '1px solid rgba(0,212,255,0.15)', borderRadius: '12px', padding: '20px', fontSize: '15px', lineHeight: '1.8', color: 'var(--text-primary)' }}>
                {result.summary}
              </div>
              {result.top_sentence_scores && (
                <div style={{ marginTop: '20px' }}>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: 'var(--text-secondary)', marginBottom: '10px' }}>📊 Sentence Importance Scores</div>
                  <div className="score-bar-container">
                    {Object.entries(result.top_sentence_scores).map(([sent, score]) => (
                      <div className="score-bar-item" key={sent}>
                        <div className="score-bar-label">
                          <span className="score-bar-text" style={{ fontSize: '12px' }}>{sent}</span>
                          <span className="score-bar-value">{score}</span>
                        </div>
                        <div className="score-bar-track">
                          <div className="score-bar-fill" style={{ width: `${Math.min(score * 300, 100)}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
