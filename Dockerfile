FROM python:3.11
run pip install poetry
WORKDIR /tmp
COPY poetry.lock pyproject.toml /tmp/
RUN poetry install
COPY . /tmp
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "RecipeAlchemy.app:app", "--port", "80"]

# FROM python:3.10 as requirements-stage
# WORKDIR /tmp
# RUN pip install poetry
# COPY ./pyproject.toml ./poetry.lock* /tmp/
# RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
# COPY --from=requirements-stage /tmp/requirements.txt /RecipeAlchemy/requirements.txt
# RUN pip install --no-cache-dir --upgrade -r /RecipeAlchemy/requirements.txt
# COPY . /RecipeAlchemy
# CMD ["uvicorn", "RecipeAlchemy.app:app", "--host", "0.0.0.0", "--port", "80"]