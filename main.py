from rich.console import Console
from rich.style import Style
import requests
import json
import time
import dlt
import duckdb


console = Console()
style = Style(color='green', bold=True)
console.print("Starting the paginated data retrieval...", style=style)
URL = "https://storage.googleapis.com/dtc_zoomcamp_api/yellow_tripdata_2009-06.jsonl"
BASE_API_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"


def paginated_data():

    page_number = 1

    param = {
        'page': page_number
    }

    while True:
        response = requests.get(BASE_API_URL, params=param)
        response.raise_for_status()

        res_json = response.json()

        console.print(
            f"Page {page_number} retrieved successfully with {len(res_json)} records.")

        if res_json:
            yield res_json
            page_number += 1
        else:
            console.print("No data to retrieve.", style=style)
            break
        if page_number >= 10:
            console.print(
                "Reached the maximum number of pages to retrieve.", style=style)
            break


def stream_download_json(URL):
    response = requests.get(URL, stream=True)
    response.raise_for_status()

    for line in response.iter_lines():
        if line:
            yield json.loads(line)


# def dlt_pipeline():
generators_pipeline = dlt.pipeline(
    destination='duckdb',
    dataset_name='generators'
)

# info = generators_pipeline.run(
#     paginated_data(),
#     table_name='http_download',
#     write_disposition='replace',
# )

# console.print(f"Pipeline info: {info}", style=style)

# info = generators_pipeline.run(
#     stream_download_json(URL),
#     table_name='stream_download',
#     write_disposition='replace',
# )
# console.print(f"Pipeline info: {info}", style=style)


if __name__ == "__main__":

    # for page_data in paginated_data():
    #     console.print(page_data)
    # console.print("Paginated data retrieval completed.", style=style)

    # start = time.time()
    # row_counter = 0

    # for row in stream_download_json(URL):
    #     console.print(row)
    #     row_counter += 1
    #     if row_counter >= 5:
    #         break

    # dlt_pipeline()
    # end = time.time()

    conn = duckdb.connect(
        f'{generators_pipeline.pipeline_name}.duckdb'
    )

    conn.sql(f"SET search_path='{generators_pipeline.dataset_name}'")
    console.print('Loaded tables: ')
    console.print(conn.sql("SHOW TABLES"))

    console.print('Table http_download:')
    console.print(conn.sql("SELECT * FROM http_download LIMIT 200"))

    console.print('Table stream_download:')
    console.print(conn.sql("SELECT * FROM stream_download LIMIT 200"))


# print(f"Downloaded {row_counter} rows in {end - start:.2f} seconds.")
