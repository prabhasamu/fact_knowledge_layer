from typing import List, Dict


def create_chunks(
    pages: List[Dict],
    chunk_size: int = 1500,
    chunk_overlap: int = 200
):
    """
    Create text chunks while preserving the original page number.

    Each returned chunk contains:
    - page_number
    - chunk_index
    - text
    """

    chunks = []

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        if not text:
            continue

        start = 0
        chunk_index = 0

        while start < len(text):

            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "text": chunk_text
                })

            if end >= len(text):
                break

            start = end - chunk_overlap
            chunk_index += 1

    return chunks