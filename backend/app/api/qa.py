from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import re

from app.models.database import get_db
from app.models.fact import Fact
from app.services.fact_retriever import retrieve_relevant_facts

from app.services.evaluator import evaluate_questions

router = APIRouter(
    prefix="/qa",
    tags=["Question Answering"]
)


class QuestionRequest(BaseModel):
    document_id: int
    question: str
    top_k: int = 5


# ---------------------------------------------------------
# QUESTION -> ATTRIBUTE MAPPING
# ---------------------------------------------------------

def detect_attribute(question):
    """
    Detect the fact attribute requested by the user.
    Traditional rule-based NLP; no LLM.
    """

    q = question.lower()

    patterns = {
        "fresh_issue": [
            "fresh issue",
            "fresh issue size",
            "new issue"
        ],

        "offer_for_sale": [
            "offer for sale",
            "offer for sale size",
            "ofs"
        ],

        "total_offer": [
            "total offer",
            "total offer size",
            "offer size"
        ],

        "revenue": [
            "revenue",
            "income",
            "sales"
        ],

        "profit": [
            "profit",
            "net profit",
            "profit after tax",
            "pat"
        ],

        "face_value": [
            "face value",
            "face value of shares",
            "face value of equity shares"
        ],

        "issue_price": [
            "issue price",
            "price of shares",
            "share price"
        ],

        "employees": [
            "employees",
            "number of employees",
            "employee count"
        ],

        "orders": [
            "orders",
            "number of orders",
            "orders received"
        ],

        "market_share": [
            "market share"
        ]
    }

    for attribute, keywords in patterns.items():
        for keyword in keywords:
            if keyword in q:
                return attribute

    return None


# ---------------------------------------------------------
# VALUE VALIDATION
# ---------------------------------------------------------

def is_valid_fact(fact):
    """
    Reject obviously invalid extracted values such as:
    1, 2, 15, commas, punctuation, etc.

    This is intentionally conservative.
    """

    value = (fact.value or "").strip()

    if not value:
        return False

    # Remove whitespace
    cleaned = value.replace(" ", "")

    # Reject punctuation-only values
    if re.fullmatch(r"[,.;:()\-\[\]]+", cleaned):
        return False

    # -----------------------------------------------------
    # Reject small enumeration/reference numbers
    # Examples:
    # Fresh Issue(1)
    # Offer for Sale(2)
    # Section (15)
    # -----------------------------------------------------

    if re.fullmatch(r"\d{1,2}", cleaned):
        number = int(cleaned)

        if 1 <= number <= 30:
            return False

    # Values such as "15," are usually extraction artifacts
    if re.fullmatch(r"\d{1,2},", cleaned):
        return False

    return True


# ---------------------------------------------------------
# ATTRIBUTE MATCHING
# ---------------------------------------------------------

def get_attribute_candidates(question, results):
    """
    Prefer facts whose structured attribute matches
    the question.
    """

    requested_attribute = detect_attribute(question)

    if not requested_attribute:
        return results

    matching = []

    for result in results:
        fact = result["fact"]

        if fact.attribute == requested_attribute:
            if is_valid_fact(fact):
                matching.append(result)

    # If matching facts exist, use only them
    if matching:
        return matching

    return results


# ---------------------------------------------------------
# BEST FACT SELECTION
# ---------------------------------------------------------

def select_best_fact(question, results):
    if not results:
        return None

    requested_attribute = detect_attribute(question)

    # Prefer facts matching the requested attribute
    if requested_attribute:
        matching = [
            result
            for result in results
            if result["fact"].attribute == requested_attribute
            and is_valid_fact(result["fact"])
        ]

        if matching:
            # Prefer:
            # 1. Higher extraction confidence
            # 2. Numeric values when available
            # 3. Retrieval score
            matching.sort(
                key=lambda x: (
                    x["fact"].confidence or 0,
                    1 if x["fact"].numeric_value is not None else 0,
                    x["score"]
                ),
                reverse=True
            )

            return matching[0]["fact"]

    # Fallback to normal retrieval
    candidates = [
        result
        for result in results
        if is_valid_fact(result["fact"])
    ]

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates[0]["fact"]

