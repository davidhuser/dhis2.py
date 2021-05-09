FROM python:3

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install pipenv

RUN mkdir /code
WORKDIR /code

COPY Pipfile .
RUN pipenv install --dev

ENTRYPOINT ["pipenv", "run"]
CMD ["tests"]