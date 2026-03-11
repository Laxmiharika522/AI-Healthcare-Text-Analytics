"""
Medical Document Search Engine
Implements TF-IDF + cosine similarity information retrieval
over research papers and clinical notes.
"""
import os
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database.db_utils import query_db, rows_to_dict


def build_corpus():
    """Build document corpus from database."""
    papers = rows_to_dict(query_db("SELECT id, title, abstract, authors, journal, year, keywords FROM Research_Papers"))
    notes = rows_to_dict(query_db("SELECT id, note_text, doctor_name, department, diagnosis FROM Clinical_Notes"))

    documents = []
    for p in papers:
        text = f"{p['title']} {p.get('abstract','') or ''} {p.get('keywords','') or ''}"
        documents.append({
            "id": f"paper_{p['id']}",
            "type": "Research Paper",
            "title": p['title'],
            "content": text,
            "metadata": {
                "authors": p.get('authors', ''),
                "journal": p.get('journal', ''),
                "year": p.get('year', ''),
                "keywords": p.get('keywords', '')
            }
        })

    for n in notes:
        text = f"{n.get('diagnosis','') or ''} {n['note_text']}"
        documents.append({
            "id": f"note_{n['id']}",
            "type": "Clinical Note",
            "title": f"Clinical Note - {n.get('diagnosis','Unknown')} ({n.get('department','General')})",
            "content": text,
            "metadata": {
                "doctor": n.get('doctor_name', ''),
                "department": n.get('department', ''),
                "diagnosis": n.get('diagnosis', '')
            }
        })

    return documents


def search_documents(query, top_k=8, doc_type="all"):
    """Search documents using TF-IDF cosine similarity."""
    try:
        corpus = build_corpus()

        if doc_type == "papers":
            corpus = [d for d in corpus if d["type"] == "Research Paper"]
        elif doc_type == "notes":
            corpus = [d for d in corpus if d["type"] == "Clinical Note"]

        if not corpus:
            return {"results": [], "query": query, "total": 0, "status": "no_documents"}

        texts = [doc["content"] for doc in corpus]
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            stop_words='english',
            sublinear_tf=True
        )

        tfidf_matrix = vectorizer.fit_transform(texts)
        query_vec = vectorizer.transform([query])
        scores = cosine_similarity(query_vec, tfidf_matrix)[0]

        # Get top-k results
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.01:
                doc = corpus[idx].copy()
                doc['relevance_score'] = round(float(scores[idx]) * 100, 2)
                doc.pop('content', None)  # Remove raw content from response
                results.append(doc)

        return {
            "results": results,
            "query": query,
            "total": len(results),
            "corpus_size": len(corpus),
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e), "status": "error", "results": []}
