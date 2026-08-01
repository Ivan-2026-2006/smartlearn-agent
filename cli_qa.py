"""
CLI Q&A Tool - PRD (Product Requirements Document)

What it does:
  A command-line tool that takes a multi-paragraph text and a question,
  then uses an LLM to answer the question with paragraph-level citations.

Input:
  1. Multi-line text from user (terminated by typing 'END' on a new line)
     OR a text file via --file flag
  2. One or more questions about the text

Output:
  Answers that reference specific paragraphs using [Paragraph X] format.

Done when:
  - User can paste text or load from file
  - Answers include [Paragraph X] citations
  - Supports multiple questions in one session
  - Uses OpenRouter API (google/gemma-4-31b-it:free model)
  - API key loaded from .env file and never printed
  - Empty text exits with a friendly error before any API call
  - Missing answers return exactly: The text does not provide this information.
"""

import os
import argparse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(encoding="utf-16")

MISSING = "The text does not provide this information."


def read_text():
    """Read multi-line text from the terminal until END is typed."""
    print("请粘贴文本（输入 END 结束）：")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def split_paragraphs(text):
    """Split the text into a list of paragraphs by blank lines."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def number_paragraphs(paragraphs):
    """Number the paragraphs and return one formatted string."""
    numbered = []
    for i, para in enumerate(paragraphs, 1):
        numbered.append(f"[Paragraph {i}]\n{para}")
    return "\n\n".join(numbered)


def ask_question(numbered_text, question):
    """Build the prompt, call the LLM API, and return the answer."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is missing. Add it to .env and try again.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = """You are a precise research assistant.

Rules:
1. Answer ONLY using information from the provided text.
2. After EVERY claim, add a citation in the format [Paragraph X].
3. If a sentence uses information from multiple paragraphs, cite all of them.
4. If the text does not contain the answer, reply exactly:
   'The text does not provide this information.'
5. Do NOT add any information beyond what is in the text.

Example:
If the text says:
[Paragraph 1] The sky is blue.
[Paragraph 2] Grass is green.

And the question is: 'What color is the sky?'
Your answer should be: 'The sky is blue [Paragraph 1].'
"""

    user_prompt = f"""Here is the text:

{numbered_text}

Question: {question}"""

    response = client.chat.completions.create(
        model="inclusionai/ling-3.0-flash:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="CLI Q&A Tool")
    parser.add_argument(
        "--file",
        help="Path to a text file to use as input (instead of pasting)",
    )
    args = parser.parse_args()

    # Read the text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"已从文件 {args.file} 读取文本。")
    else:
        text = read_text()

    paragraphs = split_paragraphs(text)
    if not paragraphs:
        raise SystemExit("No text was provided. Paste text or choose a non-empty file.")
    print(f"\n检测到 {len(paragraphs)} 个段落。")

    numbered_text = number_paragraphs(paragraphs)

    # Q&A loop
    print("你可以连续提问，输入 quit 退出。\n")

    while True:
        question = input("请输入你的问题（quit 退出）：")

        if question.strip().lower() == "quit":
            print("再见！")
            break

        print("\n正在思考...\n")
        answer = ask_question(numbered_text, question)

        print("回答：")
        print(answer)
        print()


if __name__ == "__main__":
    main()