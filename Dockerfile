FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
WORKDIR /app
COPY requirements.txt requirements-quantum.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt && useradd -u 10001 -m app
COPY . .
USER app
EXPOSE 8000
CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]
