# Presence detection

This is a container/program for detecting Bluetooth device without need of pairing it. It is usually used to detect the mobile phone and consider person carrying this device as near by.

I found the best device to run the docker on Raspberry PI (from Zero up to PI4). Of course, this docker can work on many other devices (even device which runs Linux like CoreELEC on Odroid and others), just it is necessary to have a bluetooth adapter (internal or USB one) and working driver installed.

This container utilize Bluetooth classic to detect the device i.e. Phone via MAC address. Indeed, primary reason is to detect person inside/outside the house to trigger further actions such as check for windows open/close status, switch off/on the lights, sockets etc. anything you imagine. This docker utilize MQTT protocol and Home Assistant MQTT Discovery protocol for plug & play integration, link https://www.home-assistant.io/docs/mqtt/discovery/

Docker image is available on https://hub.docker.com/r/salvq/presence

Note: Using Home Assistant is not must but very recommended. More details information for using without Home Assistant are available in General usage section.

## Change log

Docker image 2.4.0
- adjusted Last Will and Testament message, first message published after successful connection to broker
- update to arm32v5/python:3.10-buster base image
- syntax updates

Docker image 2.3.0
- initial version

## Supported Platforms

* linux/arm/v5 and up

## Prerequsities

<details>
<summary>1. Prepare Raspberry PI</summary>

###
a. Flash the PI OS like Raspberry Pi OS Lite (32bit) using Rufus or Raspberry Pi Imager
- image example for RPI ZERO W is `2023-05-03-raspios-bullseye-armhf-lite.img`

###
b. Create several files and copy to SD card root folder:
- `ssh` to enable connection via ssh
- `wpa_supplicant.conf` to enable to connect via Wi-Fi (file has to be updated based on your wi-fi credentails)
- `userconf` userfile as specified by http://rptl.io/newuser (file includes login & password credential, login `pi` and password `password`)
- use ssh manager like putty to connect to PI (either use IP address or use raspberrypi.local instead)


c. Make neccessary settings via `pi@raspberrypi:~ $ sudo raspi-config`
```
1 - System Options -> S4 Hostname -> change as needed
5 - Localisation Option -> L2 Timezone -> change as needed
```

d. In case you want to disable wi-fi (like myself, I am using eth adapter to limit interferance wi-fi vs. bluetooth):

```
sudo nano /boot/config.txt
```

Add below to section `[all]`
```
[all]
dtoverlay=disable-wifi
```

Reboot the Pi
```
sudo reboot
```
</details>

<details>
<summary>2. Install Docker</summary>

###
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

d. Install python3
```
pi@raspberrypi:~ $ sudo apt-get install -y python3 python3-pip
```

e. Optionally install Docker compose if you intend to use ```docker-compose up``` instead of ```docker run```
```
pi@raspberrypi:~ $ sudo apt-get install libffi-dev libssl-dev
pi@raspberrypi:~ $ sudo apt-get install -y python3-bcrypt
pi@raspberrypi:~ $ sudo pip3 install docker-compose
```
</details>

<details>
<summary>3. Bluetooth adapter setup</summary>

###
Test whether your device has bluetooth enabled and can discover near by devices, try execute below commands. If you found similar results as below, you are ready from hardware and driver perspective, otherwise need to troubleshoot before continue. This docker relies on working Bluetooth hardware and software.

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
</details>

<details>
<summary>4. Validate pybluez discovery routine</summary>

###
a. Install python3 bluetooth library
```
$ pip3 install pybluez==0.23
Looking in indexes: https://pypi.org/simple, https://www.piwheels.org/simple
Requirement already satisfied: pybluez==0.23 in /home/pi/.local/lib/python3.7/site-packages (0.23)
$
```

b. Execute bluetooth lookup name routine
```
$ python3
Python 3.7.13 (default, Aug  3 2022, 02:00:49)
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import bluetooth
>>> from bluetooth import *
>>> bluetooth.lookup_name('AA:BB:CC:DD:EE:FF', timeout=5)
'iPhoneJ'
>>>
```

If you find an iPhone name listed, such as "iPhoneJ", you can proceed, if no name is listed, make sure the notes below are taken into account.

Note 1: Make sure your MAC address is not randomize as this presence detection check that relies on fixed MAC address (this might be case of Android, not iPhone).

Note 2: If you have encountered an undetected iPhone, it may be due to Bluetooth not being "used", make sure you have at least 1 device paired not necessary connected.

