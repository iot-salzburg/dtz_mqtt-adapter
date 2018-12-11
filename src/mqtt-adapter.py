#!/usr/bin/env python3
#  -*- coding: utf-8 -*-

"""src.py: This module fetches heterogenious data from the Iot-Lab's MQTT_BORKER
(3D printer data previously bundled on node-red), converts it into the canonical dataformat as
specified in SensorThings and sends it in the Kafka message Bus.
If MQTT doesn't work, make sure that
1) you are listening on port 1883 (cmd: netstat -a)
2) mosquitto is running (cmd path/to/mosquitto mosquitto)
3) you can listen to the incoming MQTT data on chrome's MQTT Lens."""

import time
import re
import sys
import os
from datetime import datetime
import json
import logging
import socket
import pytz

# confluent_kafka is based on librdkafka, details in requirements.txt
from src.panta_rhei.client.panta_rhei_client import PantaRheiClient
import paho.mqtt.client as mqtt



__author__ = "Salzburg Research"
__version__ = "2.0"
__date__ = "11 Dezember 2018"
__email__ = "christoph.schranz@salzburgresearch.at"
__status__ = "Development"

# MQTT_BROKER = "il050.salzburgresearch.at"
MQTT_BROKER = "192.168.48.81"
SUBSCRIBED_TOPICS = ["prusa3d/#", "sensorpi/#", "octoprint/#"]


# # TODO get this data from the client config
# SENSORTHINGS_HOST = "192.168.48.81:8082"
# # SENSORTHINGS_PORT = "8084"
# # kafka parameters
# # topics and servers should be of the form: "topic1,topic2,..."
# KAFKA_TOPIC_metric = "dtz.sensorthings"
# KAFKA_TOPIC_logging = "dtz.logging"
# BOOTSTRAP_SERVERS = '192.168.48.81:9092,192.168.48.82:9092,192.168.48.83:9092'  # ,192.168.48.83:9095'
# KAFKA_GROUP_ID = "mqtt-adapter"
#
# # The mapping between incoming and outgoing metrics is defined by
# # The mapping between incoming and outgoing metrics is defined by
# # the json file located on:
# dir_path = os.path.dirname(os.path.realpath(__file__))
# datastream_file = os.path.join(dir_path, "datastreams.json")
#
# with open(datastream_file) as ds_file:
#     DATASTREAM_MAPPING = json.load(ds_file)
# Unit here ******************************************************


def define_mqtt_statemachine():
    """
    Setting up MQTT client and define function on mqtt events.
    :return:
    """
    # The protocol must be specified in python!
    client = mqtt.Client(protocol=mqtt.MQTTv31)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(MQTT_BROKER, 1883, 60)
    logger.info("Connection to {} on port {} established at {} UTC".format(MQTT_BROKER, 1883,
                                                                           datetime.utcnow().isoformat()))
    pr_client.send("logging", "Connection to {} on port {} established".format(MQTT_BROKER, 1883))

    client.loop_forever()


