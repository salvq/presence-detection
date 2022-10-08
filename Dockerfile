FROM arm32v7/python:3.7-buster

ADD . /presence
WORKDIR /presence

RUN apt-get update && apt-get install -y \
    bluetooth libbluetooth-dev

RUN pip install -r requirements.txt

CMD [ "python", "./presence.py"]
