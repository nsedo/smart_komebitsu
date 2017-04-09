from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import getopt
import json

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Read in command-line parameters
useWebsocket = False
host = "a2cpknzhnqtdtu.iot.us-west-2.amazonaws.com"
rootCAPath = "rootCA.pem"
certificatePath = "RaspberryPi3.cert.pem"
privateKeyPath = "RaspberryPi3.private.key"
myAWSIoTMQTTClient = None
def init_mqtt():
    print "init mqtt"
    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # Init AWSIoTMQTTClient
    if useWebsocket:
        myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
        myAWSIoTMQTTClient.configureEndpoint(host, 443)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath)
    else:
        myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
        myAWSIoTMQTTClient.configureEndpoint(host, 8883)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    return myAWSIoTMQTTClient

def connect_aws(myAWSIoTMQTTClient):
    print "connect aws"
    # Connect and subscribe to AWS IoT
    myAWSIoTMQTTClient.connect()
    myAWSIoTMQTTClient.subscribe("sdk/test2/Python", 1, customCallback)
    time.sleep(2)

    return myAWSIoTMQTTClient

def sendmsg(myAWSIoTMQTTClient):
    print "send message"
    # Publish to the same topic in a loop forever
    json_data = {'message' : "Buy kome"}
    myAWSIoTMQTTClient.publish("sdk/test2/Python", json.dumps(json_data), 1)
