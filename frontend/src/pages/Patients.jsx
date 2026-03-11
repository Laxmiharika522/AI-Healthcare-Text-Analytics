import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Plus, X } from 'lucide-react';
import Header from '../components/Header';

const API = 'http://localhost:5000/api';

export default function Patients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', age: '', gender: 'Male', blood_type: '', admission_date: '', contact: '' });
  const [msg, setMsg] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/patients`);
      setPatients(res.data.patients || []);
    } catch {}
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const addPatient = async () => {
    try {
      await axios.post(`${API}/patients`, { ...form, age: Number(form.age) });
      setMsg('Patient added successfully!');
      setShowForm(false);
      setForm({ name: '', age: '', gender: 'Male', blood_type: '', admission_date: '', contact: '' });
      load();
    } catch (e) {
      setMsg('Error: ' + (e.response?.data?.error || 'Failed'));
    }
  };

  const GENDER_COLOR = { Male: '#3b82f6', Female: '#f43f5e' };

  return (
    <div>
      <Header title="Patient Records" subtitle="Database: Patients table management" />
      <div className="page-body">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <div>
            <h1 style={{ fontSize: '26px', fontWeight: '800', background: 'linear-gradient(135deg, #e8f4fd, #00d4ff)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Patient Records</h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>{patients.length} patients in database</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
            <Plus size={16} /> Add Patient
          </button>
        </div>

        {msg && <div className={`${msg.startsWith('Error') ? 'error-msg' : 'success-msg'}`} style={{ marginBottom: '16px' }}>{msg}</div>}

        {showForm && (
          <div className="card" style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div className="section-title"><Plus size={18} /> New Patient</div>
              <button className="btn btn-secondary" style={{ padding: '5px 10px' }} onClick={() => setShowForm(false)}><X size={14} /></button>
            </div>
            <div className="grid-3" style={{ gap: '16px' }}>
              {[
                { key: 'name', label: 'Full Name', type: 'text', placeholder: 'John Doe' },
                { key: 'age', label: 'Age', type: 'text', placeholder: '45' },
                { key: 'contact', label: 'Contact', type: 'text', placeholder: '+1-555-0000' },
                { key: 'blood_type', label: 'Blood Type', type: 'text', placeholder: 'A+' },
                { key: 'admission_date', label: 'Admission Date', type: 'text', placeholder: '2024-01-15' },
              ].map(f => (
                <div className="input-group" key={f.key} style={{ marginBottom: 0 }}>
                  <label className="input-label">{f.label}</label>
                  <input type={f.type} placeholder={f.placeholder} value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
                </div>
              ))}
              <div className="input-group" style={{ marginBottom: 0 }}>
                <label className="input-label">Gender</label>
                <select value={form.gender} onChange={e => setForm({ ...form, gender: e.target.value })}>
                  <option>Male</option><option>Female</option><option>Other</option>
                </select>
              </div>
            </div>
            <div style={{ marginTop: '20px' }}>
              <button className="btn btn-emerald" onClick={addPatient} disabled={!form.name || !form.age}>Save Patient</button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="card loading-state"><div className="loading-spinner" /><span>Loading patients…</span></div>
        ) : (
          <div className="card" style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr><th>ID</th><th>Name</th><th>Age</th><th>Gender</th><th>Blood Type</th><th>Admission</th><th>Contact</th><th>Insurance</th></tr>
              </thead>
              <tbody>
                {patients.map(p => (
                  <tr key={p.id}>
                    <td style={{ color: 'var(--accent-cyan)', fontWeight: '700' }}>#{p.id}</td>
                    <td><strong>{p.name}</strong></td>
                    <td>{p.age}</td>
                    <td><span className="chip" style={{ background: `rgba(${p.gender === 'Male' ? '59,130,246' : '244,63,94'},0.15)`, color: GENDER_COLOR[p.gender] || '#ccc', border: `1px solid ${GENDER_COLOR[p.gender] || '#ccc'}40` }}>{p.gender}</span></td>
                    <td><span style={{ fontWeight: '700', color: '#f59e0b' }}>{p.blood_type}</span></td>
                    <td style={{ color: 'var(--text-secondary)' }}>{p.admission_date}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{p.contact}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{p.insurance_id}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
