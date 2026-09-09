# AI-Based Prospectus Fact Extraction and Question Answering

## Overview

This project implements an **AI-based document analysis and question answering system** for extracting structured facts from PDF prospectus documents and answering user questions using the information contained in the document.

The system follows a **traditional NLP and information retrieval approach** without using Large Language Models (LLMs), OpenAI APIs, or Google Gemini.

The pipeline extracts text from a PDF, cleans and chunks the content, identifies structured facts using rule-based NLP and pattern matching, normalizes the extracted values, retrieves relevant facts using **TF-IDF and RapidFuzz**, and generates answers using a **rule-based question answering system**.

---

# Features

* PDF document upload and processing
* Text extraction from PDF documents
* Text cleaning and preprocessing
* Document chunking
* Rule-based fact extraction
* Structured fact storage using SQLAlchemy
* Fact normalization
* Question-to-attribute detection
* TF-IDF based information retrieval
* RapidFuzz similarity matching
* Rule-based Question Answering
* Evidence extraction
* Page number tracking
* Confidence scores
* QA evaluation
* REST APIs using FastAPI
* Swagger API documentation
* No dependency on OpenAI or Gemini APIs

---

# Technology Stack

| Component             | Technology                                |
| --------------------- | ----------------------------------------- |
| Programming Language  | Python                                    |
| Backend Framework     | FastAPI                                   |
| Database ORM          | SQLAlchemy                                |
| Database              | SQLite                                    |
| PDF Processing        | Python PDF extraction libraries           |
| NLP                   | Rule-based NLP, Regex, text normalization |
| Information Retrieval | TF-IDF                                    |
| Fuzzy Matching        | RapidFuzz                                 |
| Data Processing       | Python                                    |
| API Testing           | FastAPI Swagger UI                        |
| Version Control       | Git                                       |
| Repository            | GitHub                                    |

---

# System Architecture

```text
                    PDF Prospectus
                          |
                          v
                  PDF Text Extraction
                          |
                          v
                   Text Cleaning
                          |
                          v
                      Chunking
                          |
                          v
                  Fact Extraction
                 (Rules + Regex)
                          |
                          v
                 Fact Normalization
                          |
                          v
                  Structured Facts
                          |
                          v
              +-----------------------+
              |   Question Processing |
              +-----------------------+
                          |
                          v
                Attribute Detection
                          |
                          v
          TF-IDF + RapidFuzz Retrieval
                          |
                          v
                Best Fact Selection
                          |
                          v
               Rule-Based QA Engine
                          |
                          v
          +-----------------------------+
          | Answer + Evidence + Page    |
          | Number + Confidence         |
          +-----------------------------+
                          |
                          v
                     Evaluation
```

---

# Project Structure

```text
project/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── upload.py
│   │   │   ├── facts.py
│   │   │   └── qa.py
│   │   │
│   │   ├── models/
│   │   │   ├── database.py
│   │   │   ├── document.py
│   │   │   ├── chunk.py
│   │   │   └── fact.py
│   │   │
│   │   └── services/
│   │       ├── pdf_reader.py
│   │       ├── cleaning.py
│   │       ├── chunking.py
│   │       ├── fact_extractor.py
│   │       ├── fact_normalizer.py
│   │       ├── fact_retriever.py
│   │       └── evaluator.py
│   │
│   ├── main.py
│   └── requirements.txt
│
├── uploads/
├── cleaned_text/
├── chunks/
├── README.md
└── .gitignore
```

---

# Setup and Run Instructions

## 1. Clone the repository

Clone the GitHub repository:

```bash
git clone https://github.com/prabhasamu/fact_knowledge_layer.git

cd https://github.com/prabhasamu/fact_knowledge_layer.git

```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with the URL of the GitHub repository.

---

## 2. Create a virtual environment

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If a requirements file is not available, install the main dependencies used by the project:

```bash
pip install fastapi uvicorn sqlalchemy pydantic scikit-learn rapidfuzz python-multipart
```

Install any PDF extraction dependency used by the implementation if required.

---

## 4. Run the FastAPI server

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The backend will start at:

```text
http://127.0.0.1:8000
```

---

## 5. Open Swagger API documentation

Open:

```text
http://127.0.0.1:8000/docs
```

