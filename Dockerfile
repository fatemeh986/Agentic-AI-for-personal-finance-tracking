FROM python:3.11-slim

WORKDIR /financial_agent

ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY agent ./agent
COPY ui ./ui
COPY api ./api
COPY data ./data

EXPOSE 8000

CMD ["chainlit", "run", "ui/app.py", "--host", "0.0.0.0", "--port", "8000"]