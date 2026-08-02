# SmartLearn Agent - Product Design

## User Stories

1. As a student , I want to upload a PDF and ask questions about it, so that  study more efficiently .
2. As a student , I want to get answers with page numbers, so that quickly find the original content in the PDF.
3. As a student , I want to ask follow-up questions in a conversation, so that deepen understanding of a topic.

## Feature List


| Priority | Feature | Day | Notes |
|----------|---------|-----|------|
| P0 | PDF text extraction | Day 2 | The foundation; nothing works without it |
| P0 | LLM Q&A with page citation | Day 2 | The core feature; users upload a PDF and ask questions |
| P1 | RAG pipeline | Day 3 | Handles long PDFs by retrieving only the most relevant parts |
| P1 | Web UI | Day 3 | Lets users interact through a browser |
| P2 | Chat history | Day 3 | Remembers earlier questions and supports follow-ups |

## Data Flow

### Day 2: Simple Mode

PDF File
  ->  [PDF parser / extract text]         # How do we get text out?
  -> pages[]
  -> [build prompt: pages + question]          # How do we combine with question?
  -> [LLM]
  -> Answer with [Page X]

### Day 3: RAG Mode

PDF -> [extract text] -> pages
    -> [split into chunks] -> chunks with source_page
    -> [embed] -> embeddings
    -> [vector store (FAISS)] # storage

Question -> [encode] -> [similarity search] -> relevant chunks -> [LLM] -> Answer