# PDF Summary Tool — Mini PRD

## Goal
A CLI tool that reads a PDF file and prints a structured summary.

## Usage
```
python3 pdf_summary.py <path-to-pdf>
```

## Requirements
1. Accept a PDF file path as a command-line argument
2. Extract text from the PDF
3. Send extracted text to an LLM through OpenRouter
4. Print exactly three sections: Overview, Key Points, and Limitations
5. Every key point must include a [Page X] citation
6. Never print the API key or PDF contents during normal operation

## Tech Constraints
- Use `python-dotenv` to load API keys from `.env`
- Use `openai` SDK with OpenRouter as the base URL
- PDF library: (let AI decide the best option)

## Done When
1. `python3 -m py_compile pdf_summary.py` succeeds
2. A short text-based PDF produces all three output sections and page citations
3. A missing path prints a friendly usage/error message without a traceback
4. A scanned PDF with no extractable text explains the limitation instead of calling the LLM with empty text
5. `git status --short` does not show `.env`
