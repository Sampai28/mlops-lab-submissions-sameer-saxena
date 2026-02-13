#!/bin/bash

# Start Airflow webserver in background
airflow webserver --port 8080 &

# Start Airflow scheduler in background
airflow scheduler &

# Wait a few seconds for Airflow to start
sleep 5

# Start Streamlit in foreground
streamlit run streamlit/app.py --server.port 8501 --server.address 0.0.0.0