"""
Disease Risk Prediction Module
Trains and runs ML models to predict diseases from symptom text.
Uses Logistic Regression, Random Forest, and XGBoost.
"""
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

# Training dataset: symptom descriptions → disease labels
TRAINING_DATA = [
    # Diabetes
    ("increased thirst frequent urination fatigue blurred vision slow healing weight loss", "Diabetes Mellitus Type 2"),
    ("polyuria polydipsia fatigue hyperglycemia weight loss nocturia", "Diabetes Mellitus Type 2"),
    ("high blood sugar frequent urination excessive hunger tingling hands feet", "Diabetes Mellitus Type 2"),
    ("glucose elevated hba1c fatigue blurred vision wounds slow healing", "Diabetes Mellitus Type 2"),
    ("insulin resistance obesity abdominal fat frequent urination thirst", "Diabetes Mellitus Type 2"),

    # Hypertension
    ("headache dizziness shortness of breath chest pain nosebleeds", "Hypertension"),
    ("high blood pressure severe headache visual changes palpitations", "Hypertension"),
    ("elevated blood pressure diziness fatigue headache red face", "Hypertension"),
    ("persistent headache blurred vision nausea breathlessness", "Hypertension"),
    ("blood pressure high hypertension headache irregular heartbeat", "Hypertension"),

    # Pneumonia
    ("cough fever chills chest pain difficulty breathing fatigue sputum", "Pneumonia"),
    ("productive cough high fever dyspnea consolidation chest x-ray", "Pneumonia"),
    ("respiratory infection fever cough breathlessness pleural effusion", "Pneumonia"),
    ("pneumonia fever cough mucus breathing difficulty infection lungs", "Pneumonia"),
    ("bacterial infection lung fever sputum cough low oxygen saturation", "Pneumonia"),

    # Myocardial Infarction
    ("chest pain arm pain sweating nausea shortness of breath heart attack", "Myocardial Infarction"),
    ("severe chest pressure radiating left arm jaw sweating cardiac", "Myocardial Infarction"),
    ("troponin elevated st elevation chest tightness breathing difficulty", "Myocardial Infarction"),
    ("crushing chest pain diaphoresis pain jaw nausea cardiac event", "Myocardial Infarction"),
    ("coronary artery blockage chest pain sudden breathlessness weakness", "Myocardial Infarction"),

    # Rheumatoid Arthritis
    ("joint pain swelling stiffness morning fatigue fever weight loss", "Rheumatoid Arthritis"),
    ("symmetric joint inflammation morning stiffness elevated esr crp", "Rheumatoid Arthritis"),
    ("arthritis wrist fingers swelling pain rheumatoid factor positive", "Rheumatoid Arthritis"),
    ("autoimmune joint disease pain swelling rheumatoid inflammation", "Rheumatoid Arthritis"),
    ("stiff swollen joints fatigue anemia rheumatoid nodules", "Rheumatoid Arthritis"),

    # Chronic Kidney Disease
    ("fatigue swelling shortness of breath confusion nausea decreased urination", "Chronic Kidney Disease"),
    ("elevated creatinine decreased egfr proteinuria edema hypertension", "Chronic Kidney Disease"),
    ("kidney failure fatigue anemia electrolyte imbalance fluid retention", "Chronic Kidney Disease"),
    ("renal failure urine output decreased creatinine high edema", "Chronic Kidney Disease"),
    ("chronic kidney disease uremia fatigue nausea anemia fluid overload", "Chronic Kidney Disease"),

    # Asthma
    ("wheezing shortness of breath chest tightness coughing breathlessness", "Asthma"),
    ("bronchospasm dyspnea wheeze nocturnal cough trigger allergen", "Asthma"),
    ("asthma attack shortness breath wheezing rescue inhaler", "Asthma"),
    ("airway inflammation bronchial hyperreactivity cough wheeze dyspnea", "Asthma"),
    ("breathlessness exercise induced cough nighttime wheeze asthma", "Asthma"),

    # Sepsis
    ("fever rapid heart rate rapid breathing confusion organ failure", "Sepsis"),
    ("tachycardia hypotension fever bacteremia lactate elevated shock", "Sepsis"),
    ("infection systemic response fever tachyarrhythmia hypotension organ dysfunction", "Sepsis"),
    ("septicemia high fever rapid breathing low blood pressure confusion", "Sepsis"),
    ("blood infection fever altered consciousness low blood pressure fast heart", "Sepsis"),

    # Stroke
    ("sudden numbness confusion trouble speaking vision problems severe headache", "Stroke"),
    ("facial droop arm weakness speech difficulty sudden onset neurological", "Stroke"),
    ("ischemic stroke hemiplegia aphasia sudden weakness ct scan", "Stroke"),
    ("sudden confusion slurred speech one sided weakness loss balance", "Stroke"),
    ("brain attack sudden severe headache vision loss weakness face", "Stroke"),

    # Depression
    ("persistent sadness loss of interest fatigue sleep disturbance concentration", "Depression"),
    ("anhedonia insomnia fatigue hopelessness worthlessness depression", "Depression"),
    ("low mood loss pleasure energy changes appetite sleep depression", "Depression"),
    ("depressive episode sadness crying fatigue cognitive impairment", "Depression"),
    ("major depression persistent sadness hopeless energy low suicidal", "Depression"),

    # Alzheimer
    ("memory loss confusion difficulty planning mood changes personality changes", "Alzheimer's Disease"),
    ("dementia memory impairment confusion disorientation cognitive decline", "Alzheimer's Disease"),
    ("progressive forgetfulness confusion agitation cognitive loss", "Alzheimer's Disease"),
    ("short term memory loss confusion repetition behavioral changes alzheimer", "Alzheimer's Disease"),
    ("neurodegeneration memory loss disorientation behavioral change", "Alzheimer's Disease"),

    # COPD
    ("chronic cough mucus shortness of breath wheezing chest tightness", "COPD"),
    ("emphysema chronic bronchitis dyspnea cough sputum fev1 low", "COPD"),
    ("airflow obstruction cough phlegm breathlessness exacerbation smoking", "COPD"),
    ("pulmonary disease wheezing breathlessness productive cough exacerbation", "COPD"),
    ("forced expiratory volume reduced cough dyspnea chronic respiratory", "COPD"),

    # Hypothyroidism
    ("fatigue weight gain cold intolerance constipation dry skin hair loss", "Hypothyroidism"),
    ("low thyroid tsh elevated fatigue slow metabolism constipation cold", "Hypothyroidism"),
    ("underactive thyroid weight gain fatigue depression cold intolerance", "Hypothyroidism"),
    ("hypothyroidism myxedema dry skin bradycardia fatigue weight gain", "Hypothyroidism"),
    ("thyroid deficiency fatigue cold hands weight gain slow heartbeat", "Hypothyroidism"),

    # UTI
    ("burning urination frequent urination cloudy urine pelvic pain fever", "Urinary Tract Infection"),
    ("dysuria frequency urgency pyuria bacteriuria cloudy urine", "Urinary Tract Infection"),
    ("urinary frequency burning sensation cloudy smelly urine fever", "Urinary Tract Infection"),
    ("bladder infection pain urination frequent trips bathroom", "Urinary Tract Infection"),
    ("uti burning urination frequent cloudy urine discomfort suprapubic", "Urinary Tract Infection"),

    # Migraine 
    ("severe headache nausea vomiting light sensitivity visual aura", "Migraine"),
    ("throbbing headache photophobia phonophobia aura migraine", "Migraine"),
    ("unilateral headache nausea vomiting sensitivity light sound", "Migraine"),
    ("pulsating headache aura nausea photophobia hours long", "Migraine"),
    ("migraine attack severe headache vomiting visual disturbance", "Migraine"),
]


