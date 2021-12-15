FROM python:3.8.0-slim

COPY ./ ./

RUN apt-get update && apt-get install gcc -y && apt-get clean

RUN pip install --user -r requirements.txt

WORKDIR App

CMD ["python", "FastAPI.py"]