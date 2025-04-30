

import pandas as pd
from sqlalchemy import create_engine
from rich.console import Console
import argparse
import time

print = Console().print

# URL = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet'


def main(params):
    
    # define parameters
    URL = params.url
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table = params.table
    file = params.file

    
    max_retries = 10
    retrial_interval = 5

    try:
        for retry in range(max_retries):
            # create connection to db
            print(f'Attempting to connect to database {db} retry {retry+1}/{max_retries}')

            engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

            print(f'Connecting to database {db} on {host}:{port}')
            
            engine.connect()

    except Exception as e:
        print(f'Connection attenpt {retry+1} failed: {e}')
        if retry < max_retries -1:
            print(f'Retrying in {retrial_interval} seconds...')
            time.sleep(retrial_interval)
        else:
            print(f'Failed to connect to database {db} after {max_retries} attempts')
            raise e
        

    print(f'Connected to database {db} on {host}:{port}')

    pq = pd.read_parquet(URL,engine='pyarrow')
    print(f'Loaded data from {URL}')

    pq.to_csv(file, index=False)
    print(f'Converted data to csv and saved to {file}')

    df_iter = pd.read_csv(file,iterator=True,chunksize=100000)

    df = next(df_iter)

    df.head(0).to_sql(con=engine,name=table,if_exists='replace')
    print(f'Created table {table} in database {db}')

    chunk_number = 0

    while True:
        start = time.time()

        df = next(df_iter)

        df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
        df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

        df.to_sql(con=engine,name=table,if_exists='append')

        end = time.time()

        chunk_number += 1
        print(f'Inserted chunck {chunk_number} in {end-start:.3f} seconds')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ingest data from S3 to postgres')
    parser.add_argument('--user', help='foo help')
    parser.add_argument('--password', help='Database password')
    parser.add_argument('--host', help='Database host')
    parser.add_argument('--port', help='Database port')
    parser.add_argument('--db', help='Database name')
    parser.add_argument('--table', help='Table name')
    parser.add_argument('--url', help='Table name')
    parser.add_argument('--file', help='File name')

    args = parser.parse_args()

    print(args)

    main(args)



