"""
Database seeding script for AI Healthcare Text Analytics Platform.
Populates Patients, Clinical_Notes, Diseases, and Research_Papers tables.
Works with BOTH MySQL and SQLite (auto-detected via db_utils).
"""
import os
import sys
import random
from datetime import datetime, timedelta

# Ensure db_utils is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import get_db, execute_db, query_db, _detect_backend

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def init_db():
    """Create tables if they don't exist (adapts syntax to MySQL or SQLite)."""
    _detect_backend()
    from database.db_utils import _USE_MYSQL

    if _USE_MYSQL:
        statements = [
            """CREATE TABLE IF NOT EXISTS Patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                age INT,
                gender VARCHAR(20),
                blood_type VARCHAR(10),
                admission_date VARCHAR(20),
                discharge_date VARCHAR(20),
                contact VARCHAR(50),
                insurance_id VARCHAR(50)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            """CREATE TABLE IF NOT EXISTS Clinical_Notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT,
                note_text TEXT NOT NULL,
                created_at DATETIME DEFAULT NOW(),
                doctor_name VARCHAR(100),
                department VARCHAR(100),
                diagnosis VARCHAR(200),
                severity VARCHAR(20),
                note_type VARCHAR(50),
                FOREIGN KEY (patient_id) REFERENCES Patients(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            """CREATE TABLE IF NOT EXISTS Diseases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                disease_name VARCHAR(200) NOT NULL,
                symptoms TEXT,
                severity VARCHAR(20),
                category VARCHAR(100),
                icd_code VARCHAR(20),
                description TEXT,
                treatment TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
            """CREATE TABLE IF NOT EXISTS Research_Papers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title TEXT NOT NULL,
                abstract TEXT,
                authors TEXT,
                journal VARCHAR(255),
                year INT,
                keywords TEXT,
                doi VARCHAR(100),
                citation_count INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
        ]
        conn = get_db()
        try:
            with conn.cursor() as cur:
                for stmt in statements:
                    cur.execute(stmt)
            conn.commit()
        finally:
            conn.close()
    else:
        # SQLite syntax
        statements = [
            """CREATE TABLE IF NOT EXISTS Patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, age INTEGER, gender TEXT,
                blood_type TEXT, admission_date TEXT, discharge_date TEXT,
                contact TEXT, insurance_id TEXT)""",
            """CREATE TABLE IF NOT EXISTS Clinical_Notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER REFERENCES Patients(id),
                note_text TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                doctor_name TEXT, department TEXT, diagnosis TEXT,
                severity TEXT, note_type TEXT)""",
            """CREATE TABLE IF NOT EXISTS Diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_name TEXT NOT NULL, symptoms TEXT, severity TEXT,
                category TEXT, icd_code TEXT, description TEXT, treatment TEXT)""",
            """CREATE TABLE IF NOT EXISTS Research_Papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, abstract TEXT, authors TEXT,
                journal TEXT, year INTEGER, keywords TEXT, doi TEXT,
                citation_count INTEGER DEFAULT 0)""",
        ]
        import sqlite3
        from database.db_utils import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        try:
            for stmt in statements:
                conn.execute(stmt)
            conn.commit()
        finally:
            conn.close()

    print("Database schema initialized.")


def seed_diseases():
    diseases = [
        ("Diabetes Mellitus Type 2", "increased thirst, frequent urination, fatigue, blurred vision, slow healing", "Moderate", "Endocrine", "E11", "A chronic condition affecting how the body metabolizes sugar.", "Metformin, insulin therapy, lifestyle changes"),
        ("Hypertension", "headache, dizziness, shortness of breath, chest pain, nosebleeds", "High", "Cardiovascular", "I10", "Persistently elevated blood pressure in arteries.", "ACE inhibitors, beta-blockers, lifestyle modification"),
        ("Pneumonia", "cough, fever, chills, chest pain, difficulty breathing, fatigue", "High", "Respiratory", "J18", "Infection that inflames air sacs in lungs.", "Antibiotics, antivirals, supportive care"),
        ("Myocardial Infarction", "chest pain, shortness of breath, sweating, nausea, arm pain", "Critical", "Cardiovascular", "I21", "Heart attack due to blocked coronary artery.", "Thrombolytics, PCI, aspirin, statins"),
        ("Rheumatoid Arthritis", "joint pain, swelling, stiffness, fatigue, fever, weight loss", "Moderate", "Musculoskeletal", "M05", "Autoimmune disease causing joint inflammation.", "DMARDs, NSAIDs, corticosteroids"),
        ("Chronic Kidney Disease", "fatigue, swelling, shortness of breath, confusion, nausea, decreased urination", "High", "Renal", "N18", "Gradual loss of kidney function over time.", "ACE inhibitors, dialysis, kidney transplant"),
        ("Asthma", "wheezing, shortness of breath, chest tightness, coughing, breathlessness", "Moderate", "Respiratory", "J45", "Chronic condition causing airway inflammation.", "Bronchodilators, corticosteroids, leukotriene modifiers"),
        ("Sepsis", "fever, rapid heart rate, rapid breathing, confusion, organ dysfunction", "Critical", "Infectious", "A41", "Life-threatening response to infection.", "IV antibiotics, vasopressors, supportive care"),
        ("Stroke", "sudden numbness, confusion, trouble speaking, vision problems, severe headache", "Critical", "Neurological", "I63", "Brain attack due to blocked or burst blood vessel.", "tPA, mechanical thrombectomy, rehabilitation"),
        ("Depression", "persistent sadness, loss of interest, fatigue, sleep changes, concentration difficulties", "Moderate", "Psychiatric", "F32", "Mental health disorder causing persistent low mood.", "Antidepressants, psychotherapy, lifestyle changes"),
        ("Alzheimer's Disease", "memory loss, confusion, difficulty planning, mood changes, personality changes", "High", "Neurological", "G30", "Progressive neurological disorder causing dementia.", "Cholinesterase inhibitors, memantine, supportive care"),
        ("Chronic Obstructive Pulmonary Disease", "chronic cough, mucus, shortness of breath, wheezing, chest tightness", "High", "Respiratory", "J44", "Progressive lung disease limiting airflow.", "Bronchodilators, steroids, oxygen therapy"),
        ("Hypothyroidism", "fatigue, weight gain, cold intolerance, constipation, dry skin, hair loss", "Low", "Endocrine", "E03", "Underactive thyroid gland producing insufficient hormones.", "Levothyroxine replacement therapy"),
        ("Urinary Tract Infection", "burning urination, frequent urination, cloudy urine, pelvic pain, fever", "Low", "Renal", "N39", "Bacterial infection of the urinary system.", "Antibiotics, increased fluid intake"),
        ("Migraine", "severe headache, nausea, vomiting, light sensitivity, visual aura", "Moderate", "Neurological", "G43", "Recurrent headaches of moderate to severe intensity.", "Triptans, NSAIDs, preventive medications"),
    ]
    row = query_db("SELECT COUNT(*) as c FROM Diseases", one=True)
    if (row or {}).get('c', 0) == 0:
        for d in diseases:
            execute_db("INSERT INTO Diseases (disease_name, symptoms, severity, category, icd_code, description, treatment) VALUES (?,?,?,?,?,?,?)", d)
        print(f"Seeded {len(diseases)} diseases.")


def seed_patients():
    names = ["Alice Johnson", "Bob Smith", "Carol White", "David Brown", "Emma Davis",
             "Frank Wilson", "Grace Lee", "Henry Martinez", "Isabella Taylor", "James Anderson",
             "Katherine Thomas", "Liam Jackson", "Mia Harris", "Noah Garcia", "Olivia Rodriguez",
             "Peter Lewis", "Quinn Walker", "Rachel Hall", "Samuel Young", "Tina Allen"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    genders = ["Male", "Female"]

    patients = []
    base_date = datetime(2023, 1, 1)
    for i, name in enumerate(names):
        age = random.randint(25, 80)
        admission = base_date + timedelta(days=random.randint(0, 365))
        discharge = admission + timedelta(days=random.randint(3, 30))
        patients.append((
            name, age, random.choice(genders),
            random.choice(blood_types),
            admission.strftime("%Y-%m-%d"),
            discharge.strftime("%Y-%m-%d"),
            f"+1-555-{random.randint(1000,9999):04d}",
            f"INS-{random.randint(10000, 99999)}"
        ))

    row = query_db("SELECT COUNT(*) as c FROM Patients", one=True)
    if (row or {}).get('c', 0) == 0:
        for p in patients:
            execute_db("INSERT INTO Patients (name, age, gender, blood_type, admission_date, discharge_date, contact, insurance_id) VALUES (?,?,?,?,?,?,?,?)", p)
        print(f"Seeded {len(patients)} patients.")


def seed_clinical_notes():
    notes_data = [
        (1, "Patient presents with increased thirst, frequent urination, fatigue, and blurred vision. Blood glucose level measured at 320 mg/dL. HbA1c is 9.2%. Patient has a family history of diabetes mellitus. Prescribed Metformin 500mg twice daily and recommended dietary modifications including low sugar intake.", "Dr. Sarah Mitchell", "Endocrinology", "Diabetes Mellitus Type 2", "Moderate", "Initial Consultation"),
        (2, "Patient reports persistent headache and dizziness for the past 3 weeks. Blood pressure reading: 165/105 mmHg. Electrocardiogram shows left ventricular hypertrophy. Patient is a smoker with sedentary lifestyle. Initiated antihypertensive therapy with lisinopril 10mg daily.", "Dr. Robert Chen", "Cardiology", "Hypertension", "High", "Follow-up"),
        (3, "Elderly patient admitted with high fever 39.8°C, productive cough with green sputum, and chest pain on breathing. Chest X-ray confirms right lower lobe consolidation. SpO2 88% on room air. Started on IV ceftriaxone and azithromycin. Patient requires supplemental oxygen.", "Dr. Emily Patel", "Pulmonology", "Pneumonia", "High", "Emergency Admission"),
        (4, "Patient presents with sudden onset severe chest pain radiating to left arm, associated with diaphoresis and shortness of breath. ECG shows ST-elevation in leads V1-V4. Troponin elevated at 2.4 ng/mL. Emergent PCI performed successfully. Aspirin and statin therapy initiated.", "Dr. Michael Torres", "Cardiology", "Myocardial Infarction", "Critical", "Emergency"),
        (5, "Patient with known rheumatoid arthritis presents for monthly follow-up. Reports morning stiffness lasting 2 hours with bilateral wrist and MCP joint swelling. ESR elevated at 78 mm/hr. CRP 45 mg/L. Methotrexate dose increased to 20mg weekly. Added hydroxychloroquine 400mg daily.", "Dr. Lisa Park", "Rheumatology", "Rheumatoid Arthritis", "Moderate", "Follow-up"),
        (6, "Patient with chronic kidney disease stage 3. eGFR declining from 42 to 35 mL/min over 6 months. Serum creatinine 2.1 mg/dL. Proteinuria present. Patient reports swelling in legs and decreased urine output. ACE inhibitor dose optimized. Referred to nephrology for dialysis planning.", "Dr. James Wilson", "Nephrology", "Chronic Kidney Disease", "High", "Monitoring"),
        (7, "Patient presents with acute asthma exacerbation triggered by dust exposure at work. Peak flow rate 45% of predicted. Oxygen saturation 91%. Administered nebulized salbutamol and ipratropium. IV methylprednisolone given. Patient stabilized after 2 hours. Revised inhaler technique education provided.", "Dr. Anna Rodriguez", "Pulmonology", "Asthma", "Moderate", "Emergency"),
        (8, "Post-surgical patient developed fever 38.9°C, tachycardia HR 128 bpm, and hypotension BP 88/56. Blood cultures drawn. Lactate elevated at 4.2 mmol/L. Suspected sepsis from wound infection. Fluid resuscitation with 2L normal saline. Broad spectrum antibiotics initiated immediately.", "Dr. David Kim", "Intensive Care", "Sepsis", "Critical", "Emergency"),
        (9, "Patient presents with sudden onset left-sided weakness, facial droop, and slurred speech. Symptoms onset 2 hours ago. NIHSS score 14. CT scan negative for hemorrhage. TPA thrombolysis administered within window. MRI confirms right MCA territory ischemia. Transferred to stroke unit.", "Dr. Nancy Brown", "Neurology", "Stroke", "Critical", "Emergency"),
        (10, "Patient presents with 6-month history of persistent sadness, anhedonia, sleep disturbances, and difficulty concentrating. PHQ-9 score 18 indicating severe depression. No suicidal ideation currently. Initiated sertraline 50mg daily. Referred for cognitive behavioral therapy. Follow-up in 4 weeks.", "Dr. Patricia Green", "Psychiatry", "Depression", "Moderate", "Initial Consultation"),
        (11, "76-year-old patient brought by family due to progressive memory loss over 2 years. MMSE score 18/30. Unable to recall recent events, repetitive questioning noted. CT brain shows cortical atrophy and hippocampal volume loss. Donepezil 5mg daily initiated. Caregiver education provided.", "Dr. Thomas Harris", "Neurology", "Alzheimer's Disease", "High", "Diagnosis"),
        (12, "Long-term smoker presents with worsening dyspnea on exertion, chronic productive cough, and wheezing. FEV1/FVC ratio 0.65, FEV1 55% predicted. Diagnosis of moderate COPD confirmed. Started tiotropium inhaler and salmeterol/fluticasone combination. Smoking cessation counseling provided.", "Dr. Catherine Moore", "Pulmonology", "Chronic Obstructive Pulmonary Disease", "High", "Diagnosis"),
        (13, "Patient presents with fatigue, weight gain of 8kg over 6 months, cold intolerance, constipation, and dry skin. TSH elevated at 12.5 mIU/L, free T4 low at 0.6 ng/dL. Thyroid ultrasound shows enlarged gland. Levothyroxine 75 mcg daily prescribed. Repeat TFTs in 6 weeks.", "Dr. Kevin Lee", "Endocrinology", "Hypothyroidism", "Low", "Diagnosis"),
        (14, "Female patient presents with dysuria, urinary frequency, suprapubic pain, and cloudy urine for 3 days. Urinalysis shows pyuria and bacteriuria. Nitrites positive. Urine culture sent. Trimethoprim-sulfamethoxazole prescribed empirically for 7 days. Patient advised high fluid intake.", "Dr. Rachel Adams", "Urology", "Urinary Tract Infection", "Low", "Initial Consultation"),
        (15, "Patient with 10-year history of migraines presents with typical aura preceding severe right-sided throbbing headache. Nausea and photophobia present. Current episode unresponsive to OTC analgesics. Sumatriptan 100mg administered with good response. Preventive therapy with propranolol 40mg daily initiated.", "Dr. Steven Clark", "Neurology", "Migraine", "Moderate", "Follow-up"),
        (16, "Patient with diabetes and hypertension presents for routine monitoring. HbA1c 8.1%, blood pressure 145/92 mmHg. Microalbuminuria detected. Ophthalmology review shows mild diabetic retinopathy. Medication regimen intensified. Nutritional counseling and exercise program recommended.", "Dr. Sarah Mitchell", "Endocrinology", "Diabetes Mellitus Type 2", "Moderate", "Routine Check"),
        (17, "Patient with history of hypertension presents with acute onset severe headache, confusion, and blood pressure 220/140 mmHg. Diagnosed with hypertensive crisis. IV labetalol infusion started. Neurological examination normal. ICU admission for close monitoring and gradual BP reduction.", "Dr. Robert Chen", "Cardiology", "Hypertension", "Critical", "Emergency"),
        (18, "Asthmatic patient follow-up. Well controlled on current regimen. FEV1 improved to 78% predicted. No nocturnal symptoms. Occasional rescue inhaler use. Step-down therapy considered. Patient education on trigger avoidance reinforced. Annual flu vaccine administered.", "Dr. Anna Rodriguez", "Pulmonology", "Asthma", "Low", "Follow-up"),
        (19, "Post-MI patient at 3-month follow-up. Ejection fraction improved from 35% to 48%. NYHA class II symptoms. Current medications: aspirin, clopidogrel, atorvastatin, metoprolol, ramipril. Cardiopulmonary rehabilitation completed. Return to light work approved. Echo in 6 months.", "Dr. Michael Torres", "Cardiology", "Myocardial Infarction", "Moderate", "Follow-up"),
        (20, "Patient with depression at 8-week follow-up. PHQ-9 score improved from 18 to 9. Tolerating sertraline 50mg well. Sleep and appetite improved. Still experiencing low motivation. Dose increased to 100mg. CBT sessions ongoing — reports finding them helpful.", "Dr. Patricia Green", "Psychiatry", "Depression", "Low", "Follow-up"),
    ]

    row = query_db("SELECT COUNT(*) as c FROM Clinical_Notes", one=True)
    if (row or {}).get('c', 0) == 0:
        for n in notes_data:
            execute_db("INSERT INTO Clinical_Notes (patient_id, note_text, doctor_name, department, diagnosis, severity, note_type) VALUES (?,?,?,?,?,?,?)", n)
        print(f"Seeded {len(notes_data)} clinical notes.")


def seed_research_papers():
    papers = [
        ("Deep Learning for Medical Image Analysis: A Survey", "This paper provides a comprehensive survey of deep learning methods applied to medical image analysis tasks including segmentation, detection, and classification across various imaging modalities such as MRI, CT, and X-ray.", "Litjens G, Kooi T, Bejnordi BE, et al.", "Medical Image Analysis", 2022, "deep learning, medical imaging, CNN, segmentation, classification, radiology", "10.1016/j.media.2022.001", 2847),
        ("BERT-based Clinical Named Entity Recognition for Electronic Health Records", "We present a BERT-based model fine-tuned on clinical text for named entity recognition of medical concepts including diseases, medications, symptoms, and procedures in electronic health records.", "Alsentzer E, Murphy J, Boag W, et al.", "ACL BioNLP Workshop", 2021, "NER, BERT, clinical NLP, EHR, medical entities, transformer", "10.18653/v1/W21-4913", 1203),
        ("Machine Learning Approaches for Disease Prediction: A Systematic Review", "A systematic review of machine learning algorithms including random forests, support vector machines, and neural networks applied to disease prediction tasks in clinical settings with evaluation metrics comparison.", "Johnson AE, Pollard TJ, Shen L, et al.", "Journal of Biomedical Informatics", 2020, "machine learning, disease prediction, random forest, SVM, classification, clinical", "10.1016/j.jbi.2020.103426", 892),
        ("Natural Language Processing in Healthcare: Current State and Future Directions", "This review examines the current applications of NLP in healthcare including clinical documentation, information extraction, patient communication, and decision support systems.", "Friedman C, Rindflesch TC, Corn M", "Journal of the American Medical Informatics Association", 2023, "NLP, healthcare, clinical documentation, information extraction, text mining", "10.1093/jamia/ocad023", 456),
        ("COVID-19 Treatment Outcomes: A Meta-Analysis of Clinical Trials", "Comprehensive meta-analysis of 127 randomized clinical trials examining treatment outcomes for COVID-19 patients including antiviral agents, corticosteroids, and supportive care protocols.", "Recovery Collaborative Group", "New England Journal of Medicine", 2021, "COVID-19, treatment, meta-analysis, clinical trial, antiviral, corticosteroids", "10.1056/NEJMoa2100854", 3421),
        ("Transformer Models for Clinical Text Classification", "We evaluate BERT, RoBERTa, and clinical domain-specific transformer models on multiple clinical text classification tasks including ICD coding, readmission prediction, and mortality prediction.", "Huang K, Altosaar J, Ranganath R", "Nature Machine Intelligence", 2022, "transformer, BERT, clinical text, ICD coding, classification, NLP", "10.1038/s42256-022-00439-x", 678),
        ("Electronic Health Records and Secondary Use: Opportunities and Challenges", "Analysis of opportunities for utilizing EHR data for secondary research purposes including population health management, pharmacovigilance, and clinical decision support with attention to privacy concerns.", "Safran C, Bloomrosen M, Hammond WE", "Journal of the American Medical Informatics Association", 2021, "EHR, secondary data use, privacy, population health, pharmacovigilance", "10.1093/jamia/ocab021", 234),
        ("Predicting Hospital Readmission with Machine Learning: A Multi-Site Study", "Multi-site study using gradient boosting, logistic regression, and deep learning to predict 30-day hospital readmission across 12 hospitals using structured and unstructured EHR data.", "Rajkomar A, Oren E, Chen K, et al.", "npj Digital Medicine", 2020, "readmission prediction, machine learning, gradient boosting, EHR, hospital outcomes", "10.1038/s41746-020-0291-8", 789),
        ("Medical Question Answering Using Knowledge Graphs", "A novel approach to medical question answering combining knowledge graph embedding with transformer-based language models to retrieve and rank medical answers from clinical guidelines.", "Zhang Y, Chen Q, Yang Z, et al.", "Bioinformatics", 2022, "question answering, knowledge graph, medical QA, NLP, clinical guidelines", "10.1093/bioinformatics/btac022", 312),
        ("Federated Learning for Privacy-Preserving Medical AI", "Framework for training machine learning models across multiple hospitals without sharing patient data, demonstrated on radiology report classification and clinical outcome prediction tasks.", "Rieke N, Hancox J, Li W, et al.", "npj Digital Medicine", 2020, "federated learning, privacy, medical AI, distributed training, healthcare", "10.1038/s41746-020-00323-1", 1567),
        ("Automatic Summarization of Medical Case Reports using Neural Networks", "Deep learning approach for automatic summarization of medical case reports using pointer-generator networks with coverage mechanism, evaluated on a new benchmark dataset of 5000 case reports.", "Zhang J, Zhao Y, Saleh M, Liu P", "EMNLP", 2021, "text summarization, medical case reports, neural networks, abstractive summarization", "10.18653/v1/2021.emnlp-main.823", 234),
        ("Clinical Decision Support Systems: A Review of Approaches and Evidence", "Comprehensive review of clinical decision support system architectures, including rule-based, ML-based, and hybrid approaches, with analysis of clinical impact across specialties.", "Berner ES, La Lande TJ", "Health Informatics Journal", 2023, "clinical decision support, CDSS, machine learning, rule-based system, evidence-based", "10.1177/14604582231189403", 445),
        ("Drug-Drug Interaction Prediction Using Graph Neural Networks", "Novel GNN-based framework for predicting drug-drug interactions using molecular structure graphs and clinical knowledge bases, achieving state-of-the-art performance on multiple benchmarks.", "Lin X, Quan Z, Wang ZJ, et al.", "Briefings in Bioinformatics", 2022, "drug interactions, graph neural network, pharmacology, molecular graph, prediction", "10.1093/bib/bbac103", 567),
        ("Survival Analysis with Machine Learning in Oncology", "Application of machine learning methods including Cox proportional hazards, random survival forests, and deep survival networks to predict patient survival in breast cancer, lung cancer, and leukemia cohorts.", "Katzman JL, Shaham U, Cloninger A, et al.", "BMC Medical Research Methodology", 2021, "survival analysis, machine learning, oncology, cancer prognosis, deep learning", "10.1186/s12874-021-01230-y", 891),
        ("Wearable Biosensors and AI for Continuous Health Monitoring", "Review of wearable biosensor technologies combined with machine learning algorithms for continuous monitoring of vital signs, glucose levels, and cardiac rhythms in ambulatory patients.", "Seshadri DR, Li RT, Voos JE, et al.", "npj Digital Medicine", 2023, "wearables, biosensors, IoT, health monitoring, machine learning, real-time", "10.1038/s41746-023-00789-2", 234),
    ]

    row = query_db("SELECT COUNT(*) as c FROM Research_Papers", one=True)
    if (row or {}).get('c', 0) == 0:
        for p in papers:
            execute_db("INSERT INTO Research_Papers (title, abstract, authors, journal, year, keywords, doi, citation_count) VALUES (?,?,?,?,?,?,?,?)", p)
        print(f"Seeded {len(papers)} research papers.")


def seed_all():
    init_db()
    seed_diseases()
    seed_patients()
    seed_clinical_notes()
    seed_research_papers()
    print("All data seeded successfully!")


if __name__ == "__main__":
    seed_all()
