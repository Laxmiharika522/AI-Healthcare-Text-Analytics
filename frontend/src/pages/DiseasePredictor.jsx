import React, { useState } from 'react';
import axios from 'axios';
import { Activity, Zap, AlertTriangle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import Header from '../components/Header';

const API = 'http://localhost:5000/api';
const SAMPLE = `fever, cough, rapid breathing, chest pain, chills, difficulty breathing, fatigue, low oxygen saturation, productive sputum`;
const COLORS = ['#00d4ff', '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'];

const RISK_COLORS = { High: '#f43f5e', Moderate: '#f59e0b', Low: '#10b981' };

export default function DiseasePredictor() {
  const [symptoms, setSymptoms] = useState('');
  const [model, setModel] = useState('random_forest');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const predict = async () => {
    if (!symptoms.trim()) return;
    setLoading(true); setError(''); setResult(null);
    try {
      const res = await axios.post(`${API}/predict`, { symptoms, model });
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.error || 'Prediction failed. Is the backend running?');
    } finally { setLoading(false); }
  };

  const chartData = result?.predictions?.map(p => ({
    name: p.disease.length > 20 ? p.disease.substring(0, 20) + '…' : p.disease,
    fullName: p.disease,
    probability: p.probability,
    risk: p.risk_level,
  })) || [];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload?.[0]) {
      const d = payload[0].payload;
      return (
        <div style={{ background: '#0a192f', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '10px', padding: '12px 16px' }}>
          <p style={{ color: '#fff', fontWeight: 700, marginBottom: '4px' }}>{d.fullName}</p>
          <p style={{ color: '#00d4ff' }}>Probability: <strong>{d.probability}%</strong></p>
          <span className={`badge badge-${d.risk.toLowerCase()}`}>{d.risk} Risk</span>
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <Header title="Disease Risk Predictor" subtitle="ML-powered disease prediction from symptom descriptions" />
      <div className="page-body">
        <div className="page-header">
          <h1>Disease Risk Predictor</h1>
          <p>Describe symptoms in natural language and see probability-ranked disease predictions from trained ML models.</p>
        </div>

        <div className="grid-2">
          <div className="card">
            <div className="section-title"><Activity size={18} /> Symptom Description</div>
            <div className="input-group">
              <label className="input-label">Describe Symptoms</label>
              <textarea
                rows={6}
                placeholder="e.g., severe chest pain radiating to left arm, shortness of breath, sweating, nausea..."
                value={symptoms}
                onChange={e => setSymptoms(e.target.value)}
              />
            </div>
            <div className="input-group">
              <label className="input-label">ML Model</label>
              <select value={model} onChange={e => setModel(e.target.value)}>
                <option value="random_forest">Random Forest</option>
                <option value="logistic_regression">Logistic Regression</option>
                {result?.available_models?.includes('xgboost') && <option value="xgboost">XGBoost</option>}
              </select>
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-primary" onClick={predict} disabled={loading || !symptoms.trim()}>
                <Zap size={16} /> {loading ? 'Predicting…' : 'Predict Diseases'}
              </button>
              <button className="btn btn-secondary" onClick={() => setSymptoms(SAMPLE)}>Sample</button>
            </div>
            {error && <div className="error-msg">⚠️ {error}</div>}

            {/* Model comparison */}
            {result?.all_models && (
              <div style={{ marginTop: '20px' }}>
                <div className="result-title" style={{ fontSize: '14px', marginBottom: '10px' }}>🔬 All Model Predictions</div>
                {Object.entries(result.all_models).map(([mname, mres]) => (
                  <div key={mname} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{mname.replace('_', ' ')}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '13px', fontWeight: '600' }}>{mres.prediction}</span>
                      <span style={{ fontSize: '12px', color: 'var(--accent-cyan)' }}>{mres.confidence}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {loading && <div className="card loading-state"><div className="loading-spinner" /><span>Running ML models…</span></div>}

            {result && !loading && (
              <>
                {/* Bar Chart */}
                <div className="card">
                  <div className="section-title"><Activity size={18} /> Probability Distribution</div>
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="name" tick={{ fill: '#8aa5c0', fontSize: 11 }} />
                      <YAxis tick={{ fill: '#8aa5c0', fontSize: 11 }} domain={[0, 100]} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="probability" radius={[6, 6, 0, 0]}>
                        {chartData.map((entry, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Prediction list */}
                <div className="card">
                  <div className="section-title">Top Predictions</div>
                  <div className="score-bar-container">
                    {result.predictions.map((pred, i) => (
                      <div key={i} style={{ padding: '10px', background: 'rgba(0,0,0,0.2)', borderRadius: '10px', marginBottom: '8px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                          <span style={{ fontWeight: '700', fontSize: '14px' }}>{i + 1}. {pred.disease}</span>
                          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                            <span className={`badge badge-${pred.risk_level.toLowerCase()}`}>{pred.risk_level}</span>
                            <span style={{ color: 'var(--accent-cyan)', fontWeight: '800', fontSize: '16px' }}>{pred.probability}%</span>
                          </div>
                        </div>
                        <div className="score-bar-track">
                          <div className="score-bar-fill" style={{ width: `${pred.probability}%`, background: `linear-gradient(90deg, ${RISK_COLORS[pred.risk_level] || '#3b82f6'}, var(--accent-cyan))` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {!result && !loading && (
              <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', flexDirection: 'column', gap: '12px', color: 'var(--text-muted)' }}>
                <AlertTriangle size={40} opacity={0.3} />
                <span>Enter symptoms to get predictions</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
