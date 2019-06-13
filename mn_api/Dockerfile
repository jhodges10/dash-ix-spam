FROM python

COPY . /bin

RUN pip install -r bin/requirements.txt

EXPOSE 5000

CMD ["python", "/bin/index.py", "-p 5000"]
