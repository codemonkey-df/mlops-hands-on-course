# Mock vLLM: ~60 MB of Python deps instead of a ~10 GB CUDA image.
# Build from the repo root:
#   docker build -f platform/images/mock-vllm/Dockerfile -t mlops/mock-vllm:0.1.0 .
FROM python:3.12-slim
RUN pip install --no-cache-dir \
      fastapi==0.143.0 uvicorn==0.54.0 prometheus-client==0.26.0 pydantic==2.14.1
WORKDIR /app
# Only the mock module, not the whole project (no torch, no mlflow).
COPY src/mlops_course/__init__.py mlops_course/__init__.py
COPY src/mlops_course/llm/ mlops_course/llm/
RUN useradd -u 1000 -m vllm
USER 1000
EXPOSE 8000
# Same arguments as the real image (`vllm serve <model> --flags...`) go in `args:`.
ENTRYPOINT ["python", "-m", "mlops_course.llm.mock_vllm"]
