import sys
import time
import logging
import paho.mqtt.client


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(filename)s: %(levelname)s: %(message)s')



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
