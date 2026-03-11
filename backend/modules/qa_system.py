"""
Medical Research Assistant - Question Answering System
Retrieves relevant answers from the medical document corpus.
"""
import os
import sys
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import query_db, rows_to_dict


def build_passage_corpus():
    """Build passage-level corpus from DB for fine-grained QA."""
    papers = rows_to_dict(query_db(
        "SELECT id, title, abstract, authors, journal, year FROM Research_Papers"
    ))
    notes = rows_to_dict(query_db(
        "SELECT id, note_text, doctor_name, department, diagnosis FROM Clinical_Notes"
    ))
    diseases = rows_to_dict(query_db(
        "SELECT id, disease_name, description, symptoms, treatment FROM Diseases"
    ))

    passages = []

    # Research papers: split abstract into sentences
    for p in papers:
        abstract = p.get('abstract', '') or ''
        if abstract:
            sents = sent_tokenize(abstract)
            for i, sent in enumerate(sents):
                if len(sent.split()) > 5:
                    passages.append({
                        "text": sent,
                        "source_type": "Research Paper",
                        "source_title": p['title'],
                        "source_info": f"{p.get('authors','')}, {p.get('journal','')}, {p.get('year','')}",
                        "full_context": abstract[:400]
                    })

        # Also add full abstract as a passage
        passages.append({
            "text": abstract or p['title'],
            "source_type": "Research Paper",
            "source_title": p['title'],
            "source_info": f"{p.get('authors','')}, {p.get('journal','')}, {p.get('year','')}",
            "full_context": abstract[:500]
        })

    # Clinical notes: split into sentences
    for n in notes:
        note = n.get('note_text', '') or ''
        sents = sent_tokenize(note)
        for sent in sents:
            if len(sent.split()) > 6:
                passages.append({
                    "text": sent,
                    "source_type": "Clinical Note",
                    "source_title": f"Clinical Note - {n.get('diagnosis', 'Unknown')}",
                    "source_info": f"Dept: {n.get('department','')}, Dr. {n.get('doctor_name','')}",
                    "full_context": note[:400]
                })

    # Diseases: add description + symptoms + treatment as passages
    for d in diseases:
        for field in ['description', 'symptoms', 'treatment']:
            val = d.get(field, '') or ''
            if val and len(val.split()) > 5:
                passages.append({
                    "text": f"{d['disease_name']}: {val}",
                    "source_type": "Disease Database",
                    "source_title": d['disease_name'],
                    "source_info": "Medical Knowledge Base",
                    "full_context": f"Disease: {d['disease_name']}\nSymptoms: {d.get('symptoms','')}\nTreatment: {d.get('treatment','')}"
                })

    return passages


def answer_question(question, top_k=5):
    """Retrieve most relevant passages for the given question."""
    try:
        passages = build_passage_corpus()

        if not passages:
            return {
                "question": question,
                "answers": [],
                "status": "no_documents"
            }

        texts = [p["text"] for p in passages]
        all_texts = texts + [question]

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=8000,
            stop_words='english',
            sublinear_tf=True
        )
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        q_vec = tfidf_matrix[-1]
        doc_matrix = tfidf_matrix[:-1]

        scores = cosine_similarity(q_vec, doc_matrix)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]

        answers = []
        seen_texts = set()
        for idx in top_indices:
            if scores[idx] > 0.05:
                text = passages[idx]["text"]
                # Deduplicate
                text_key = text[:80]
                if text_key in seen_texts:
                    continue
                seen_texts.add(text_key)
                answers.append({
                    "answer": text,
                    "relevance": round(float(scores[idx]) * 100, 2),
                    "source_type": passages[idx]["source_type"],
                    "source_title": passages[idx]["source_title"],
                    "source_info": passages[idx]["source_info"],
                    "context": passages[idx]["full_context"]
                })

        return {
            "question": question,
            "answers": answers,
            "total_passages_searched": len(passages),
            "status": "success"
        }
    except Exception as e:
        return {"question": question, "answers": [], "error": str(e), "status": "error"}
