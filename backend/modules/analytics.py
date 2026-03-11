"""
Analytics Module
Provides 10+ complex SQL/Pandas queries for dashboard visualizations.
"""
import os
import sys
import pandas as pd
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import query_db, rows_to_dict, DB_PATH


def get_dataframes():
    """Load all tables into Pandas DataFrames."""
    conn = sqlite3.connect(DB_PATH)
    patients_df = pd.read_sql("SELECT * FROM Patients", conn)
    notes_df = pd.read_sql("SELECT * FROM Clinical_Notes", conn)
    diseases_df = pd.read_sql("SELECT * FROM Diseases", conn)
    papers_df = pd.read_sql("SELECT * FROM Research_Papers", conn)
    conn.close()
    return patients_df, notes_df, diseases_df, papers_df


def safe_query(fn):
    """Wrapper for safe query execution."""
    try:
        result = fn()
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"data": [], "status": "error", "error": str(e)}


# ──────────────────────────────────────────────
# Query 1: Most Common Diseases in Clinical Notes
# ──────────────────────────────────────────────
def most_common_diseases():
    def fn():
        rows = query_db("""
            SELECT diagnosis, COUNT(*) as count
            FROM Clinical_Notes
            WHERE diagnosis IS NOT NULL AND diagnosis != ''
            GROUP BY diagnosis
            ORDER BY count DESC
            LIMIT 10
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 2: Most Frequent Symptoms (from Diseases table)
# ──────────────────────────────────────────────
def most_frequent_symptoms():
    def fn():
        _, _, diseases_df, _ = get_dataframes()
        all_symptoms = []
        for syms in diseases_df['symptoms'].dropna():
            for s in [x.strip() for x in syms.split(',')]:
                if s:
                    all_symptoms.append(s.lower())
        from collections import Counter
        counts = Counter(all_symptoms).most_common(12)
        return [{"symptom": s, "count": c} for s, c in counts]
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 3: Patient Age Distribution (Risk Groups)
# ──────────────────────────────────────────────
def patient_age_distribution():
    def fn():
        patients_df, _, _, _ = get_dataframes()
        bins = [0, 30, 45, 60, 75, 100]
        labels = ['<30', '30-45', '45-60', '60-75', '75+']
        patients_df['age_group'] = pd.cut(patients_df['age'], bins=bins, labels=labels)
        dist = patients_df['age_group'].value_counts().reset_index()
        dist.columns = ['age_group', 'count']
        dist = dist.sort_values('age_group')
        return dist.to_dict('records')
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 4: Disease Trend Over Time (Monthly Clinical Notes)
# ──────────────────────────────────────────────
def disease_trend_over_time():
    def fn():
        rows = query_db("""
            SELECT 
                strftime('%Y-%m', created_at) as month,
                diagnosis,
                COUNT(*) as count
            FROM Clinical_Notes
            WHERE created_at IS NOT NULL AND diagnosis IS NOT NULL
            GROUP BY month, diagnosis
            ORDER BY month
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 5: Average Patient Age by Disease Category
# ──────────────────────────────────────────────
def avg_age_by_disease_category():
    def fn():
        rows = query_db("""
            SELECT d.category, ROUND(AVG(p.age), 1) as avg_age, COUNT(*) as patient_count
            FROM Clinical_Notes cn
            JOIN Patients p ON cn.patient_id = p.id
            JOIN Diseases d ON d.disease_name = cn.diagnosis
            GROUP BY d.category
            ORDER BY avg_age DESC
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 6: Top Doctors by Number of Clinical Notes
# ──────────────────────────────────────────────
def top_doctors_by_notes():
    def fn():
        rows = query_db("""
            SELECT doctor_name, COUNT(*) as note_count, 
                   COUNT(DISTINCT patient_id) as unique_patients,
                   department
            FROM Clinical_Notes
            WHERE doctor_name IS NOT NULL
            GROUP BY doctor_name
            ORDER BY note_count DESC
            LIMIT 10
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 7: Research Papers per Year
# ──────────────────────────────────────────────
def papers_per_year():
    def fn():
        rows = query_db("""
            SELECT year, COUNT(*) as paper_count, 
                   SUM(citation_count) as total_citations
            FROM Research_Papers
            WHERE year IS NOT NULL
            GROUP BY year
            ORDER BY year
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 8: Disease Severity Distribution
# ──────────────────────────────────────────────
def disease_severity_distribution():
    def fn():
        rows = query_db("""
            SELECT severity, COUNT(*) as count
            FROM Diseases
            WHERE severity IS NOT NULL
            GROUP BY severity
            ORDER BY 
                CASE severity
                    WHEN 'Critical' THEN 1
                    WHEN 'High' THEN 2
                    WHEN 'Moderate' THEN 3
                    WHEN 'Low' THEN 4
                END
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 9: Department-wise Severity Analysis
# ──────────────────────────────────────────────
def department_severity_analysis():
    def fn():
        rows = query_db("""
            SELECT department, severity, COUNT(*) as count
            FROM Clinical_Notes
            WHERE department IS NOT NULL AND severity IS NOT NULL
            GROUP BY department, severity
            ORDER BY department, severity
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 10: Patient Gender Distribution
# ──────────────────────────────────────────────
def patient_gender_distribution():
    def fn():
        rows = query_db("""
            SELECT gender, COUNT(*) as count, ROUND(AVG(age), 1) as avg_age
            FROM Patients
            GROUP BY gender
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 11: Note Types Distribution
# ──────────────────────────────────────────────
def note_type_distribution():
    def fn():
        rows = query_db("""
            SELECT note_type, COUNT(*) as count
            FROM Clinical_Notes
            WHERE note_type IS NOT NULL
            GROUP BY note_type
            ORDER BY count DESC
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 12: Most Cited Research Papers
# ──────────────────────────────────────────────
def most_cited_papers():
    def fn():
        rows = query_db("""
            SELECT title, authors, journal, year, citation_count
            FROM Research_Papers
            ORDER BY citation_count DESC
            LIMIT 8
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 13: Disease Categories with Most Diseases
# ──────────────────────────────────────────────
def diseases_by_category():
    def fn():
        rows = query_db("""
            SELECT category, COUNT(*) as disease_count
            FROM Diseases
            GROUP BY category
            ORDER BY disease_count DESC
        """)
        return rows_to_dict(rows)
    return safe_query(fn)


# ──────────────────────────────────────────────
# Query 14: Summary Statistics
# ──────────────────────────────────────────────
def summary_statistics():
    def fn():
        total_patients = query_db("SELECT COUNT(*) as c FROM Patients", one=True)['c']
        total_notes = query_db("SELECT COUNT(*) as c FROM Clinical_Notes", one=True)['c']
        total_diseases = query_db("SELECT COUNT(*) as c FROM Diseases", one=True)['c']
        total_papers = query_db("SELECT COUNT(*) as c FROM Research_Papers", one=True)['c']
        avg_age = query_db("SELECT ROUND(AVG(age), 1) as c FROM Patients", one=True)['c']
        critical_cases = query_db("SELECT COUNT(*) as c FROM Clinical_Notes WHERE severity='Critical'", one=True)['c']
        return {
            "total_patients": total_patients,
            "total_clinical_notes": total_notes,
            "total_diseases": total_diseases,
            "total_research_papers": total_papers,
            "average_patient_age": avg_age,
            "critical_cases": critical_cases
        }
    return safe_query(fn)


def get_all_analytics():
    """Run all analytics queries and return combined results."""
    return {
        "summary": summary_statistics(),
        "most_common_diseases": most_common_diseases(),
        "most_frequent_symptoms": most_frequent_symptoms(),
        "patient_age_distribution": patient_age_distribution(),
        "disease_trend": disease_trend_over_time(),
        "avg_age_by_disease_category": avg_age_by_disease_category(),
        "top_doctors": top_doctors_by_notes(),
        "papers_per_year": papers_per_year(),
        "disease_severity": disease_severity_distribution(),
        "department_severity": department_severity_analysis(),
        "patient_gender": patient_gender_distribution(),
        "note_types": note_type_distribution(),
        "most_cited_papers": most_cited_papers(),
        "diseases_by_category": diseases_by_category(),
    }
