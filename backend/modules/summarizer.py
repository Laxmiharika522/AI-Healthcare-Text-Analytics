"""
Clinical Report Summarizer Module
Implements extractive summarization using TF-IDF sentence scoring.
"""
import re
import math
from collections import Counter

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


def _tfidf_sentence_scores(sentences, stop_words):
    """Score sentences using TF-IDF idea at sentence level."""
    # Build word frequencies across all sentences
    word_freq = Counter()
    for sent in sentences:
        words = [w.lower() for w in word_tokenize(sent)
                 if w.isalpha() and w.lower() not in stop_words and len(w) > 2]
        word_freq.update(words)

    # Avoid division by zero
    max_freq = max(word_freq.values()) if word_freq else 1

    # Score each sentence
    scores = {}
    for i, sent in enumerate(sentences):
        words = [w.lower() for w in word_tokenize(sent)
                 if w.isalpha() and w.lower() not in stop_words and len(w) > 2]
        if not words:
            scores[i] = 0
            continue

        # TF contribution
        tf_score = sum(word_freq.get(w, 0) / max_freq for w in words) / len(words)

        # Position bonus (first and last sentences tend to be important)
        n = len(sentences)
        position_bonus = 0
        if n > 1:
            if i == 0:
                position_bonus = 0.3
            elif i == n - 1:
                position_bonus = 0.1
            elif i < n * 0.2:
                position_bonus = 0.15

        # Sentence length penalty (penalize very short/long sentences)
        length_factor = 1.0
        if len(words) < 5:
            length_factor = 0.6
        elif len(words) > 50:
            length_factor = 0.8

        scores[i] = (tf_score + position_bonus) * length_factor

    return scores


def summarize(text, num_sentences=4, ratio=None):
    """
    Summarize text using extractive TF-IDF sentence scoring.
    Args:
        text: Input text to summarize
        num_sentences: Number of sentences in summary
        ratio: If provided, overrides num_sentences (e.g., 0.3 = 30% of sentences)
    """
    if not text or len(text.strip()) < 100:
        return {
            "summary": text.strip() if text else "",
            "original_length": len(text) if text else 0,
            "summary_length": len(text) if text else 0,
            "compression_ratio": 1.0,
            "status": "too_short"
        }

    stop_words = set(stopwords.words('english'))
    sentences = sent_tokenize(text)

    if len(sentences) <= 3:
        return {
            "summary": text.strip(),
            "original_length": len(text),
            "summary_length": len(text),
            "sentences_original": len(sentences),
            "sentences_summary": len(sentences),
            "compression_ratio": 1.0,
            "status": "already_short"
        }

    # Determine number of sentences
    if ratio:
        num_sentences = max(2, int(len(sentences) * ratio))
    num_sentences = min(num_sentences, len(sentences) - 1)
    num_sentences = max(2, num_sentences)

    scores = _tfidf_sentence_scores(sentences, stop_words)

    # Get top sentences preserving original order
    top_indices = sorted(
        sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:num_sentences]
    )

    summary_sentences = [sentences[i] for i in top_indices]
    summary = " ".join(summary_sentences)

    # Calculate word stats
    original_words = len(word_tokenize(text))
    summary_words = len(word_tokenize(summary))

    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "original_word_count": original_words,
        "summary_word_count": summary_words,
        "sentences_original": len(sentences),
        "sentences_summary": len(summary_sentences),
        "compression_ratio": round(summary_words / original_words, 2) if original_words > 0 else 1.0,
        "top_sentence_scores": {sentences[i][:60] + "...": round(scores[i], 4) for i in top_indices},
        "status": "success"
    }


def summarize_with_sumy(text, method='lsa', num_sentences=4):
    """Try sumy library for more advanced summarization."""
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.summarizers.lex_rank import LexRankSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words

        LANGUAGE = "english"
        parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        if method == 'lexrank':
            summarizer = LexRankSummarizer(stemmer)
        else:
            summarizer = LsaSummarizer(stemmer)

        summarizer.stop_words = get_stop_words(LANGUAGE)
        summary_sentences = summarizer(parser.document, num_sentences)
        summary = " ".join(str(s) for s in summary_sentences)

        original_words = len(word_tokenize(text))
        summary_words = len(word_tokenize(summary))

        return {
            "summary": summary,
            "method": f"sumy_{method}",
            "original_word_count": original_words,
            "summary_word_count": summary_words,
            "compression_ratio": round(summary_words / original_words, 2),
            "status": "success"
        }
    except Exception as e:
        # Fall back to custom summarizer
        return summarize(text, num_sentences=num_sentences)
