import time, socket, os, subprocess, ast, bluetooth, logging, logging.handlers
from configparser import ConfigParser
from urllib.request import urlopen
import paho.mqtt.client as mqttClient
import sys, re, uuid
import json, random
import platform

# Read hostname
socket_name = socket.gethostname()

# Read MAC address
hex_mac_address = hex(uuid.getnode())

# Generate client id
client_id_random = socket_name + '_' + hex_mac_address + str(random.randint(0,1000))

# Retrieve required env. variables
if 'HOST' not in os.environ or 'PORT' not in os.environ or 'USER' not in os.environ or 'DBASE' not in os.environ or 'LOCATION' not in os.environ or not 'PASSWORD' in os.environ:
    print("Required enviroment variable are missing, define and re-run program!")
    sys.exit()
else:
    host = os.environ['HOST']
    port = int(os.environ['PORT'])
    user_name = os.environ['USER']
    password = os.environ['PASSWORD']
    location = os.environ['LOCATION']
    dbase = os.environ['DBASE']

# create and set logger level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create handlers (with file rotation)
stream_handler = logging.StreamHandler()
syslog_handler = logging.handlers.SysLogHandler(address=(host, 514))

# create and set formatter
formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(name)s,%(message)s',datefmt='%Y/%m/%dT%H:%M:%S')
syslog_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# set handler level (debug -> info -> warning -> error -> critical)
if os.environ.get('LOGGING') == 'DEBUG':
    syslog_handler.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.DEBUG)
else:
    syslog_handler.setLevel(logging.INFO)
    stream_handler.setLevel(logging.INFO)

# attach handler to logger
logger.addHandler(stream_handler)
logger.addHandler(syslog_handler)

# Set optional env. variables to default values
clean_session = os.environ.get('CLEANSESSION', False)
will_qos = os.environ.get('WILLQOS', 1)
will_retain = os.environ.get('WILLRETAIN', True)
subs_qos = os.environ.get('SUBSQOS', 1)
msg_qos = os.environ.get('MSGQOS', 1)
msg_retain = os.environ.get('MSGRETAIN', True)
will_topic = 'presence/'+hex_mac_address+'/'+location+'/lwt'
publish_topic = 'presence/'+hex_mac_address+'/'+location
subscribed_topic = 'presence/'+hex_mac_address+'/'+location+'/set'
timeout_scan = os.environ.get('TIMEOUTSCAN', 2)
sleep_between = os.environ.get('SLEEPBETWEEN', 5)

logger.info(f'Program started')

# Read device model
with open('/proc/device-tree/model') as f:
    full_model = f.read()
    mfg = full_model.split()[0]

# Open mac database JSON file
with urlopen(dbase) as openfile:
    logger.info(f'Reading MAC from http json file: {dbase}')
    database = json.load(openfile)

def on_log(client, userdata, level, buf):
    logger.debug(f'on_log: {buf}')

def on_connect(client, userdata, flags, rc):
    logger.info(f'Server connected to broker, rc code: {rc}')
    client.publish(will_topic, 'online', will_qos, will_retain)
    client.subscribe(subscribed_topic, subs_qos)
    for name in database["devices"]:
        unique_id = name["name"] + '_' + hex_mac_address
        sensor_name = name["name"] + ' ' + location
        state_topic = 'presence/'+hex_mac_address+'/'+location+'/'+name["name"]
        config_topic = 'homeassistant/device_tracker/'+unique_id+'/presence/config'
        print(state_topic)
        print(config_topic)
        data_set = {
          "device": {
            "identifiers": [
              hex_mac_address
            ],
            "manufacturer": mfg,
            "model": full_model,
            "name": hex_mac_address
          },
          "name": sensor_name,
          "unique_id": unique_id,
          "state_topic": state_topic,
          "availability_topic": will_topic,
          "payload_available": 'online',
          "payload_not_available": 'offline'
        }
        config_payload = json.dumps(data_set)
        client.publish(config_topic, payload=config_payload, qos=msg_qos, retain=msg_retain)

def on_disconnect(client, userdata, rc):
    logger.info(f'Server disconnected from broker, rc code: {rc}')

def on_message(client, userdata, msg):
    logger.info(f'Message received, topic: {msg.topic}, qos: {msg.qos}, payload: {msg.payload}')
    if msg.payload.decode() == "on":
        scan()
    else:
        logger.info(f'Received unknown payload, topic: {msg.topic}, qos: {msg.qos}, payload: {msg.payload}')
        return

def on_subscribe(client, userdata, mid, granted_qos):
    logger.info(f'Client subscribed to topic: {subscribed_topic}, with callback mid: {mid}')

def scan():
    for device in database["devices"]:
        logger.debug(f'Searching for {device["mac"]}')
        result = bluetooth.lookup_name(device['mac'], timeout=timeout_scan)
        if result:
            device['state'] = 'on'
            logger.debug(f'Found {device["mac"]}')
        else:
            device['state'] = 'off'
            logger.debug(f'Not found {device["mac"]}')
        time.sleep(sleep_between) # ble & wifi coexistence behaviour, sleeping between scans to decrease number of network drops
        client.publish(f'{publish_topic}/{device["name"]}', payload=device['state'], qos=msg_qos, retain=msg_retain)
        logger.debug(f'Message published for mac: {device["mac"]} with state {device["state"]}')
        time.sleep(sleep_between) # ble & wifi coexistence behaviour, sleeping between scans to decrease number of network drops

# create client instance and set connection parameters
client = mqttClient.Client(client_id_random, clean_session, userdata=None, protocol=mqttClient.MQTTv311, transport='tcp')
client.username_pw_set(user_name, password)
client.will_set(will_topic, 'offline', will_qos, will_retain)

# attach function to callback
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_log = on_log
client.on_message = on_message
client.on_subscribe = on_subscribe

# set initial connection flag, connect to broker and start the loop
client.connect(host, port, keepalive=120, bind_address='')
client.loop_forever()
