import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.pdf_extractor import extract_text_from_pdf

PDF_PATH = Path(
    "data/uploads/01-delhivery-prospectus-2022-excerpt.pdf"
)


def main():
    pages = extract_text_from_pdf(str(PDF_PATH))

    print("=" * 80)
    print("PDF ENCODING TEST")
    print("=" * 80)

    for page in pages:
        text = page["text"]

        if "42.27" in text:
            position = text.find("42.27")

            start = max(0, position - 100)
            end = min(len(text), position + 150)

            sample = text[start:end]

            print("Page:", page["page_number"])
            print()
            print("NORMAL TEXT:")
            print(sample)

            print()
            print("REPR:")
            print(repr(sample))

            print()
            print("UNICODE CODE POINTS:")

            for char in sample:
                if char != " ":
                    print(
                        repr(char),
                        "->",
                        hex(ord(char))
                    )

            print()
            print("=" * 80)
            return

    print("42.27 was not found in the extracted PDF text.")


if __name__ == "__main__":
    main()