# ---------------------------------------------------------
# ANSWER GENERATION
# ---------------------------------------------------------

def generate_answer(question, results):

    if not results:
        return {
            "answer": "I could not find relevant information in the document.",
            "evidence": []
        }

    best = select_best_fact(
        question,
        results
    )

    if best is None:
        return {
            "answer": "I could not find a reliable value for this question in the document.",
            "evidence": []
        }

    attribute = best.attribute
    value = best.value
    unit = best.unit

    readable_attribute = (
        attribute.replace("_", " ")
        if attribute
        else "requested information"
    )

    # -----------------------------------------------------
    # Format answer
    # -----------------------------------------------------

    if unit:
        answer = (
            f"The {readable_attribute} "
            f"was {value} {unit}."
        )
    else:
        answer = (
            f"The {readable_attribute} "
            f"was {value}."
        )

    return {
        "answer": answer,
        "evidence": [
            {
                "page_number": best.page_number,
                "chunk_id": best.chunk_id,
                "evidence_text": best.evidence_text,
                "confidence": best.confidence
            }
        ]
    }


# ---------------------------------------------------------
# QA API
# ---------------------------------------------------------

@router.post("/")
def answer_question(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):

    facts = (
        db.query(Fact)
        .filter(
            Fact.document_id == request.document_id
        )
        .all()
    )

    if not facts:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No facts found for "
                f"document {request.document_id}"
            )
        )

    # -----------------------------------------------------
    # Detect requested attribute
    # -----------------------------------------------------

    requested_attribute = detect_attribute(
        request.question
    )

    # -----------------------------------------------------
    # Normal retrieval
    # -----------------------------------------------------

    results = retrieve_relevant_facts(
        question=request.question,
        facts=facts,
        top_k=request.top_k
    )

    # -----------------------------------------------------
    # Direct attribute-based retrieval
    # -----------------------------------------------------
    # This prevents the correct fact from being lost
    # when it is outside the TF-IDF top-k results.
    # -----------------------------------------------------

    if requested_attribute:

        attribute_facts = [
            fact
            for fact in facts
            if fact.attribute == requested_attribute
            and is_valid_fact(fact)
        ]

        # Add attribute-matching facts to results
        existing_ids = {
            result["fact"].id
            for result in results
        }

        for fact in attribute_facts:

            if fact.id not in existing_ids:

                results.append({
                    "fact": fact,
                    "score": 1.0
                })

    # -----------------------------------------------------
    # Sort again after adding attribute matches
    # -----------------------------------------------------

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # -----------------------------------------------------
    # Generate answer
    # -----------------------------------------------------

    response = generate_answer(
        request.question,
        results
    )

    return {
        "document_id": request.document_id,
        "question": request.question,
        "answer": response["answer"],
        "evidence": response["evidence"],
        "retrieved_facts": [
            {
                "fact_id": result["fact"].id,
                "attribute": result["fact"].attribute,
                "value": result["fact"].value,
                "unit": result["fact"].unit,
                "page_number": result["fact"].page_number,
                "score": round(
                    result["score"],
                    4
                )
            }
            for result in results[:request.top_k]
        ]
    }

@router.post("/evaluate/{document_id}")
def evaluate_qa(
    document_id: int,
    db: Session = Depends(get_db)
):

    facts = (
        db.query(Fact)
        .filter(
            Fact.document_id == document_id
        )
        .all()
    )

    if not facts:
        raise HTTPException(
            status_code=404,
            detail=f"No facts found for document {document_id}"
        )

    questions = [
        {
            "question": "What was the fresh issue?",
            "expected_attribute": "fresh_issue"
        },
        {
            "question": "What was the offer for sale?",
            "expected_attribute": "offer_for_sale"
        },
        {
            "question": "What was the total offer?",
            "expected_attribute": "total_offer"
        },
        {
            "question": "What was the revenue?",
            "expected_attribute": "revenue"
        },
        {
            "question": "What was the profit?",
            "expected_attribute": "profit"
        }
    ]

    evaluation = evaluate_questions(
        questions=questions,
        facts=facts,
        top_k=5
    )

    return {
        "document_id": document_id,
        "evaluation": evaluation
    }
