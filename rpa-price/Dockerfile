FROM python:3.11-slim

WORKDIR /app
RUN pip install poetry==1.7.1

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY rpa ./
ENTRYPOINT ["/bin/bash"]