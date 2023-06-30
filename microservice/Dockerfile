FROM python:3.10.6-slim

WORKDIR /microservice
COPY . .

RUN pip install -r ./requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]