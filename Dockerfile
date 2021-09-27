FROM prioreg.azurecr.io/prio-data/uvicorn_deployment:latest
COPY requirements.txt /
RUN pip install -r requirements.txt
COPY /cc_metrics /cc_metrics
COPY compute_metrics.py /compute_metrics.py
ENV APP cc_metrics.app:app
