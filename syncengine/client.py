import paho.mqtt.client as mqtt
import pickle
from uuid import uuid4
import config

class Client:
    def __init__(self):
        self.mqttc = mqtt.Client()
        self.mqttc.on_message = self.handle_message
        self.mqttc.on_connect = self.handle_connect
        self.mqttc.on_disconnect = self.on_disconnect
        self.id = str(uuid4())
        self.callbacks = {}

        self.on_connect = None
        self.on_message = None

    def handle_message(self, client, userdata, msg):
        topic = msg.topic
        content = pickle.loads(msg.payload)
        #  print("MSG", topic, content)
        if self.on_message:
            self.on_message(self, topic, content)

        # Inform callbacks
        for topicPrefix in self.callbacks:
            if topic.startswith(topicPrefix):
                self.callbacks[topicPrefix](self, topic, content)

    def handle_connect(self, client, userdata, flags, rc):
        print("CONNECTED")
        if self.on_connect:
            self.on_connect(self)

    def on_disconnect(self, client, userdata, rc):
        print("DISCONNECTED")

    def subscribe(self, topic, appendId=False):
        if appendId:
            topic += self.id
        else:
            topic += "#"
        self.mqttc.subscribe(topic)

    def send_message(self, content, topic, appendId=False, idToAppend=None):
        if appendId:
            if idToAppend:
                topic += idToAppend
            else:
                topic += self.id
        self.mqttc.publish(topic, pickle.dumps(content))

    def register_callback(self, topicPrefix, callback):
        self.callbacks[topicPrefix] = callback

    def guess_interlocutor_id(self, topic):
        return topic.split("/")[-1]

    def connect(self):
        self.mqttc.connect(config.mqttBrokerHost, config.mqttBrokerPort)
