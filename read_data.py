import os
import RPi.GPIO as GPIO
import dht11
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
from datetime import date, datetime

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()


# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("client1")
myMQTTClient.configureEndpoint(os.environ['AWS_IOT_ENDPOINT'], 8883)
myMQTTClient.configureCredentials("/home/pi/awsIoTConf/RootCA.pem", "/home/pi/awsIoTConf/privatekey.pem", "/home/pi/awsIoTConf/cert.pem")
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)
serial_no = "12345abcd"

#connect and publish
myMQTTClient.connect()
myMQTTClient.publish(serial_no + "/aapghdiiot", "connected", 0)

#loop and publish sensor reading
while 1:
    now = datetime.utcnow()
    now_str = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    instance = dht11.DHT11(pin = 4) 
    result = instance.read()

    if result.is_valid():

        payload = '{ "temperature": ' + str(result.temperature) + ',"humidity": '+ str(result.humidity) + ',"createdAt": "' + now_str + '" }'
        print payload
        myMQTTClient.publish(serial_no + "/aapghdiiot", payload, 0)
        sleep(4)
    else:
        print (".")
        sleep(1)
