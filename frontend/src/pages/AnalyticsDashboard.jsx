import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LineChart, Line, AreaChart, Area
} from 'recharts';
import { Activity, Users, FileText, BookOpen, AlertTriangle, RefreshCw } from 'lucide-react';
import Header from '../components/Header';

const API = 'http://localhost:5000/api';
const COLORS = ['#00d4ff', '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e', '#06b6d4', '#84cc16'];
const SEV_COLORS = { Critical: '#f43f5e', High: '#f59e0b', Moderate: '#3b82f6', Low: '#10b981' };

const CustomPieTooltip = ({ active, payload }) => {
  if (active && payload?.[0]) {
    return (
      <div style={{ background: '#0a192f', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '10px', padding: '10px 14px' }}>
        <p style={{ color: '#fff', fontWeight: 700 }}>{payload[0].name}</p>
        <p style={{ color: '#00d4ff' }}>Count: <strong>{payload[0].value}</strong></p>
        <p style={{ color: '#8aa5c0', fontSize: '12px' }}>{payload[0].payload.percent}%</p>
      </div>
    );
  }
  return null;
};

export default function AnalyticsDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = async () => {
    setLoading(true); setError('');
    try {
      const res = await axios.get(`${API}/analytics`);
      setData(res.data);
    } catch (e) {
      setError('Could not load analytics. Make sure the backend is running on port 5000.');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  if (loading) return (
    <div>
      <Header title="Analytics Dashboard" subtitle="Loading data..." />
      <div className="page-body">
        <div className="card loading-state" style={{ minHeight: '400px' }}>
          <div className="loading-spinner" />
          <span>Loading analytics from database…</span>
        </div>
      </div>
    </div>
  );

  if (error) return (
    <div>
      <Header title="Analytics Dashboard" subtitle="Error" />
      <div className="page-body">
        <div className="error-msg">{error}</div>
        <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={fetchData}>
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    </div>
  );

  const summary = data?.summary?.data;
  const diseases = (data?.most_common_diseases?.data || []).slice(0, 8);
  const symptoms = (data?.most_frequent_symptoms?.data || []).slice(0, 10);
  const ageGroups = data?.patient_age_distribution?.data || [];
  const severity = (data?.disease_severity?.data || []).map(d => ({
    ...d, fill: SEV_COLORS[d.severity] || '#3b82f6'
  }));
  const papersYear = data?.papers_per_year?.data || [];
  const genderData = (data?.patient_gender?.data || []).map((d, i) => ({
    ...d, fill: COLORS[i]
  }));
  const topDoctors = data?.top_doctors?.data || [];
  const topPapers = data?.most_cited_papers?.data || [];
  const categories = data?.diseases_by_category?.data || [];

  return (
    <div>
      <Header title="Analytics Dashboard" subtitle="Real-time insights from medical database" />
      <div className="page-body">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
          <div>
            <h1 style={{ fontSize: '26px', fontWeight: '800', background: 'linear-gradient(135deg, #e8f4fd, #00d4ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Analytics Dashboard</h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>14 complex queries · Complete healthcare insights</p>
          </div>
          <button className="btn btn-secondary" onClick={fetchData}><RefreshCw size={15} /> Refresh</button>
        </div>

        {/* Summary Stats */}
        {summary && (
          <div className="grid-4" style={{ marginBottom: '24px' }}>
            {[
              { label: 'Patients', value: summary.total_patients, icon: '👤', color: '#00d4ff' },
              { label: 'Clinical Notes', value: summary.total_clinical_notes, icon: '📋', color: '#10b981' },
              { label: 'Diseases', value: summary.total_diseases, icon: '🦠', color: '#f43f5e' },
              { label: 'Research Papers', value: summary.total_research_papers, icon: '📄', color: '#8b5cf6' },
              { label: 'Avg Patient Age', value: summary.average_patient_age, icon: '🎂', color: '#f59e0b' },
              { label: 'Critical Cases', value: summary.critical_cases, icon: '🚨', color: '#f43f5e' },
            ].map(({ label, value, icon, color }) => (
              <div className="stat-card" key={label}>
                <div style={{ fontSize: '24px' }}>{icon}</div>
                <div className="stat-value" style={{ color, fontSize: '26px' }}>{value}</div>
                <div className="stat-label">{label}</div>
              </div>
            ))}
          </div>
        )}

        {/* Row 1: Most Common Diseases + Severity Distribution */}
        <div className="grid-2" style={{ marginBottom: '20px' }}>
          <div className="card">
            <div className="section-title">🦠 Most Common Diseases</div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={diseases} margin={{ top: 0, right: 10, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="diagnosis" tick={{ fill: '#8aa5c0', fontSize: 10 }} angle={-35} textAnchor="end" />
                <YAxis tick={{ fill: '#8aa5c0', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0a192f', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '10px' }} labelStyle={{ color: '#fff' }} itemStyle={{ color: '#00d4ff' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {diseases.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="section-title">⚠️ Disease Severity Distribution</div>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={severity} cx="50%" cy="50%" outerRadius={90} dataKey="count" nameKey="severity" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`} labelLine={{ stroke: 'rgba(255,255,255,0.2)' }}>
                  {severity.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Pie>
                <Tooltip content={<CustomPieTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Row 2: Top Symptoms + Age Distribution */}
        <div className="grid-2" style={{ marginBottom: '20px' }}>
          <div className="card">
            <div className="section-title">🩺 Most Frequent Symptoms</div>
            <div className="score-bar-container">
              {symptoms.slice(0, 8).map(s => (
                <div className="score-bar-item" key={s.symptom}>
                  <div className="score-bar-label">
                    <span className="score-bar-text" style={{ fontSize: '13px' }}>{s.symptom}</span>
                    <span className="score-bar-value">{s.count}</span>
                  </div>
                  <div className="score-bar-track">
                    <div className="score-bar-fill" style={{ width: `${(s.count / (symptoms[0]?.count || 1)) * 100}%`, background: 'linear-gradient(90deg, #f59e0b, #f43f5e)' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="section-title">👥 Patient Age Groups (Risk Distribution)</div>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={ageGroups} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="age_group" tick={{ fill: '#8aa5c0', fontSize: 12 }} />
                <YAxis tick={{ fill: '#8aa5c0', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0a192f', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '10px' }} labelStyle={{ color: '#fff' }} itemStyle={{ color: '#10b981' }} />
                <Bar dataKey="count" fill="#10b981" radius={[6, 6, 0, 0]} name="Patients" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Row 3: Research Papers Timeline + Gender */}
        <div className="grid-2" style={{ marginBottom: '20px' }}>
          <div className="card">
            <div className="section-title">📈 Research Papers Published Per Year</div>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={papersYear} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="paperGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="year" tick={{ fill: '#8aa5c0', fontSize: 11 }} />
                <YAxis tick={{ fill: '#8aa5c0', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#0a192f', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '10px' }} labelStyle={{ color: '#fff' }} />
                <Area type="monotone" dataKey="paper_count" stroke="#8b5cf6" fill="url(#paperGrad)" strokeWidth={2} name="Papers" />
                <Area type="monotone" dataKey="total_citations" stroke="#00d4ff" fill="none" strokeWidth={1.5} strokeDasharray="4 2" name="Citations" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <div className="section-title">⚤ Patient Gender Distribution</div>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={genderData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} dataKey="count" nameKey="gender"
                  label={({ name, value }) => `${name}: ${value}`} labelLine={{ stroke: 'rgba(255,255,255,0.2)' }}>
                  {genderData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#0a192f', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Row 4: Top Doctors + Disease Categories */}
        <div className="grid-2" style={{ marginBottom: '20px' }}>
          <div className="card">
            <div className="section-title">👨‍⚕️ Top Doctors by Clinical Notes</div>
            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead><tr><th>#</th><th>Doctor</th><th>Department</th><th>Notes</th><th>Patients</th></tr></thead>
                <tbody>
                  {topDoctors.slice(0, 6).map((d, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--accent-cyan)', fontWeight: '700' }}>{i + 1}</td>
                      <td><strong>{d.doctor_name}</strong></td>
                      <td style={{ color: 'var(--text-secondary)' }}>{d.department}</td>
                      <td><span style={{ color: '#10b981', fontWeight: '700' }}>{d.note_count}</span></td>
                      <td>{d.unique_patients}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <div className="section-title">🏷️ Disease Categories</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={categories} layout="vertical" margin={{ top: 5, right: 30, left: 30, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" tick={{ fill: '#8aa5c0', fontSize: 11 }} />
                <YAxis type="category" dataKey="category" tick={{ fill: '#8aa5c0', fontSize: 11 }} width={90} />
                <Tooltip contentStyle={{ background: '#0a192f', border: '1px solid rgba(0,212,255,0.3)', borderRadius: '10px' }} labelStyle={{ color: '#fff' }} />
                <Bar dataKey="disease_count" radius={[0, 6, 6, 0]}>
                  {categories.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Row 5: Most Cited Papers */}
        <div className="card">
          <div className="section-title">📚 Most Cited Research Papers</div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead><tr><th>#</th><th>Title</th><th>Authors</th><th>Journal</th><th>Year</th><th>Citations</th></tr></thead>
              <tbody>
                {topPapers.map((p, i) => (
                  <tr key={i}>
                    <td style={{ color: 'var(--accent-cyan)', fontWeight: '700' }}>{i + 1}</td>
                    <td style={{ maxWidth: '260px', fontSize: '12px' }}><strong>{p.title}</strong></td>
                    <td style={{ color: 'var(--text-secondary)', fontSize: '11px', maxWidth: '140px' }}>{p.authors?.split(',')[0]}…</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '11px' }}>{p.journal}</td>
                    <td>{p.year}</td>
                    <td><span style={{ color: '#f59e0b', fontWeight: '800' }}>{p.citation_count?.toLocaleString()}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
