FROM arm32v5/python:3.7-buster
#FROM arm32v7/python:3.7-buster

ADD script /script
WORKDIR /script

RUN apt-get update && apt-get install -y \
    bluetooth libbluetooth-dev \
    && pip install -r requirements.txt \
    && chmod +x ./presence.py

CMD [ "python", "./presence.py"]