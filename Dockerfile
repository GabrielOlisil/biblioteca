FROM python:3.13-slim-trixie


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/django/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y libpq-dev curl build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY --from=ghcr.io/astral-sh/uv@sha256:2381d6aa60c326b71fd40023f921a0a3b8f91b14d5db6b90402e65a635053709 /uv /bin/

WORKDIR /app


COPY uv.lock pyproject.toml .python-version ./

RUN uv pip install . --system \
    && rm -rf /bin/uv/

COPY . ./

RUN adduser --disabled-password --gecos '' django \
    && chown -R django:django /app
USER django


EXPOSE 8080

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
