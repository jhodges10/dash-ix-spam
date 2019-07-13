FROM python:3-alpine as base

FROM base as pip
COPY requirements.txt bin/requirements.txt
RUN pip install -r bin/requirements.txt

FROM pip
COPY . /bin

CMD ["python", "/bin/zmq_test.py"]