![image](https://user-images.githubusercontent.com/43242348/210435225-a165de71-596a-42da-aa77-f29b80179801.png)
</details>

<details>
<summary>5. HTTP server for serving `database.json` file</summary>

###
To make sharing json file easy across different devices and docker containers, I use HTTP server to localy expose `database.json`. Just copy `database.json` file to host folder, for instance `/share/Container/simplehttpserver/database.json`.

More details how to setup an easy HTTP server you can find on the [link](https://github.com/salvq/simplehttpserver)
</details>


## Download this repository to your PI


a. Create folder in your home folder
```
pi@raspberrypi:~ $ mkdir presence
pi@raspberrypi:~ $ cd presence
pi@raspberrypi:~ $ pwd
/home/pi/presence
```

b. Download repository
```
pi@raspberrypi:~ $ sudo apt update
pi@raspberrypi:~ $ sudo apt install git
pi@raspberrypi:~ $ git clone https://github.com/salvq/presence-detection.git
```

## Update MAC address of your Phones or other devices

Write down your MAC address from your Android or iPhone and create as many records as you want i.e. depends on how many persons / devices you want to detect. In my case, I am using to detect mine and my wife's phone, so I ended up having 2 MAC addresses. Every "name" value must be unique i.e. do not use 2 same names as this would break the logic of sensing and detecting the individual persons.

Edit `database.json` file and add as many records as needed in devices section but must follow JSON content structure and file must be located on server via HTTP request

Content of `database.json` file is following:

```
{
  "devices": [
    {
      "name": "Name1",
      "mac": "AB:CD:34:62:BA:12"
    },
    {
      "name": "Name2",
      "mac": "BA:DC:43:26:AB:21"
    }
  ]
}       
```

## Docker start-up

Run command to start the docker instance for `docker run`
```
docker run -d \
--name presence \
--privileged \
--net=host \
--restart=always \
-e HOST=192.168.5.76 \
-e PORT=1883 \
-e USER=login \
-e PASSWORD=password \
-e LOCATION=roomA \
-e LOGGING=DEBUG \
-e DBASE=http://192.168.5.76:8019/presence/database.json \
-v /etc/localtime:/etc/localtime:ro \
salvq/presence:2.3.0
```

Optionally navigate to folder with downloaded repository and run command to start the docker instance for `docker-compose.yaml`
```
pi@raspberrypi:~ $ cd /home/pi/presence/presence-detection
pi@raspberrypi:~ $ docker-compose up -d
```

Content of `docker-compose.yaml`

```
version: '3'

services:
  presence:
    image: salvq/presence:2.3.0
    container_name: presence
    restart: unless-stopped
    network_mode: host
    privileged: true
    environment:
      - HOST=192.168.5.76
      - PORT=1883
      - USER=login
      - PASSWORD=passowrd
      - LOCATION=roomA
      - LOGGING=DEBUG
      - DBASE=http://192.168.5.76:8019/presence/database.json
    volumes:
      - /etc/localtime:/etc/localtime:ro
```

### Container configuration details

Optionally edit and update `docker-compose.yaml` file based on your needs. Minimal config of docker-compose.yaml file is following:

| Name         | Environment | Default | Description                                                                      |
| ------------ | ----------- | ------- | -------------------------------------------------------------------------------- |
| HOST         | REQUIRED    | NONE    | MQTT broker IP address, example HOST=192.168.89.56                       |
| PORT         | REQUIRED    | NONE    | MQTT broker PORT, example PORT=1883                       |
| USER         | REQUIRED    | NONE    | MQTT broker user authetification, example USER=name                       |
| PASSWORD     | REQUIRED    | NONE    | MQTT broker password authetification, PASSWORD=secret                       |
| LOCATION     | REQUIRED    | NONE    | Location of device running this docker like bedroom, example LOCATION=bedroom |
| DBASE        | REQUIRED    | NONE    | Location of your database.json file, example http://192.168.5.76:8019/presence/database.json |
| CLEANSESSION | OPTIONAL    | FALSE   | MQTT advance settings, possible value FALSE or TRUE                       |
| WILLQOS      | OPTIONAL    | 1       | Last Will and Testament QOS (possible value 0, 1 or 2)                       |
| WILLRETAIN   | OPTIONAL    | TRUE    | Last Will and Testament retain message (possible FALSE or TRUE)                       |
| MSGQOS       | OPTIONAL    | 1       | Publish message QOS (possible value 0, 1 or 2)                       |
| MSGRETAIN    | OPTIONAL    | TRUE    | Publish retain message (possible FALSE or TRUE)                       |
| SUBSQOS      | OPTIONAL    | 1       | Subscribe to topic with QOS message (possible value 0, 1 or 2)                       |
| TIMEOUTSCAN  | OPTIONAL    | 2       | Bluetooth timeout scanning in seconds (if devices is not found during this time, it is considered as not found)  |
| SLEEPBETWEEN | OPTIONAL    | 5       | Waiting time between two scans in seconds (improve wi-fi / bluetooth coesistence)                       |
| LOGGING      | OPTIONAL    | INFO    | When it is needed to increase verbose and debug (possible value INFO or DEBUG) |



## Home Assistant integration (recommended)

**a. Create template sensor which will be updated based on all the locations.**

Example below describes 3 devices in total, one in bedroom, second one in hall and 3rd one is kidsroom. If there is at least phone detected in either one of the rooms, sensor turns to `Home`, if all the 3 devices provides results as off sensor turns to `Away`. If the programs are shut down or not available (program is not running), sensor turns to `Unknown`. 

Note: name1 in the sensors below has to be renamed to the one from your database.json file or can be find in Home Assistant new created device.

```
# Example configuration entry
template:
  sensor:
    - name: Name1_presence_evaluation
      unique_id: '0a7476bb-d6ce-40ba-8aes-606528c3497f'
      state: >-
        {% if is_state('device_tracker.name1_bedroom', 'unavailable') or is_state('device_tracker.name1_hall', 'unavailable') or is_state('device_tracker.name1_kidsroom', 'unavailable') %}
          Unknown
        {% elif is_state('device_tracker.name1_bedroom', 'on') or is_state('device_tracker.name1_hall', 'on') or is_state('device_tracker.name1_kidsroom', 'on') %}
          Home
        {% elif is_state('device_tracker.name1_bedroom', 'off') and is_state('device_tracker.name1_hall', 'off') and is_state('device_tracker.name1_kidsroom', 'off')  %}
          Away
        {% else %}
          Unknown
        {% endif %}
```

**b. create automation which triggers the scanning**

Example below shows configuration which triggers the scanning. Scanning below is triggered by opening doors like garage door, gate door, main door or even Home Assistant restart. After the trigger, automation waits for another minute (optional) to trigger the scanning by sending the payload `on` to all the 3 devices.

Note: triggers sensors have to be updated based on your configuration. The mqtt topics can be detected by listenning the general topic `presence/#`, by reading the docker log or in Home Assistant new created device.

```
automation:
- id: '1629390836472'
  alias: Presence trigger
  description: ''
  trigger:
  - platform: state
    entity_id:
    - binary_sensor.0xa4c13811329a1502_contact
  - platform: state
    entity_id:
    - binary_sensor.0xa4c138345ec22a63_contact
  - platform: state
    entity_id:
    - sensor.garage_door_status
  - platform: homeassistant
    event: start
  condition: []
  action:
  - service: mqtt.publish
    data:
      topic: presence/0xb956eb36ca0d/bedroom/set
      payload: 'on'
  - service: mqtt.publish
    data:
      topic: presence/0xa09ec1325f2c/kidsroom/set
      payload: 'on'
  - service: mqtt.publish
    data:
      topic: presence/0xb342eb36ca0c/hall/set
      payload: 'on'
  mode: restart
```


## General usage without Home Assistant

**To trigger the scanning, type in**

`pi@raspberrypi:~ $ sudo mosquitto_pub -h 192.168.5.76 -u login -P password -t presence/0xb342eb36ca0c/hall/set -m 'on'`


**To listen to PI device, just type in:**

a. for CONFIG topic

`pi@rraspberrypi:~ $ sudo mosquitto_sub -h 192.168.5.76 -u login -P password -t homeassistant/device_tracker/# -v`

b. for WILL and/or STATE topic:

`pi@rraspberrypi:~ $ sudo mosquitto_sub -h 192.168.5.76 -u login -P password -t presence/# -v`


**Topic explanation:**

| Topic     | Description     |
| --------- | ------------------------------------------------------------------------------------------------------- |
| CONFIG    | This topic configure Home Assistant sensors, `homeassistant/device_tracker/Name1_0xb342eb36ca0c/presence/config`. `Name1` is name in `database.json` and `0xb342eb36ca0c` is mac address of the device running docker. It uses HA MQTT discovery protocol, see https://www.home-assistant.io/docs/mqtt/discovery/. |
| WILL      | This TOPIC provides information about program status wheter is only or offline, `presence/0xb342eb36ca0c/hall/lwt online` or `presence/0xb342eb36ca0c/hall/lwt offline`. Where `0xb342eb36ca0c` is mac address of the device running docker and `hall` is location. |
| SUBSCRIBE | Topic which PI device subscribe to is used to start/trigger scanning (using `on` as payload), `presence/0xb342eb36ca0c/hall/set on`. Where `0xb342eb36ca0c` is mac address of the device running docker and `hall` is location.               |
| STATE     | This is the topic that PI device provide results to whether the `Name1` device is found near by or not, `presence/0xb342eb36ca0c/hall/Name1 on` or `presence/0xb342eb36ca0c/hall/Name1 off`. Where `0xb342eb36ca0c` is mac address of the device running docker, `hall` is location and `Name1` is name in `database.json`      |
