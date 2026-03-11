"""
Clinical Text Analyzer Module
Performs NLP preprocessing and Named Entity Recognition on medical text.
"""
import re
import string

# NLTK imports
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Download required NLTK data
def download_nltk_data():
    resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

download_nltk_data()

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# Medical entity dictionaries
MEDICAL_ENTITIES = {
    "diseases": [
        "diabetes", "hypertension", "pneumonia", "myocardial infarction", "heart attack",
        "arthritis", "asthma", "sepsis", "stroke", "depression", "alzheimer","alzheimer's",
        "copd", "hypothyroidism", "uti", "migraine", "cancer", "tumor", "leukemia",
        "hepatitis", "cirrhosis", "nephritis", "anemia", "osteoporosis", "dementia",
        "parkinson", "epilepsy", "schizophrenia", "obesity", "malaria", "tuberculosis"
    ],
    "symptoms": [
        "pain", "fever", "cough", "fatigue", "headache", "nausea", "vomiting",
        "dizziness", "shortness of breath", "dyspnea", "chest pain", "palpitations",
        "weight loss", "weight gain", "swelling", "edema", "rash", "itching",
        "diarrhea", "constipation", "insomnia", "anxiety", "confusion", "memory loss",
        "blurred vision", "tinnitus", "numbness", "weakness", "stiffness", "trauma"
    ],
    "medications": [
        "metformin", "insulin", "aspirin", "lisinopril", "atorvastatin", "metoprolol",
        "amoxicillin", "ceftriaxone", "azithromycin", "ibuprofen", "acetaminophen",
        "warfarin", "heparin", "clopidogrel", "sertraline", "fluoxetine", "donepezil",
        "levothyroxine", "prednisone", "omeprazole", "losartan", "ramipril", "furosemide",
        "salbutamol", "tiotropium", "albuterol", "sumatriptan", "methotrexate", "adalimumab"
    ],
    "treatments": [
        "surgery", "chemotherapy", "radiation", "dialysis", "transplant", "physiotherapy",
        "psychotherapy", "immunotherapy", "pci", "thrombolysis", "intubation",
        "ventilation", "rehabilitation", "catheterization", "biopsy", "endoscopy",
        "colonoscopy", "ct scan", "mri", "ecg", "echocardiogram", "ultrasound",
        "blood transfusion", "iv therapy", "oxygen therapy", "nebulization"
    ],
    "anatomy": [
        "heart", "lung", "liver", "kidney", "brain", "blood", "artery", "vein",
        "muscle", "bone", "joint", "skin", "stomach", "intestine", "pancreas",
        "thyroid", "adrenal", "prostate", "uterus", "bladder", "colon", "spine"
    ],
    "measurements": [
        "blood pressure", "heart rate", "temperature", "glucose", "hemoglobin",
        "cholesterol", "creatinine", "bmi", "oxygen saturation", "spo2",
        "hba1c", "troponin", "esr", "crp", "egfr", "inr", "platelet"
    ]
}


def preprocess_text(text):
    """Full NLP preprocessing pipeline."""
    # Tokenize sentences
    sentences = sent_tokenize(text)
    # Tokenize words
    tokens = word_tokenize(text.lower())
    # Remove punctuation
    tokens_clean = [t for t in tokens if t not in string.punctuation and t.isalpha()]
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    # Keep important medical stop words
    medical_keep = {'not', 'no', 'without', 'with', 'few', 'less', 'more', 'high', 'low'}
    filtered = [t for t in tokens_clean if t not in stop_words or t in medical_keep]
    # Stem
    stemmed = [stemmer.stem(t) for t in filtered]
    # Lemmatize
    lemmatized = [lemmatizer.lemmatize(t) for t in filtered]

    return {
        "original_text": text,
        "sentence_count": len(sentences),
        "sentences": sentences,
        "word_count": len(word_tokenize(text)),
        "tokens": tokens_clean[:50],
        "filtered_tokens": filtered[:50],
        "stemmed": stemmed[:30],
        "lemmatized": lemmatized[:30]
    }


def extract_entities(text):
    """Extract medical entities using dictionary-based NER."""
    text_lower = text.lower()
    found_entities = {cat: [] for cat in MEDICAL_ENTITIES}

    for category, terms in MEDICAL_ENTITIES.items():
        for term in terms:
            # Use word boundary matching
            pattern = r'\b' + re.escape(term) + r'\b'
            matches = re.findall(pattern, text_lower)
            if matches:
                # Find the original casing
                orig_pattern = re.compile(pattern, re.IGNORECASE)
                orig_matches = orig_pattern.findall(text)
                if orig_matches:
                    found_entities[category].append({
                        "entity": orig_matches[0],
                        "normalized": term,
                        "count": len(matches)
                    })

    # Also try SpaCy if available
    spacy_entities = extract_spacy_entities(text)

    # Stats
    total_entities = sum(len(v) for v in found_entities.values())

    return {
        "entities": found_entities,
        "spacy_entities": spacy_entities,
        "total_entities": total_entities,
        "entity_summary": {cat: len(entities) for cat, entities in found_entities.items()}
    }


def extract_spacy_entities(text):
    """Try SpaCy NER extraction."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            return []
        doc = nlp(text[:5000])  # Limit text length
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "description": spacy.explain(ent.label_) or ent.label_
            })
        return entities
    except Exception:
        return []


def analyze_text(text):
    """Main analysis function combining preprocessing and NER."""
    if not text or len(text.strip()) < 10:
        return {"error": "Text too short for analysis"}

    preprocessing = preprocess_text(text)
    entities = extract_entities(text)

    # Word frequency (top 10 non-stopword words)
    stop_words = set(stopwords.words('english'))
    words = [w.lower() for w in word_tokenize(text) if w.isalpha() and w.lower() not in stop_words and len(w) > 3]
    from collections import Counter
    word_freq = Counter(words).most_common(10)

    return {
        "preprocessing": preprocessing,
        "entities": entities,
        "word_frequency": word_freq,
        "text_length": len(text),
        "status": "success"
    }
