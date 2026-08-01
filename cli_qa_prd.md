CLI Q&A Tool - PRD (Product Requirements Document)

What it does:
  A command-line tool that takes a multi-paragraph text and a question,
  then uses an LLM to answer the question with paragraph-level citations.

Input:
  1. Multi-line text from user (terminated by typing 'END' on a new line)
  2. A question about the text

Output:
  An answer that references specific paragraphs using [Paragraph X] format.

Done when / acceptance tests:
  - User can paste text and ask questions in the terminal
  - Answers include [Paragraph X] citations
  - Uses OpenRouter API (google/gemma-4-31b-it:free model)
  - API key loaded from .env file and never printed
  - A question answered by Paragraph 1 cites [Paragraph 1]
  - A question absent from the text returns: The text does not provide this information.
  - An empty text input shows a friendly error instead of calling the API
  - python3 -m py_compile cli_qa.py succeeds