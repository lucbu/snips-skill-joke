#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import requests
import json
import random

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

jokes = json.loads(requests.get("https://bridge.buddyweb.fr/api/blagues/blagues").content)

class Joke(object):
    """Class used to wrap action code with mqtt connection
        
        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        # start listening to MQTT
        self.start_blocking()
        
    # --> Sub callback function, one per intent
    def intent_joke_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, jokes[random.randint(0, len(jokes) - 1)]['blagues'], "")

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        intent_name = intent_message.intent.intent_name

        if ':' in intent_name:
            intent_name = intent_name.split(":")[1]

        if intent_name == 'blague':
            self.intent_joke_callback(hermes, intent_message)

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    Joke()
