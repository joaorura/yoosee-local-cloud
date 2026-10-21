ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base-python:3.12-alpine3.20
FROM ${BUILD_FROM}

WORKDIR /app

RUN apk add --no-cache bash jq \
    && apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY sounds/ ./sounds/

RUN pip install --no-cache-dir . \
    && apk del .build-deps

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
