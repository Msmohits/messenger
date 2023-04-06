FROM python:3.10-slim-buster

WORKDIR /app

COPY requirement.txt requirement.txt

RUN pip install -r requirement.txt

RUN apt-get update

RUN apt-get install rabbitmq-server -y

COPY . .

EXPOSE 8001

CMD ["python", "core.py"]