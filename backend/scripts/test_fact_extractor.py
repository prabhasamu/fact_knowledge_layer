from app.services.fact_extractor import extract_facts_from_chunk


text = """
DELHIVERY LIMITED

Fresh issue of 82,152,503 Equity Shares
aggregating to ₹40,000.00 million.

Offer for sale of 25,364,585 Equity Shares
aggregating to ₹12,350.00 million.
"""


facts = extract_facts_from_chunk(
    text,
    page_number=1,
    chunk_id=289
)


for fact in facts:

    print("\nFACT")
    print("------------------")

    for key, value in fact.items():
        print(f"{key}: {value}")