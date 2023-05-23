FROM python:3.11 as requirements-stage
RUN pip install poetry
WORKDIR /tmp
COPY poetry.lock pyproject.toml /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
FROM python:3.11
COPY --from=requirements-stage /tmp/requirements.txt /RecipeAlchemy/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /RecipeAlchemy/requirements.txt
COPY . /RecipeAlchemy
WORKDIR /RecipeAlchemy
CMD ["gunicorn", "RecipeAlchemy.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80"]
#CMD ["poetry", "run", "gunicorn", "RecipeAlchemy.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:80"]

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