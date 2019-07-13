FROM python:3-alpine as base

FROM base as builder
RUN apk --no-cache add build-base
RUN apk --no-cache add postgresql-dev
RUN python3 -m pip install psycopg2


# Because context is set in docker compose, we're already in /scraper when we start the build
FROM builder as pip
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

FROM pip

COPY . .
EXPOSE 5000

CMD ["python", "/bin/peewee_test.py", "-p 5000"]
