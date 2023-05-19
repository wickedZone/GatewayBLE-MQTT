import os
import sys
import time
import logging
import mqttclient
import blueTooth
import struct
import json
import threading
from yaml import full_load
from bluepy.btle import Scanner, DefaultDelegate,UUID, Peripheral

# time.sleep(30)  


identificadoresBLE= ['6e400001-b5a3-f393-e0a9-e50e24dcca9e']

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(filename)s: %(levelname)s: %(message)s')


mqtt =mqttclient.MQTT('localhost', '', '', '') #parametros del broker mqtt
class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            logging.info("Discovered bluetooth device:{}".format(dev.addr))
        elif isNewData:
            logging.info("Received new data from:{}".format(dev.addr))
class NotifyDelegate(DefaultDelegate):
    def __init__(self, params):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        updateMsn = {}
  
  
       
        format = "<hhhhhhh"
        float_values = struct.unpack(format, data)
        data = {}
        arrayy={}
        data['id']=float_values[0]
      
        arrayy['x']=float_values[1]
        arrayy['y']=float_values[2]
        arrayy['z']=float_values[3]
        data['gyroscope'] = arrayy
        arrayy1={}
        arrayy1['x']=float_values[4]
        arrayy1['y']=float_values[5]
        arrayy1['z']=float_values[6]
        data['accelerometer'] = arrayy1
        
        json_data = json.dumps(data)

        
        if json_data:        
            
            mqtt.publish("sensorData", json_data, 1)  
        else:
            pass


    


 
 

def on_connect(client, userdata, flags, rc):
   
    print("Connected with result code "+str(rc))

def on_message(lient, userdata, msg):
    
    print(msg.topic + ":" + str(msg.payload.decode("utf-8")))


    

def connect_and_subscribe(dev):
    try:
        server = blueTooth.bluetooth.getServices(dev, identificadoresBLE[0])
        characteristic = blueTooth.bluetooth.getCharacteristics(server)
        dev.withDelegate(NotifyDelegate(dev))
        
        for descriptor in dev.getDescriptors(characteristic, server.hndEnd):
            if (descriptor.uuid==0x2902):
                print(f'Client Characteristic Configuration found at handle 0x{format(descriptor.handle,"02X")}')
                hEcgCCC=descriptor.handle

        dev.writeCharacteristic(hEcgCCC,bytes([1, 0]))
        
    except Exception as e:
        print(f"Error connecting and subscribing to device {dev.addr}: {str(e)}")
        dev.disconnect()

def worker(dev):
    
    devicesRconn =[]
    namesRconn=[]
    connect_and_subscribe(dev)
    while True:
        try:
            if dev.waitForNotifications(1.0):
                continue
            
        except Exception as e:
            print(f"Error in worker thread for device {dev.addr}: {str(e)}")
            dev.disconnect()
            time.sleep(10)
            try:
                dev.connect(dev.addr)
                if len(dev.getServices()) > 0:
                    print("Connected to BLE device")
                    connect_and_subscribe(dev)
                else:
                    print("Failed to reconnect to BLE device")
                    break
            except Exception as b:
                print("Failed to reconnect to BLE device")
                break

            
def main():
    scanned_devices = set()
    #dispositivos= set() # para guardar las mac de los dispositivos
    mqtt.subscribe('/user/sub2') 
    mqtt.begin(on_message,on_connect)
    logging.info("Connected to broker. Starting CLI...")
    threads = []

    while True:
        devices= blueTooth.bluetooth.scannerDevices(identificadoresBLE, ScanDelegate,scanned_devices)
        logging.info("HAY {} DISPOSITIVOS".format(len(devices)))

        
        for i, dev in enumerate(devices):
            if dev.addr not in scanned_devices:
                t = threading.Thread(target=worker, args=(dev,))
                t.name=(dev.addr)
                #t.daemon=True
                t.start()
                threads.append(t)
                scanned_devices.add(dev.addr)
                #dispositivos.add(dev.addr)
        logging.info("Reescanning......")
        mqtt.publish("Scanned", str(scanned_devices), 2)
        if len(scanned_devices)!=0:
            time.sleep(350)
        
        for t in threads:
            if not t.is_alive():
                for devv in scanned_devices:
                    if devv == t.name:
                        scanned_devices.remove(devv)
                        break
                threads.remove(t)
        
       
           
        mqtt.publish("Scanned", str(scanned_devices), 2) 

    for t in threads:
        t.join()


if __name__ == '__main__':
    logging.info("MQTT2BLUETOOTH.py running")
    main()