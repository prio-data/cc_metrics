FROM python:3.8
COPY requirements.txt /
RUN pip install -r requirements.txt
COPY /* /cc_ged/
CMD ["gunicorn","-b","0.0.0.0:80","-k","uvicorn.workers.UvicornWorker","--forwarded-allow-ips","*","--proxy-allow-from","*","cc_ged.app:app"]