def on_connect(client, userdata, flags, rc):
    """Report if connection to MQTT_BROKER is established
    and subscribe to all topics. MQTT subroutine"""
    logger.info("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for mqtt_topic in SUBSCRIBED_TOPICS:
        client.subscribe(mqtt_topic)


def on_disconnect(client, userdata, rc):
    """Reporting if connection to MQTT_BROKER is lost. MQTT subroutine"""
    logger.warning("Disconnect, reason: " + str(rc), level="warning")
    logger.warning("Disconnect, reason: " + str(client), level="warning")
    pr_client.send("logging", "Disconnect, reason: " + str(client))
    pr_client.send("logging", "Disconnect, reason: " + str(rc))


def on_message(client, userdata, msg):
    """
    Action on received message:
    Raw message will be parsed to the canonical data format specified with SensorThings
    and published on the Kafka message bus via the kafka producer.
    Nothing to return, because kafka message sending is called here.
    :param client: not used, but part of routine.
    :param userdata: not used, but part of routine.
    :param msg: Incoming raw MQTT message
    :return:
    """
    print("Received new data with topic: {} and values: {}".format(msg.topic, msg.payload))

    # kafka_logger("New MQTT message: {}, {}".format(msg.topic, "-"), level="debug")  # msg.payload))
    if msg.topic not in MQTT_TOPICS:
        MQTT_TOPICS.append(msg.topic)
        with open(topics_list_file, "w") as topics:
            json.dump({"topics": sorted(MQTT_TOPICS)}, topics, indent=4, sort_keys=True)
            logger.info("Found new mqtt topic: {} and saved it to file".format(msg.topic))
            pr_client.send("logging", "Found new mqtt topic: {} and saved it to file".format(msg.topic))


    messages = list()
    if msg.topic.startswith("testtopic"):
        message = dict()
        message["Datastream"] = msg.topic.replace("/", ".")
        message["result"] = float(msg.payload)
        message["phenomenonTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
        message["resultTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
        messages.append(message)

    elif msg.topic.startswith("octoprint/temperature"):
        # messages = parse_octoprint_temperature(msg)
        pass
    elif msg.topic.startswith("prusa3d/temperature"):
        messages = parse_prusa3d_temperature(msg)
    elif msg.topic.startswith("prusa3d/progress"):
        messages = parse_prusa3d_progress(msg)
    elif msg.topic.startswith("prusa3d/mqtt"):
        messages = parse_prusa3d_mqtt(msg)
    elif msg.topic.startswith("prusa3d/event"):
        messages = parse_prusa3d_event(msg)
    elif msg.topic.startswith("sensorpi/"):
        send_sensorpi_message(msg)
    else:
        logger.warning("Found unparsed message: {}: {}".format(msg.topic, msg.payload))


def send_sensorpi_message(msg):
    # That mapping must fit from mqtt topic name to gost_instances datastream name
    sensorpi_mapping = dict({
        "sensorpi/temperature": "temperature",
        "sensorpi/humidity": "humidity",
        "sensorpi/current0": "panda_current",
        "sensorpi/current1": "prusa_current",
        "sensorpi/current2": "pixtend_current",
        "sensorpi/current3": "sigmatek_current"
    })
    pr_client.send(quantity=sensorpi_mapping[msg.topic], result=msg.payload.decode())
    logger.debug("Sent SensorPi Data to Panta Rhei")


def parse_octoprint_temperature(msg):
    # octoprint and prusa3d equal because there could be a bug in the plugin, ignore octoprint messages
    payload = json.loads(msg.payload.decode("utf-8"))

    messages = list()
    for direction in ["target", "actual"]:
        if direction in payload.keys():
            message = dict()
            message["phenomenonTime"] = convert_timestamp(payload["_timestamp"])
            message["resultTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
            message["result"] = payload[direction]
            if msg.topic == "octoprint/temperature/bed":
                message["Datastream"] = "prusa3d.bed.temp.{}".format(direction)
            elif msg.topic == "octoprint/temperature/tool0":
                message["Datastream"] = "prusa3d.tool0.temp.{}".format(direction)
            else:
                logger.warning("Octoprint quantity not implemented.")
            messages.append(message)
        else:
            logger.warning("Octoprint payload direction not implemented.")

    return messages


def parse_prusa3d_temperature(msg):
    payload = json.loads(msg.payload.decode("utf-8"))

    messages = list()
    for direction in ["target", "actual"]:
        if direction in payload.keys():
            message = dict()
            message["phenomenonTime"] = convert_timestamp(payload["_timestamp"])
            message["resultTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
            message["result"] = payload[direction]
            if msg.topic == "prusa3d/temperature/bed":
                message["Datastream"] = "prusa3d.bed.temp.{}".format(direction)
            elif msg.topic == "prusa3d/temperature/tool0":
                message["Datastream"] = "prusa3d.tool0.temp.{}".format(direction)
            else:
                logger.warning("Octoprint quantity not implemented.")
            messages.append(message)
        else:
            logger.warning("Octoprint payload direction not implemented.")

    return messages


def parse_prusa3d_progress(msg):
    message = dict()
    payload = json.loads(msg.payload.decode("utf-8"))
    message["phenomenonTime"] = convert_timestamp(payload["_timestamp"])
    # del(payload["_timestamp"])
    message["resultTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
    message["result"] = None
    message["parameters"] = payload
    message["Datastream"] = "prusa3d.progress.status"
    return [message]


def parse_prusa3d_mqtt(msg):
    message = dict()
    payload = msg.payload.decode("utf-8")
    try:
        message["phenomenonTime"] = convert_timestamp(payload["_timestamp"])
    except TypeError:
        message["phenomenonTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
    message["resultTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
    message["result"] = None
    message["parameters"] = payload
    message["Datastream"] = "prusa3d.mqtt.status"
    return [message]


def parse_prusa3d_event(msg):
    # Skip ZChange information as they occur to frequently
    if msg.topic == "prusa3d/event/ZChange":
        return None
    payload = json.loads(msg.payload.decode("utf-8"))
    if payload.get("_event") in ["CaptureStart", "CaptureDone"]:
        return None
    message = dict()
    try:
        message["phenomenonTime"] = convert_timestamp(payload["_timestamp"])
        # del(payload["_timestamp"])
    except KeyError:
        message["phenomenonTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
    message["resultTime"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
    message["result"] = None
    message["parameters"] = payload
    message["Datastream"] = "prusa3d.event.status"
    return [message]


def mqtt_to_sensorthings(msg):
    """
    Parsing MQTT message from raw message object and transform into inte
    :param msg: MQTT message including topic and payload
    :return: datapoint dictionary including quantity (topic), timestamp and value
    """

    datapoint = dict()
    datapoint["quantity"] = msg.topic
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception as e:
        logger.warning("Couldn't parse message: {}, {}".format(msg, e))
        return

    if type(payload) in [type(0), type(0.0)]:
        datapoint["value"] = payload
        datapoint["ts"] = datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat()
        datapoints = list([datapoint])
    elif len(payload.keys()) != 2:
        # In this case there are multiple keys in one payload,
        # e.g. {'posE': 2233.81, 'posZ': 0.5, 'ts': 1516356558.740686, 'posX': 94.44, 'posY': 85.1}
        datapoints = fetch_multiple_data(payload)
        # return None
    else:
        try:
            datapoint["ts"] = payload["ts"]
            for key in list(payload.keys()):
                if key != "ts":
                    datapoint["value"] = payload[key]
            datapoints = list([datapoint])
        except:
            logger.warning("Could not parse: {}".format(payload))
            return None
    return datapoints


def fetch_multiple_data(payload):
    """
    Previously used for parsing kafka messages
    :param payload: old kafka message
    :return: datapoint dictionary
    """
    datapoints = list()
    data_of_interest = ["posX", "posY", "posZ", "posE", "targetNozzle", "targetBed", "tempNozzle", "tempBed"]

    ts_in = payload.get("ts", None)
    if ts_in is None:  # return if no timestamp is found in payload
        return None

    for key, value in payload.items():
        if key in data_of_interest:
            datapoint = dict()
            datapoint["value"] = value
            datapoint["quantity"] = "rasp02/{}".format(key)
            datapoint["ts"] = ts_in
            datapoints.append(datapoint)
    return datapoints


# def convert_datastream_id(message):
#     """
#     Translate message metric: the MQTT input topic into the kafka bus quantity name via the
#     metrics mapping json file.
#     :param message: dictionary including quantity, timestamp and value
#     :return: updated datapoint dictionary including timestamp, value and new quantity
#     :rtype: dictionary. None if datapoint is ignored.
#     """
#
#     if not isinstance(message["Datastream"], str):
#         logger.error("Bad instance: {}".format(message))
#         return None
#     if message["Datastream"] in DATASTREAM_MAPPING.keys():
#         iot_id = DATASTREAM_MAPPING[message["Datastream"]]["id"]
#         try:
#             uri = "http://{}/v1.0/Datastreams({})".format(SENSORTHINGS_HOST, iot_id)
#         except Exception:
#             kafka_logger(Exception, level="debug")
#             uri = ""
#         message["Datastream"] = {"@iot.id": iot_id,
#                                  "name": message["Datastream"],
#                                  "URI": uri}
#         return message
#     else:
#         kafka_logger("Datastream not listed: {}".format(message["Datastream"]), level="warning")
#         print(message)
#         return None
#
#
# def create_message(datapoint):
#     """
#     Convert any datapoint message into the canonical message format
#     from i-maintenance's first iteration.
#     :param datapoint: dictionary including quantity, timestamp and value
#     :return: canonical message format as 4-key dictionary
#     """
#     message = {
#         'phenomenonTime': datapoint["ts"],
#         'resultTime': datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
#         'result': datapoint["value"],
#         'Datastream': {'@iot.id': datapoint["quantity"]}}
#     return message
#
#
# def convert_timestamp(ts_in, form="ISO8601"):
#     """Parse any timestamp format into a specific one.
#     Keyword arguments:
#     :param ts_in: timestamp (string, int or float)
#     :param form: timestamp format (string) default: "ISO8601"
#     :return: a conventional timestamp of default type ISO8601 e.g. "2017-10-17T11:52:42.123456"
#     """
#     # Check if the input has already the correct format
#     if form == "ISO8601" and type(ts_in) is str and ts_in.count(":") == 3:
#         return ts_in
#     # extract the unix timestamp to seconds
#     if type(ts_in) in [int, float]:
#         ts_len = len(str(int(ts_in)))
#         if ts_len in [10, 9]:
#             ts_in = float(ts_in)
#         elif ts_len in [13, 12]:
#             ts_in = float(ts_in) / 1000
#         elif ts_len in [16, 15]:
#             ts_in = float(ts_in) / 1000 / 1000
#         else:
#             kafka_logger("Unexpected timestamp format: {} ({})".format(ts_in, type(ts_in)), level="warning")
#     if form == "ISO8601":
#         return datetime.utcfromtimestamp(ts_in).replace(tzinfo=pytz.UTC).isoformat()
#     elif form in ["UNIX", "Unix", "unix"]:
#         return ts_in
#     else:
#         kafka_logger("Invalid date format specified: {}".format(form), level="warning")


# # noinspection PyBroadException
# def publish_message(message):
#     """
#     Publish the canonical data format (Version: i-maintenance first iteration)
#     to the Kafka Bus.
#
#     Keyword argument:
#     :param message: dictionary with 4 keywords and optional "parameters"
#     :return: None
#     """
#     try:
#         producer.produce(KAFKA_TOPIC_metric, json.dumps(message).encode('utf-8'),
#                          key=str(message['Datastream']).encode('utf-8'))
#         producer.poll(0)  # using poll(0), as Eden Hill mentions it avoids BufferError: Local: Queue full
#         # producer.flush() poll should be faster here
#         # print("sent:", str(message), str(message['Datastream']['@iot.id']).encode('utf-8'))
#     except Exception as e:
#         kafka_logger("Exception while sending log: {} \non kafka topic: {}\n Error: {}"
#                      .format(message, KAFKA_TOPIC_metric, e), level="warning")
#
#
# def kafka_logger(payload, level="debug"):
#     """
#     Publish the canonical data format (Version: i-maintenance first iteration)
#     to the Kafka Bus.
#
#     Keyword argument:
#     :param payload: message content as json or string
#     :param level: log-level
#     :return: None
#     """
#     message = {"Datastream": "dtz.src.logging",
#                "phenomenonTime": datetime.utcnow().replace(tzinfo=pytz.UTC).isoformat(),
#                "result": payload,
#                "level": level,
#                "host": socket.gethostname()}
#
#     print("Level: {} \tMessage: {}".format(level, payload))
#     try:
#         producer.produce(KAFKA_TOPIC_logging, json.dumps(message).encode('utf-8'),
#                          key=str(message['Datastream']).encode('utf-8'))
#         producer.poll(0)  # using poll(0), as Eden Hill mentions it avoids BufferError: Local: Queue full
#         # producer.flush() poll should be faster here
#     except Exception as e:
#         print("Exception while sending metric: {} \non kafka topic: {}\n Error: {}"
#               .format(message, KAFKA_TOPIC_logging, e))


if __name__ == '__main__':
    logger = logging.getLogger("MQTT-Adapter_Logger")
    logger.setLevel(logging.INFO)

    logging.basicConfig()
    logger.info("Started MQTT Adapter")

    dir_path = os.path.dirname(os.path.realpath(__file__))
    topics_list_file = os.path.join(dir_path, "topics_list.json")
    with open(topics_list_file) as topics_file:
        MQTT_TOPICS = json.load(topics_file)["topics"]

    pr_client = PantaRheiClient("MQTT-Adapter")
    pr_client.register(instance_file="gost_instances.json")

    logger.info("Configured the Panta Rhei Client")
    define_mqtt_statemachine()