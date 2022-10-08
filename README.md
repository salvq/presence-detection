# Presence detection

This is a container/program for detecting Bluetooth device without need of pairing. It is usually used to detect the mobile phone and consider person carrying this device is near by.

I found the best device to run the docker on Raspberry PI (any model is fine). Of course, this docker can work on many other devices (even device which runs CoreELEC like Odroid and others), just it is necessary to have a bluetooth adpter or built in driver installed and worked.

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
d. sudo systemctl enable docker
```

e. Install Docker compose
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

$ hcitool -i hci0 scan
Scanning ...
	FC:XX:XX:XX:XX:FE	n/a
```

**3. Bluetooth MAC addresses**

Write down your MAC address from your Android or iPhone and create as many records as you want i.e. depends on how many persons / devices you want to detect. In my case, I am using to detect mine and my wife's phone, so I ended up having 2 MAC addresses.

Note: Make sure your MAC address is not randomize as this presence detection check rely on fixed MAC address.

Edit `database.json` file and add as many records as desired but must follow JSON content structure, file must be located in the same files as `docker-compose.yaml`

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

Run command `[~] # docker-compose up -d` in shell where are located files `database.json` and `docker-compose.yaml`

```
version: '3'

services:
  test:
    image: salvq/presence:1.1.0
    container_name: presence
    restart: unless-stopped
    network_mode: host
    privileged: true
    environment:
      - HOST=192.168.78.156
      - PORT=1883
      - USER=ABC
      - PASSWORD=EFG
      - LOCATION=bedroom
    volumes:
      - ./database.json:/presence/database.json
      - /etc/localtime:/etc/localtime:ro
```

## Container Configuration

| Name         | Enviromental variable | Description                                                                      |
| ------------ | ----------------------|--------------------------------------------------------------------------------- |
| HOST         | REQUIRED              | MQTT broker IP address, example HOST=192.168.89.56                       |
| PORT         | REQUIRED              | MQTT broker PORT, example PORT=1883                       |
| USER         | REQUIRED              | MQTT broker user authetification, example USER=name                       |
| PASSWORD     | REQUIRED              | MQTT broker password authetification, PASSWORD=secret                       |
| LOCATION     | REQUIRED              | Location of device like bedroom, example LOCATION=bedroom |
| CLEANSESSION | OPTIONAL              | MQTT advance settings, possible value FALSE or TRUE, default value FALSE                       |
| WILLQOS      | OPTIONAL              | Last Will and Testament QOS (possible value 0, 1 or 2), default value 1                       |
| WILLRETAIN   | OPTIONAL              | Last Will and Testament retain message (possible FALSE or TRUE), default value TRUE                       |
| MSGQOS       | OPTIONAL              | Publish message QOS (possible value 0, 1 or 2), default value 1                       |
| MSGRETAIN    | OPTIONAL              | Publish retain message (possible FALSE or TRUE), default value TRUE                       |
| TIMEOUTSCAN  | OPTIONAL              | Bluetooth timeout scanning in seconds (detect device as off after this time), default value 2  |
| SLEEPBETWEEN | OPTIONAL              | Waiting time between two scans in seconds (improve wi-fi / bluetooth coesistence), default value 5                       |
| LOGGING      | OPTIONAL              | When it is needed to increase verbose and debug (possible value INFO or DEBUG), default value is INFO |


## Usage

TBA

## Integration with Home Assistant

TBA
