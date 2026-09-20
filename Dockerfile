FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY corpus ./corpus
COPY docs ./docs
RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["jevbench"]
CMD ["validate"]

