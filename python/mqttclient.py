import sys
import time
import logging
import paho.mqtt.client


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(filename)s: %(levelname)s: %(message)s')

MQTT_HOST = 'localhost'

MQTT_PORT = 1883

CLIENT_ID = 'a'  

USER_NAME = 'a'

PASSWORD = 'a'

PUBLISH_TOPIC = '/user/pub'

SUBSCRIBE_TOPIC = 'user/sub2'

BIND_ADDRESS = ''

MQTT_RECONNECT_TRIES = 60
class MQTT():
    def __init__(self,host,clientID,username=None,password=None,port=1883,timeOut=60):
        self.Host = host
        self.Port = port
        self.timeOut = timeOut
        self.username =username
        self.password = password
        self.clientID = clientID

        self.mqttc = paho.mqtt.client.Client(self.clientID)                  
        if self.username is not None:                                   
            self.mqttc.username_pw_set(self.username, self.password)    

        self.mqttc.connect(self.Host, self.Port, self.timeOut)          

    def begin(self,message,connect):
        self.mqttc.on_connect = connect
        self.mqttc.on_message = message
        self.mqttc.loop_start()  

    def publish(self,tag,date,_Qos = 0):
        self.mqttc.publish(tag,date,_Qos)

    def subscribe(self,_tag):
        self.mqttc.subscribe(_tag)   

def on_message(client, userdata, msg):
  
    logging.info(msg.topic + ":" + str(msg.payload.decode("utf-8")))

def on_connect(client, userdata, flags, rc):
    
    logging.info("Connected with result code "+str(rc))

def main():# solo para pruebas
    mqtt = MQTT(MQTT_HOST,CLIENT_ID,USER_NAME,PASSWORD)
    mqtt.subscribe(SUBSCRIBE_TOPIC) 
    mqtt.begin(on_message,on_connect)

    while True:
        time.sleep(2)
        mqtt.publish(PUBLISH_TOPIC,"{\"msg\":\"hello,world!\"}")

if __name__ == '__main__':
    main()