models = {}
vectorizer = None
label_encoder = None


def train_models():
    """Train all ML models and save them."""
    global models, vectorizer, label_encoder

    texts = [d[0] for d in TRAINING_DATA]
    labels = [d[1] for d in TRAINING_DATA]

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=500)
    X = vectorizer.fit_transform(texts)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Logistic Regression
    lr = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    lr.fit(X_train, y_train)
    models['logistic_regression'] = lr

    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    models['random_forest'] = rf

    # XGBoost
    if HAS_XGB:
        xgb = XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss', use_label_encoder=False)
        xgb.fit(X_train, y_train)
        models['xgboost'] = xgb

    # Save
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, 'vectorizer.pkl'))
    joblib.dump(label_encoder, os.path.join(MODEL_DIR, 'label_encoder.pkl'))
    for name, model in models.items():
        joblib.dump(model, os.path.join(MODEL_DIR, f'{name}.pkl'))

    print(f"Models trained and saved. Classes: {list(label_encoder.classes_)}")
    return True


def load_models():
    """Load saved models or train if not available."""
    global models, vectorizer, label_encoder
    vec_path = os.path.join(MODEL_DIR, 'vectorizer.pkl')

    if os.path.exists(vec_path):
        vectorizer = joblib.load(vec_path)
        label_encoder = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))
        for name in ['logistic_regression', 'random_forest', 'xgboost']:
            path = os.path.join(MODEL_DIR, f'{name}.pkl')
            if os.path.exists(path):
                models[name] = joblib.load(path)
    else:
        train_models()


def predict_disease(symptom_text, model_name='random_forest'):
    """Predict diseases from symptom text with probability scores."""
    global models, vectorizer, label_encoder

    if not models:
        load_models()

    if model_name not in models:
        model_name = list(models.keys())[0]

    model = models[model_name]
    X = vectorizer.transform([symptom_text.lower()])

    # Get probabilities
    proba = model.predict_proba(X)[0]
    classes = label_encoder.classes_

    # Sort by probability descending, take top 5
    top_indices = np.argsort(proba)[::-1][:5]
    predictions = []
    for idx in top_indices:
        if proba[idx] > 0.01:
            predictions.append({
                "disease": classes[idx],
                "probability": round(float(proba[idx]) * 100, 2),
                "risk_level": "High" if proba[idx] > 0.5 else "Moderate" if proba[idx] > 0.2 else "Low"
            })

    # Get results from all available models for comparison
    all_model_results = {}
    for mname, mmodel in models.items():
        mp = mmodel.predict_proba(X)[0]
        top_idx = np.argsort(mp)[::-1][0]
        all_model_results[mname] = {
            "prediction": classes[top_idx],
            "confidence": round(float(mp[top_idx]) * 100, 2)
        }

    return {
        "predictions": predictions,
        "model_used": model_name,
        "all_models": all_model_results,
        "available_models": list(models.keys()),
        "status": "success"
    }


# Initialize models on import
try:
    load_models()
except Exception as e:
    print(f"Warning: Could not load models on import: {e}")
