FROM python:3.12.1-slim-bookworm

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.7 \
  POETRY_VIRTUALENVS_CREATE=false

RUN pip install --upgrade pip && \
    pip install "poetry==$POETRY_VERSION"

WORKDIR /code

COPY poetry.lock pyproject.toml /code/

RUN poetry install --no-interaction

COPY . /code

#EXPOSE 9000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]
