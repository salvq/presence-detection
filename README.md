# Presence detection

This is a container/program for detecting Bluetooth device without need of pairing it. It is usually used to detect the mobile phone and consider person carrying this device as near by.

I found the best device to run the docker on Raspberry PI (from Zero up to PI4). Of course, this docker can work on many other devices (even device which runs Linux like CoreELEC on Odroid and others), just it is necessary to have a bluetooth adapter (internal or USB one) and working driver installed.

This container utilize Bluetooth classic to detect the device i.e. Phone via MAC address. Indeed, primary reason is to detect person inside/outside the house to trigger further actions such as check for windows open/close status, switch off/on the lights, sockets etc. anything you imagine. This docker utilize MQTT protocol and Home Assistant MQTT Discovery protocol for plug & play integration, link https://www.home-assistant.io/docs/mqtt/discovery/

Note: Using Home Assistant is not must but very recommended as it provides easy integration of other devices and connecting anything with everything.

## Supported Platforms

* linux/arm

## Prerequisites

**1. Docker readiness:**

a. Install Docker
```
pi@raspberrypi:~ $ sudo curl -fsSL https://get.docker.com -o get-docker.sh
pi@raspberrypi:~ $ sudo sh get-docker.sh
```

b. Add the permissions to the current user to run Docker commands
```
pi@raspberrypi:~ $ sudo usermod -aG docker pi
pi@raspberrypi:~ $ sudo docker version
```

c. Enable docker when system bootup
```
pi@raspberrypi:~ $ sudo systemctl enable docker
```

d. Install Docker compose
```
pi@raspberrypi:~ $ sudo apt-get install libffi-dev libssl-dev
pi@raspberrypi:~ $ sudo apt install python3-dev
pi@raspberrypi:~ $ sudo apt-get install -y python3 python3-pip
pi@raspberrypi:~ $ sudo pip3 install docker-compose
```

**2. Bluetooth adapter**

Test whether your device has bluetooth enabled and can discover near by devices, try execute following codes. If you found similar results as below, you are ready from Hardware and driver perspective.

```
$ hciconfig
hci0:   Type: Primary  Bus: UART
        BD Address: 34:B3:EA:C9:32:F5  ACL MTU: 1021:8  SCO MTU: 64:1
        UP RUNNING
        RX bytes:3794 acl:0 sco:0 events:124 errors:0
        TX bytes:2722 acl:0 sco:0 commands:108 errors:0

$ sudo hcitool lescan
LE Scan ...
21:7C:5B:BA:BB:01 (unknown)
59:7C:5B:BA:BC:01 (unknown)
22:35:1A:C8:31:C5 (unknown)
$
```

**3. Bluetooth MAC addresses**

Write down your MAC address from your Android or iPhone and create as many records as you want i.e. depends on how many persons / devices you want to detect. In my case, I am using to detect mine and my wife's phone, so I ended up having 2 MAC addresses.

Note: Make sure your MAC address is not randomize as this presence detection check rely on fixed MAC address. And every name must be unique i.e. do not use 2 same names as this would break the logic of topic vs. sensor states.

Edit `database.json` file and add as many records as needed in devices section but must follow JSON content structure and file must be located in the same files as `docker-compose.yaml`

Content of `database.json` file is following:

```
{
  "devices": [
    {
      "name": "Name 1",
      "mac": "AB:CD:34:62:BA:12"
    },
    {
      "name": "Name 2",
      "mac": "BA:DC:43:26:AB:21"
    }
  ]
}       
```

## Docker start-up

Run command `pi@raspberrypi:~ $ docker-compose up -d` in shell where are located files `database.json` and `docker-compose.yaml`

Content of `docker-compose.yaml` file is following:

```
version: '3'

services:
  test:
    image: salvq/presence:1.5.0
    container_name: presence
    restart: unless-stopped
    network_mode: host
    privileged: true
    environment:
      - HOST=192.168.78.156
      - PORT=1883
      - USER=ABC
      - PASSWORD=EFG
      - LOCATION=hall
    volumes:
      - ./database.json:/presence/database.json
      - /etc/localtime:/etc/localtime:ro
```

## Container Configuration

| Name         | Environment | Default | Description                                                                      |
| ------------ | ----------- | ------- | -------------------------------------------------------------------------------- |
| HOST         | REQUIRED    | NONE    | MQTT broker IP address, example HOST=192.168.89.56                       |
| PORT         | REQUIRED    | NONE    | MQTT broker PORT, example PORT=1883                       |
| USER         | REQUIRED    | NONE    | MQTT broker user authetification, example USER=name                       |
| PASSWORD     | REQUIRED    | NONE    | MQTT broker password authetification, PASSWORD=secret                       |
| LOCATION     | REQUIRED    | NONE    | Location of device running this docker like bedroom, example LOCATION=bedroom |
| CLEANSESSION | OPTIONAL    | FALSE   | MQTT advance settings, possible value FALSE or TRUE                       |
| WILLQOS      | OPTIONAL    | 1       | Last Will and Testament QOS (possible value 0, 1 or 2)                       |
| WILLRETAIN   | OPTIONAL    | TRUE    | Last Will and Testament retain message (possible FALSE or TRUE)                       |
| MSGQOS       | OPTIONAL    | 1       | Publish message QOS (possible value 0, 1 or 2)                       |
| MSGRETAIN    | OPTIONAL    | TRUE    | Publish retain message (possible FALSE or TRUE)                       |
| TIMEOUTSCAN  | OPTIONAL    | 2       | Bluetooth timeout scanning in seconds (if devices is not found during this time, it is considered as not found)  |
| SLEEPBETWEEN | OPTIONAL    | 5       | Waiting time between two scans in seconds (improve wi-fi / bluetooth coesistence)                       |
| LOGGING      | OPTIONAL    | INFO    | When it is needed to increase verbose and debug (possible value INFO or DEBUG) |


## Usage

TBA

## Integration with Home Assistant

TBA