Swagger provides an interactive interface for testing all API endpoints.

---

# Processing a PDF

The system processes a prospectus through the following sequence:

```text
PDF Upload
    ↓
Text Extraction
    ↓
Cleaning
    ↓
Chunk Creation
    ↓
Fact Extraction
    ↓
Fact Normalization
    ↓
Question Answering
```

A document is assigned a `document_id` after upload.

For example:

```text
document_id = 5
```

---

# API Endpoints

## Upload PDF

```text
POST /upload/
```

Uploads and processes a PDF document.

---

## Extract Facts

```text
POST /facts/extract/{document_id}
```

Extracts structured facts from the processed document.

Example:

```text
POST /facts/extract/5
```

---

## Normalize Facts

```text
POST /facts/normalize/{document_id}
```

Normalizes extracted numerical values and units.

Example:

```text
POST /facts/normalize/5
```

---

## Search Facts

```text
GET /facts/search/{document_id}
```

Allows facts to be filtered by attribute.

Example:

```text
GET /facts/search/5?attribute=fresh_issue
```

---

## Question Answering

```text
POST /qa/
```

Example request:

```json
{
  "document_id": 5,
  "question": "What was the fresh issue?",
  "top_k": 5
}
```

The system returns the answer along with supporting evidence.

---

## QA Evaluation

```text
POST /qa/evaluate/{document_id}
```

Example:

```text
POST /qa/evaluate/5
```

This evaluates fact retrieval using a predefined set of questions.

---

# Example Questions

The system can answer questions such as:

```text
What was the fresh issue?

What was the offer for sale?

What was the total offer?

What was the revenue?

What was the profit?
```

For example:

```text
Question:
What was the fresh issue?

Answer:
The fresh issue was 82,152,503.
```

The response also provides supporting evidence and page information.

---

# Approach

## 1. PDF Text Extraction

The uploaded prospectus is first converted from PDF into machine-readable text.

The extracted text is retained along with page information so that the system can later identify where a particular fact was found.

---

## 2. Text Cleaning

The extracted text is cleaned to remove unnecessary whitespace, formatting artifacts, and other noise introduced during PDF extraction.

This improves the quality of subsequent fact extraction and retrieval.

---

## 3. Chunking

Large documents are divided into smaller chunks.

Chunking allows the system to process and search relevant portions of the document instead of comparing every question against the entire document.

Each chunk retains document and page information.

---

## 4. Fact Extraction

Instead of using an LLM, the project uses **rule-based NLP and regular expressions** to identify structured facts.

The extracted fact contains fields such as:

```text
document_id
chunk_id
page_number
entity
attribute
value
numeric_value
unit
period
scope
fact_type
evidence_text
confidence
```

Examples of attributes include:

```text
fresh_issue
offer_for_sale
total_offer
revenue
profit
face_value
issue_price
employees
orders
market_share
```

This converts unstructured prospectus text into structured information.

---

## 5. Fact Normalization

Extracted values are normalized to improve consistency.

For example, numerical values and their units are stored separately:

```text
value
numeric_value
unit
normalized_value
normalized_unit
```

This makes the extracted information easier to search and compare.

---

## 6. Question-to-Attribute Detection

The question is first analyzed using rule-based keyword matching.

For example:

```text
"What was the fresh issue?"
```

is mapped to:

```text
fresh_issue
```

Similarly:

```text
"What was the revenue?"
```

is mapped to:

```text
revenue
```

This allows the system to focus retrieval on the requested type of information.

---

## 7. TF-IDF Retrieval

The system uses **TF-IDF (Term Frequency-Inverse Document Frequency)** to identify facts that are textually relevant to the question.

TF-IDF provides a lightweight and interpretable information retrieval method without requiring a large language model.

---

## 8. RapidFuzz Matching

TF-IDF retrieval is supplemented with **RapidFuzz similarity matching**.

RapidFuzz helps handle small variations in wording between the question and the evidence text.

The retrieval score combines multiple signals:

```text
Final Score =
    0.45 × Attribute Similarity
  + 0.30 × TF-IDF Similarity
  + 0.15 × Keyword Similarity
  + 0.10 × Evidence Similarity
```

This hybrid approach improves retrieval compared with relying on a single similarity method.

