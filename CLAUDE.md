# SmartLearn Agent

## Project
SmartLearn Agent is an AI-powered learning assistant that parses PDF lecture slides and answers students' course-related questions.


## Tech Stack
- Backend: Python + FastAPI
- Frontend: React + Vite
- LLM: OpenRouter (qwen/qwen3.5-flash-02-23)
- Vector Search: FAISS (Day 3)

## AI Coding Environment
- Claude Code uses DeepSeek directly through ANTHROPIC_BASE_URL
- OpenRouter is only for the student Python API exercises
- Never route Claude Code through OpenRouter

## Conventions
- API keys in .env, never commit
- Use venv for Python dependencies
- Commit messages: type: description (feat/fix/docs/refactor)

## Do Not Modify
- .env
- package-lock.json