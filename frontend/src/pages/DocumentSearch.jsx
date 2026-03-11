import React, { useState } from 'react';
import axios from 'axios';
import { Search, ExternalLink, BookOpen, FileText } from 'lucide-react';
import Header from '../components/Header';

const API = 'http://localhost:5000/api';

export default function DocumentSearch() {
  const [query, setQuery] = useState('');
  const [docType, setDocType] = useState('all');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true); setError(''); setResults(null);
    try {
      const res = await axios.post(`${API}/search`, { query, doc_type: docType, top_k: 10 });
      setResults(res.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Search failed. Is the backend running?');
    } finally { setLoading(false); }
  };

  const handleKey = e => e.key === 'Enter' && search();

  const SAMPLE_QUERIES = ['diabetes treatment', 'pneumonia antibiotics', 'deep learning medical imaging', 'blood pressure hypertension', 'covid 19 clinical trial'];

  return (
    <div>
      <Header title="Medical Document Search" subtitle="TF-IDF + Cosine Similarity Information Retrieval" />
      <div className="page-body">
        <div className="page-header">
          <h1>Medical Document Search Engine</h1>
          <p>Search through research papers and clinical notes using TF-IDF vectorization and cosine similarity ranking.</p>
        </div>

        {/* Search Box */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <input
              type="text"
              placeholder="Search medical documents, papers…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKey}
              style={{ flex: 1, minWidth: '250px' }}
            />
            <select value={docType} onChange={e => setDocType(e.target.value)} style={{ width: '160px' }}>
              <option value="all">All Documents</option>
              <option value="papers">Research Papers</option>
              <option value="notes">Clinical Notes</option>
            </select>
            <button className="btn btn-primary" onClick={search} disabled={loading || !query.trim()}>
              <Search size={16} /> {loading ? 'Searching…' : 'Search'}
            </button>
          </div>

          {/* Sample queries */}
          <div style={{ marginTop: '14px', display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Try:</span>
            {SAMPLE_QUERIES.map(q => (
              <button key={q} className="btn btn-secondary" style={{ padding: '4px 12px', fontSize: '12px' }} onClick={() => { setQuery(q); }}>
                {q}
              </button>
            ))}
          </div>
        </div>

        {error && <div className="error-msg">⚠️ {error}</div>}

        {/* Stats */}
        {results && (
          <div style={{ display: 'flex', gap: '16px', marginBottom: '20px', flexWrap: 'wrap' }}>
            <div className="stat-card" style={{ flex: '1', minWidth: '140px' }}>
              <div className="stat-value" style={{ color: 'var(--accent-cyan)', fontSize: '24px' }}>{results.total}</div>
              <div className="stat-label">Results Found</div>
            </div>
            <div className="stat-card" style={{ flex: '1', minWidth: '140px' }}>
              <div className="stat-value" style={{ color: '#8b5cf6', fontSize: '24px' }}>{results.corpus_size}</div>
              <div className="stat-label">Docs Searched</div>
            </div>
            <div className="stat-card" style={{ flex: '2', minWidth: '200px' }}>
              <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-primary)' }}>"{results.query}"</div>
              <div className="stat-label">Search Query</div>
            </div>
          </div>
        )}

        {loading && <div className="card loading-state"><div className="loading-spinner" /><span>Searching corpus…</span></div>}

        {/* Results */}
        {results?.results?.map((doc, i) => (
          <div className="result-card" key={i}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', marginBottom: '10px' }}>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', flex: 1 }}>
                <div style={{ marginTop: '2px' }}>
                  {doc.type === 'Research Paper' ? <BookOpen size={18} color="#8b5cf6" /> : <FileText size={18} color="var(--accent-cyan)" />}
                </div>
                <div>
                  <div style={{ fontWeight: '700', fontSize: '15px', marginBottom: '4px' }}>{doc.title}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {doc.metadata?.authors && <span>{doc.metadata.authors} • </span>}
                    {doc.metadata?.journal && <span>{doc.metadata.journal} </span>}
                    {doc.metadata?.year && <span>({doc.metadata.year})</span>}
                    {doc.metadata?.doctor && <span>Dr. {doc.metadata.doctor} • {doc.metadata.department}</span>}
                    {doc.metadata?.diagnosis && <span> • {doc.metadata.diagnosis}</span>}
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
                <span className={`badge ${doc.type === 'Research Paper' ? 'badge-paper' : 'badge-note'}`}>{doc.type}</span>
                <span style={{ fontWeight: '800', color: 'var(--accent-cyan)', fontSize: '15px' }}>{doc.relevance_score}%</span>
              </div>
            </div>
            {doc.metadata?.keywords && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '6px' }}>
                🏷️ {doc.metadata.keywords}
              </div>
            )}
            <div className="relevance-bar" style={{ width: `${doc.relevance_score}%` }} />
          </div>
        ))}

        {results?.total === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <Search size={40} opacity={0.3} style={{ margin: '0 auto 12px' }} />
            <p>No results found. Try different keywords.</p>
          </div>
        )}
      </div>
    </div>
  );
}