---

## 9. Rule-Based Question Answering

After retrieving relevant facts, the system selects the most appropriate structured fact.

The answer is generated using a deterministic template.

For example:

```text
The fresh issue was 82,152,503.
```

This approach was deliberately chosen instead of using an LLM because the project requirements can be satisfied using traditional NLP and information retrieval techniques.

---

# AI Tools Used

The project intentionally **does not use Large Language Models**.

The following AI/NLP techniques are used:

### Rule-Based NLP

Used for:

* Question classification
* Attribute detection
* Fact extraction
* Pattern recognition
* Value validation

### Regular Expressions

Used for:

* Numerical extraction
* Unit detection
* Pattern matching
* Filtering extraction artifacts

### TF-IDF

Used for:

* Text representation
* Question-to-fact similarity
* Information retrieval

### RapidFuzz

Used for:

* Fuzzy text matching
* Handling wording variations
* Evidence similarity

### Traditional Machine Learning / Information Retrieval

The project focuses on lightweight and interpretable NLP/AI methods rather than generative AI.

---

# Important Design Decisions

## Why no LLM?

The project intentionally avoids:

```text
OpenAI
Gemini
ChatGPT APIs
Other Generative LLM APIs
```

This makes the system:

* Deterministic
* Reproducible
* Lightweight
* Easier to deploy
* Independent of external API keys
* Less dependent on internet connectivity
* More interpretable

---

## Why TF-IDF?

TF-IDF is computationally inexpensive and works well for document retrieval when the important terms in the question also occur in the document.

It is also easy to explain and debug.

---

## Why RapidFuzz?

Exact keyword matching can fail when the question and document use slightly different wording.

RapidFuzz provides an additional similarity signal while remaining lightweight.

---

## Why Rule-Based QA?

The target questions are primarily factual questions involving structured information such as:

```text
Issue size
Revenue
Profit
Share information
Employee count
Orders
Market share
```

A deterministic rule-based approach is sufficient for these types of questions and avoids hallucination associated with generative systems.

---

# Evaluation

The system was evaluated using five factual questions:

| Question                     | Expected Attribute | Result    |
| ---------------------------- | ------------------ | --------- |
| What was the fresh issue?    | `fresh_issue`      | Correct   |
| What was the offer for sale? | `offer_for_sale`   | Incorrect |
| What was the total offer?    | `total_offer`      | Correct   |
| What was the revenue?        | `revenue`          | Correct   |
| What was the profit?         | `profit`           | Correct   |

### Evaluation Results

```text
Total Questions:       5
Top-1 Accuracy:       80%
Top-5 Accuracy:       80%
Correct:               4 / 5
```

The evaluation demonstrates that the fact retrieval system correctly identifies the intended fact attribute for **4 out of 5 test questions**.

---

# Git Usage

Git was used to maintain the project source code and track development throughout the implementation.

The repository should contain meaningful commits representing major development stages.

Recommended commit history:

```bash
git add .
git commit -m "Initial FastAPI project setup"

git add .
git commit -m "Add PDF text extraction and preprocessing"

git add .
git commit -m "Implement document chunking"

git add .
git commit -m "Implement rule-based fact extraction"

git add .
git commit -m "Add fact normalization"

git add .
git commit -m "Implement TF-IDF and RapidFuzz retrieval"

git add .
git commit -m "Implement rule-based question answering"

git add .
git commit -m "Add QA evaluation"

git add .
git commit -m "Finalize project documentation"
```

Push the project to GitHub:

```bash
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

The repository should **not contain secrets, API keys, virtual environments, databases containing sensitive information, or unnecessary generated files**.

Use `.gitignore` to exclude files such as:

```text
venv/
__pycache__/
.env
*.pyc
*.db
uploads/
cleaned_text/
```

---

# Video Demo

A short demo video of **3 minutes or less** should demonstrate the complete processing pipeline.

The recommended demo flow is:

### 1. Start the application

Show:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

### 2. Process the PDF

Show the PDF upload endpoint and upload the prospectus.

### 3. Extract facts

Run:

```text
POST /facts/extract/{document_id}
```

Show the extracted fact count.

### 4. Normalize facts

Run:

```text
POST /facts/normalize/{document_id}
```

Show the successful normalization response.

### 5. Demonstrate the four required QA cases

Use the required questions from the assignment. For this implementation, the main demonstrated factual cases are:

```text
What was the fresh issue?

