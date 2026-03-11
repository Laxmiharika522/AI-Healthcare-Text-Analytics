"""
AI Healthcare Text Analytics Platform - Flask Backend
Main application entry point with all API routes.
"""
import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# ─── Initialize Database ───────────────────────────────────────────────────
from database.seed_data import seed_all
from database.db_utils import query_db, execute_db, rows_to_dict

def init_app():
    """Initialize database and seed data."""
    try:
        seed_all()
        print("Database ready.")
    except Exception as e:
        print(f"DB init warning: {e}")

# ─── Module Imports ────────────────────────────────────────────────────────
from modules.text_analyzer import analyze_text
from modules.disease_predictor import predict_disease, load_models
from modules.search_engine import search_documents
from modules.summarizer import summarize, summarize_with_sumy
from modules.qa_system import answer_question
from modules.analytics import get_all_analytics


# ──────────────────────────────────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "AI Healthcare Platform is running"})


# ──────────────────────────────────────────────────────────────────────────
# 1. Clinical Text Analyzer
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    text = data.get('text', '').strip()
    if len(text) < 10:
        return jsonify({"error": "Text too short"}), 400
    result = analyze_text(text)
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# 2. Disease Risk Prediction
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'symptoms' not in data:
        return jsonify({"error": "No symptoms provided"}), 400
    symptoms = data.get('symptoms', '').strip()
    model = data.get('model', 'random_forest')
    if len(symptoms) < 5:
        return jsonify({"error": "Please describe symptoms in more detail"}), 400
    result = predict_disease(symptoms, model_name=model)
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# 3. Medical Document Search
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "No search query provided"}), 400
    query = data.get('query', '').strip()
    top_k = data.get('top_k', 8)
    doc_type = data.get('doc_type', 'all')
    result = search_documents(query, top_k=top_k, doc_type=doc_type)
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# 4. Clinical Report Summarization
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/summarize', methods=['POST'])
def summarize_text():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    text = data.get('text', '').strip()
    num_sentences = data.get('num_sentences', 4)
    method = data.get('method', 'tfidf')
    if len(text) < 50:
        return jsonify({"error": "Text too short to summarize"}), 400
    if method == 'lsa' or method == 'lexrank':
        result = summarize_with_sumy(text, method=method, num_sentences=num_sentences)
    else:
        result = summarize(text, num_sentences=num_sentences)
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# 5. Medical Research Assistant (QA)
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/qa', methods=['POST'])
def qa():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "No question provided"}), 400
    question = data.get('question', '').strip()
    top_k = data.get('top_k', 5)
    if len(question) < 5:
        return jsonify({"error": "Question too short"}), 400
    result = answer_question(question, top_k=top_k)
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# 6. Analytics Dashboard
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/analytics', methods=['GET'])
def analytics():
    result = get_all_analytics()
    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# 7. Patients CRUD
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/patients', methods=['GET'])
def get_patients():
    patients = rows_to_dict(query_db("SELECT * FROM Patients ORDER BY id"))
    return jsonify({"patients": patients, "total": len(patients)})


@app.route('/api/patients', methods=['POST'])
def add_patient():
    data = request.get_json()
    required = ['name', 'age', 'gender']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields: name, age, gender"}), 400
    pid = execute_db(
        "INSERT INTO Patients (name, age, gender, blood_type, admission_date, contact) VALUES (?,?,?,?,?,?)",
        (data['name'], data['age'], data['gender'],
         data.get('blood_type', ''), data.get('admission_date', ''), data.get('contact', ''))
    )
    return jsonify({"message": "Patient added", "id": pid}), 201


# ──────────────────────────────────────────────────────────────────────────
# 8. Research Papers
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/papers', methods=['GET'])
def get_papers():
    papers = rows_to_dict(query_db("SELECT * FROM Research_Papers ORDER BY year DESC"))
    return jsonify({"papers": papers, "total": len(papers)})


# ──────────────────────────────────────────────────────────────────────────
# 9. Clinical Notes
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = rows_to_dict(query_db("""
        SELECT cn.*, p.name as patient_name
        FROM Clinical_Notes cn
        LEFT JOIN Patients p ON cn.patient_id = p.id
        ORDER BY cn.id DESC
    """))
    return jsonify({"notes": notes, "total": len(notes)})


@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.get_json()
    if not data or 'note_text' not in data:
        return jsonify({"error": "note_text required"}), 400
    nid = execute_db(
        """INSERT INTO Clinical_Notes (patient_id, note_text, doctor_name, department, diagnosis, severity, note_type)
           VALUES (?,?,?,?,?,?,?)""",
        (data.get('patient_id'), data['note_text'], data.get('doctor_name', ''),
         data.get('department', ''), data.get('diagnosis', ''),
         data.get('severity', ''), data.get('note_type', 'General'))
    )
    return jsonify({"message": "Note added", "id": nid}), 201


# ──────────────────────────────────────────────────────────────────────────
# 10. Diseases
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    diseases = rows_to_dict(query_db("SELECT * FROM Diseases ORDER BY disease_name"))
    return jsonify({"diseases": diseases, "total": len(diseases)})


# ──────────────────────────────────────────────────────────────────────────
# 11. Document Upload
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower()

    if ext == 'txt':
        text = file.read().decode('utf-8', errors='ignore')
        return jsonify({
            "filename": secure_filename(file.filename),
            "text": text,
            "length": len(text),
            "status": "success"
        })
    else:
        return jsonify({"error": "Only .txt files supported for upload. Please copy-paste other document types."}), 400


# ──────────────────────────────────────────────────────────────────────────
# 12. Seed / Reset DB
# ──────────────────────────────────────────────────────────────────────────
@app.route('/api/seed', methods=['POST'])
def seed_database():
    try:
        seed_all()
        return jsonify({"message": "Database seeded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    init_app()
    print("Starting AI Healthcare Text Analytics Platform...")
    print("Backend running at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
