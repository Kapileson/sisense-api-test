# Sisense-Sanity-Test
API test framework to compare SISENSE and BIGQUERY. \
Tools/Language Used: Python, Pytest, Requests, BigQueryPython, GCS and Docker.

## Environment variables needed:
1. SISENSE_USERNAME
2. SISENSE_PASSWORD
3. GOOGLE_APPLICATION_CREDENTIALS
4. ENVIRONMENT
5. DASHBOARD_NAME
6. FROM_ADDR
7. TO_ADDR
8. FROM_PASSWORD
9. THREAD

## Setup:
1. setup a python virtual environment
2. pip install -r requirememts.txt

## Docker Execution:
./build/run.sh

## Pytest Execution:
pytest --html=report.html --self-contained-html -s -v -n $THREAD $DASHBOARD