What was the offer for sale?

What was the total offer?

What was the revenue?
```

For each question, show:

```text
Question
   ↓
Retrieved Fact
   ↓
Answer
   ↓
Evidence
   ↓
Page Number
```

### 6. Show evaluation

Finally run:

```text
POST /qa/evaluate/{document_id}
```

and show the evaluation result:

```text
Top-1 Accuracy: 80%
Top-5 Accuracy: 80%
```

## Video Demo Link

Add the final video URL here:

```text
[VIDEO DEMO LINK]
```

For example, the video can be uploaded to YouTube as an **Unlisted** video or to another accessible video-hosting service, and the link can be added above.

---

# Limitations

The current system has several limitations.

## 1. Rule-Based Fact Extraction

The fact extractor depends on predefined patterns and rules.

Documents with significantly different formatting or terminology may require additional extraction rules.

---

## 2. PDF Extraction Noise

PDF-to-text conversion can introduce artifacts such as:

```text
footnote numbers
page numbers
broken words
punctuation
table formatting errors
```

Some of these artifacts may result in incorrect or incomplete facts.

---

## 3. Limited Question Types

The current QA system focuses primarily on predefined factual attributes.

It does not yet support complex reasoning questions such as:

```text
Why did revenue increase?

Compare the company's performance across multiple years.

What are the main risks mentioned in the document?
```

---

## 4. Limited Semantic Understanding

TF-IDF and fuzzy matching primarily rely on lexical similarity.

They do not provide the deep semantic understanding available from modern language models.

---

## 5. Extraction Ambiguity

Some prospectus sections contain several related values close together.

For example, an issue section may contain:

```text
Fresh Issue
Offer for Sale
Employee Reservation Portion
Net Offer
Total Offer
```

PDF extraction can cause surrounding values to be associated with the wrong attribute.

This is reflected in the current evaluation where the **Offer for Sale** question was incorrectly retrieved.

---

## 6. Small Evaluation Dataset

The current evaluation uses five representative questions.

A larger manually verified question-answer dataset would provide a more reliable measurement of system performance.

---

# Next Steps

Future improvements could include:

1. Improve table-aware PDF extraction.
2. Add more robust fact extraction rules.
3. Add Named Entity Recognition for company names, financial entities, and organizations.
4. Improve numerical and unit normalization.
5. Add more question categories.
6. Create a larger manually labelled evaluation dataset.
7. Improve retrieval using BM25 or other traditional information retrieval algorithms.
8. Add domain-specific NLP models without using generative LLMs.
9. Improve handling of multi-year financial information.
10. Add cross-document comparison.
11. Add confidence-based answer validation.
12. Improve evidence ranking and citation selection.

---

# Additional Notes

## No LLM Dependency

A major design decision in this project is that the system does **not depend on an LLM or external generative AI API**.

The complete question-answering pipeline is based on:

```text
Rules
+
Regular Expressions
+
TF-IDF
+
RapidFuzz
+
Structured Facts
```

This makes the system lightweight and reproducible.

---

## Explainability

Every answer can be traced back to:

```text
Fact
 ↓
Evidence Text
 ↓
Page Number
 ↓
Source Document
```

This is particularly useful for document analysis because users can verify the generated answer against the original prospectus.

---

## Reproducibility

The application can be run locally using Python and FastAPI without requiring an external AI API key.

The same input document and processing rules produce deterministic results.

---

# Conclusion

This project demonstrates a complete **document intelligence and question answering pipeline** using traditional NLP and information retrieval techniques.

The system transforms an unstructured PDF prospectus into structured facts and uses those facts to answer factual questions with supporting evidence and page references.

The current implementation achieves:

```text
Fact Extraction
        +
Fact Normalization
        +
TF-IDF Retrieval
        +
RapidFuzz Matching
        +
Rule-Based QA
        +
Evidence Tracking
        +
80% Top-1 Retrieval Accuracy
```

The architecture provides a strong foundation for further improvements in financial document analysis while remaining lightweight, interpretable, and independent of LLM APIs.
