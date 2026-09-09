import re

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------
# TEXT CLEANING
# ---------------------------------------------------------

def clean_text(text):
    if not text:
        return ""

    text = str(text).lower()

    # Convert underscores to spaces
    text = text.replace("_", " ")

    # Keep English letters, numbers, spaces and useful symbols
    text = re.sub(r"[^a-z0-9\s%₹]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ---------------------------------------------------------
# QUESTION NORMALIZATION
# ---------------------------------------------------------

def normalize_question(question):
    """
    Convert common question wording into terms
    that match our structured fact attributes.
    """

    question = clean_text(question)

    replacements = {
        "what was the fresh issue": "fresh issue",
        "what is the fresh issue": "fresh issue",
        "fresh issue size": "fresh issue",

        "what was the offer for sale": "offer for sale",
        "what is the offer for sale": "offer for sale",
        "offer for sale size": "offer for sale",

        "total offer size": "total offer",
        "what was the total offer": "total offer",

        "face value of the shares": "face value",
        "face value of equity shares": "face value",

        "issue price of the shares": "issue price",
        "price of the shares": "issue price",

        "number of shares": "shares",
        "number of equity shares": "shares",

        "company name": "company",
        "name of the company": "company",
    }

    for old, new in replacements.items():
        if old in question:
            question = question.replace(old, new)

    return question


# ---------------------------------------------------------
# FACT TEXT
# ---------------------------------------------------------

def build_fact_text(fact):
    """
    Convert a structured fact into searchable text.
    """

    parts = [
        fact.attribute or "",
        fact.entity or "",
        fact.value or "",
        fact.unit or "",
        fact.period or "",
        fact.scope or "",
        fact.fact_type or "",
        fact.evidence_text or ""
    ]

    return clean_text(" ".join(parts))


# ---------------------------------------------------------
# ATTRIBUTE SIMILARITY
# ---------------------------------------------------------

def attribute_similarity(question, attribute):
    """
    Compare the question with the structured
    fact attribute.
    """

    question = clean_text(question)
    attribute = clean_text(attribute)

    if not question or not attribute:
        return 0.0

    # Direct phrase match
    if attribute in question:
        return 1.0

    # Fuzzy similarity
    return fuzz.token_set_ratio(
        question,
        attribute
    ) / 100.0


# ---------------------------------------------------------
# KEYWORD MATCHING
# ---------------------------------------------------------

def keyword_similarity(question, fact):
    """
    Check whether important words from the question
    occur in the fact's attribute/evidence.
    """

    question_words = set(clean_text(question).split())

    fact_words = set(
        clean_text(
            f"{fact.attribute} {fact.entity} {fact.evidence_text}"
        ).split()
    )

    if not question_words:
        return 0.0

    common_words = question_words.intersection(fact_words)

    return len(common_words) / len(question_words)


# ---------------------------------------------------------
# FACT RETRIEVAL
# ---------------------------------------------------------

def retrieve_relevant_facts(
    question,
    facts,
    top_k=5
):
    """
    Retrieve relevant facts using:

    1. TF-IDF + cosine similarity
    2. Attribute matching
    3. Keyword matching
    4. Evidence fuzzy matching

    No LLM is used.
    """

    if not facts:
        return []

    # Normalize the question
    question_clean = normalize_question(question)

    # Build searchable fact documents
    fact_texts = [
        build_fact_text(fact)
        for fact in facts
    ]

    # -----------------------------------------------------
    # TF-IDF
    # -----------------------------------------------------

    documents = [question_clean] + fact_texts

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    question_vector = tfidf_matrix[0]

    fact_vectors = tfidf_matrix[1:]

    similarity_scores = cosine_similarity(
        question_vector,
        fact_vectors
    )[0]

    # -----------------------------------------------------
    # Calculate final relevance score
    # -----------------------------------------------------

    results = []

    for index, fact in enumerate(facts):

        # TF-IDF similarity
        tfidf_score = float(
            similarity_scores[index]
        )

        # Structured attribute similarity
        attribute_score = attribute_similarity(
            question_clean,
            fact.attribute
        )

        # Keyword overlap
        keyword_score = keyword_similarity(
            question_clean,
            fact
        )

        # Evidence similarity
        evidence_score = fuzz.token_set_ratio(
            question_clean,
            clean_text(fact.evidence_text or "")
        ) / 100.0

        # -------------------------------------------------
        # Weighted score
        #
        # Attribute is given the highest importance because
        # it is our structured NLP-extracted field.
        # -------------------------------------------------

        final_score = (
            0.45 * attribute_score
            + 0.30 * tfidf_score
            + 0.15 * keyword_score
            + 0.10 * evidence_score
        )

        results.append({
            "fact": fact,
            "score": final_score
        })

    # -----------------------------------------------------
    # Sort by relevance
    # -----------------------------------------------------

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:top_k]