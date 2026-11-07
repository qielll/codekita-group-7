# Build from the repo root:  docker build -t codekita-grader -f grader/Dockerfile .
FROM python:3.12-slim
WORKDIR /app
COPY grader/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY grader/ ./grader/
COPY content/ ./content/
CMD ["uvicorn", "grader.main:app", "--host", "0.0.0.0", "--port", "8000"]
