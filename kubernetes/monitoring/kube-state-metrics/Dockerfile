FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir kubernetes prometheus-client

COPY kube-state-exporter.py /app/

EXPOSE 8080

CMD ["python", "kube-state-exporter.py"]
