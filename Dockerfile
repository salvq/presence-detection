FROM arm32v5/python:3.10-buster

ADD script /script
WORKDIR /script

RUN apt-get update && apt-get install -y \
    bluetooth libbluetooth-dev \
    && pip install -r ./requirements.txt

CMD [ "python", "./presence.py"]
