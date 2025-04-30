FROM python:3.9

RUN pip install pandas rich psycopg2-binary sqlalchemy pyarrow

WORKDIR /app

COPY ingest.py .

ENTRYPOINT [ "python","ingest.py" ]