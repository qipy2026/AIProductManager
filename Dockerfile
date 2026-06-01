FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV AGENTOPS_STORAGE=sqlite
ENV SEMANTIC_BACKEND=chroma
ENV LLM_MODE=mock
ENV USE_LANGGRAPH=1

EXPOSE 8000

CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
