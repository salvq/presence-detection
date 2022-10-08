# Presence detection

This is a container/program for detecting Bluetooth device without need of pairing. It is usually used to detect mobile phone and consider person owning this device is near by.

This container utilize Bluetooth classic to detect the device i.e. Phone via MAC address. Indeed, primary reason is to detect person inside/outside the house to trigger further actions such as check for windows open/close status, switch off/on the lights, sockets etc. anything you imagine. This docker utilize MQTT protocol and Home Assistant MQTT Discovery protocol for plug & play integration, link https://www.home-assistant.io/docs/mqtt/discovery/

Note: Using Home Assistant is not must but very recommended as it provides easy integration of other devices and connecting anything with everything.

## Supported Platforms

* linux/arm

## Prerequisites

Write down your MAC address from your Android or iPhone and create as many records as you want i.e. depends on how many persons / devices you want to detect. In my case, I am using to detect mine and my wife's phone, so I ended up having 2 MAC addresses.

Note: Make sure your MAC address is not randomize as this presence detection check rely on fixed MAC address.

Edit database.json file and update as many records as desired, file must be located in the same files as docker-compose.yaml

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

## Container Configuration

| Name         | Enviromental variable | Description                                                                      |
| ------------ | ----------------------|--------------------------------------------------------------------------------- |
| HOST         | REQUIRED              | MQTT broker IP address, example HOST=192.168.89.56                       |
| PORT         | REQUIRED              | MQTT broker PORT, example PORT=1883                       |
| USER         | REQUIRED              | MQTT broker user authetification, example USER=name                       |
| PASSWORD     | REQUIRED              | MQTT broker password authetification, PASSWORD=secret                       |
| LOCATION     | REQUIRED              | Location of device like bedroom, example LOCATION=bedroom |
| CLEANSESSION | OPTIONAL              | MQTT advance settings, default value FALSE                       |
| WILLQOS      | OPTIONAL              | MQTT advance settings, default value FALSE                       |
| WILLRETAIN   | OPTIONAL              | MQTT advance settings, default value FALSE                       |
| MSGQOS       | OPTIONAL              | MQTT advance settings, default value FALSE                       |
| MSGRETAIN    | OPTIONAL              | MQTT advance settings, default value FALSE                       |
| MSGQOS       | OPTIONAL              | MQTT advance settings, default value FALSE                       |
| TIMEOUTSCAN  | OPTIONAL              | MQTT advance settings, default value FALSE                       |
| SLEEPBETWEEN | OPTIONAL              | MQTT advance settings, default value FALSE                       |

If the `BEGIN` command is set, then the `INTERVAL` will be set to 1440 (one day) automatically. If you want to override this then set `INTERVAL` to the delay you want (you can also set it to `0` to exit immediately).
