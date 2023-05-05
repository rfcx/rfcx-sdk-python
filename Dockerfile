FROM python:3.9-buster

WORKDIR /usr/src/app

RUN apt update && apt -y install libsndfile-dev
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
