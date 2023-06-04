FROM python:3.11 as requirements-stage
RUN pip install poetry
WORKDIR /tmp
COPY poetry.lock pyproject.toml /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
FROM python:3.11
COPY --from=requirements-stage /tmp/requirements.txt /Ralchemist/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /Ralchemist/requirements.txt
COPY . /Ralchemist
WORKDIR /Ralchemist
CMD ["gunicorn", "src.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80"]