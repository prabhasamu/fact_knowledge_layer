from app.services.fact_retriever import retrieve_relevant_facts


def evaluate_questions(questions, facts, top_k=5):
    """
    Evaluate fact retrieval using expected attributes.

    Each question should contain:
        question
        expected_attribute
    """

    total = len(questions)
    top1_correct = 0
    topk_correct = 0

    results = []

    for item in questions:

        question = item["question"]
        expected_attribute = item["expected_attribute"]

        retrieved = retrieve_relevant_facts(
            question=question,
            facts=facts,
            top_k=top_k
        )

        retrieved_attributes = [
            result["fact"].attribute
            for result in retrieved
        ]

        top1 = (
            len(retrieved_attributes) > 0
            and retrieved_attributes[0] == expected_attribute
        )

        topk = expected_attribute in retrieved_attributes

        if top1:
            top1_correct += 1

        if topk:
            topk_correct += 1

        results.append({
            "question": question,
            "expected_attribute": expected_attribute,
            "top1_attribute": (
                retrieved_attributes[0]
                if retrieved_attributes
                else None
            ),
            "top1_correct": top1,
            "top_k_correct": topk
        })

    return {
        "total_questions": total,
        "top1_accuracy": (
            top1_correct / total
            if total else 0
        ),
        "top_k_accuracy": (
            topk_correct / total
            if total else 0
        ),
        "results": results
    }