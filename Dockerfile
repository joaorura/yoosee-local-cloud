FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

EXPOSE 8080 32100/udp 32108/udp 18443/udp 18800/udp 19800/udp

ENTRYPOINT ["yoosee-fake-cloud"]
CMD ["--host", "0.0.0.0", "--http-port", "8080", "--reply-ack", "-v"]
