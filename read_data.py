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
myMQTTClient = AWSIoTMQTTClient("client123")
myMQTTClient.configureEndpoint(os.environ['AWS_IOT_ENDPOINT'], 8883)
myMQTTClient.configureCredentials("./awsIoTConf/RootCA.pem", "./awsIoTConf/privatekey.pem", "./awsIoTConf/cert.pem")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
serial_no = os.environ['DEVICE_SERIAL_NO']

#connect and publish
myMQTTClient.connect()
myMQTTClient.publish(serial_no + "/temphumid", "connected", 0)

#loop and publish sensor reading
while 1:
    now = datetime.utcnow()
    now_str = now.strftime('%Y-%m-%dT%H:%M:%SZ') #e.g. 2016-04-18T06:12:25.877Z
    instance = dht11.DHT11(pin = 4) #BCM GPIO04
    result = instance.read()

    if result.is_valid():

        payload = '{ "temperature": ' + str(result.temperature) + ',"humidity": '+ str(result.humidity) + ',"createdAt": "' + now_str + '" }'
        print payload
        myMQTTClient.publish(serial_no + "/temphumid", payload, 0)
        sleep(4)
    else:
        print (".")
        sleep(1)

Provisioning a certificate:

aws iot create-keys-and-certificate --set-as-active
The output of the command contains the certificate, the public key, and the private key.

aws iot describe-certificate --certificate-id id --output text --query certific ateDescription.certificatePem > cert.pem

--certificate-id specifies the part in the certificate ARN after the last slash (/): arn:aws:iot:us-east-1:123456789012:cert/id-is-found-here.
