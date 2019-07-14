FROM python:3-slim as base

FROM base as pip
COPY requirements.txt zmq/requirements.txt
RUN pip install -r zmq/requirements.txt

FROM pip
COPY . zmq/bin/

CMD ["python", "zmq/bin/zmq_worker.py"]