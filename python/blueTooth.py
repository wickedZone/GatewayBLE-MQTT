import sys
import logging
import time
from bluepy.btle import Scanner, DefaultDelegate,UUID, Peripheral
from binascii import hexlify
from multiprocessing import Process, Event
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(filename)s: %(levelname)s: %(message)s')


passiveMode=True
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
        print("Notification from Handle: 0x" + format(cHandle,'02X') )
        print(hexlify(data))
class bluetooth():
    
    def scannerDevices(buleName,scanner1,scanned_dev):
        devices_list = []
        try:
            scanner = Scanner().withDelegate(scanner1())
            if passiveMode == True:
                devices = scanner.scan(5.0,passive=True)
            else: 
                devices = scanner.scan(5.0,passive=False)
        except Exception as e:
            #si el primer escaneo pasivo no es compatible, se escanea en adelante de forma activa
            passiveMode=False
            devices = scanner.scan(5.0,passive=False)
        
        for dev in devices:
            logging.info("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            for (adtype, desc, value) in dev.getScanData():
               
                if value in buleName and dev.addr not in [d.addr for d in scanned_dev]:
                    
                    devices_list.append(Peripheral(dev))
                logging.info("  %s = %s" % (desc, value))
        logging.info('device:{}'.format(devices_list))

        return devices_list

    def getServices(devices,server_uuid):
        services = devices.getServices()
        service_uuid = UUID(server_uuid)
        service_specific = devices.getServiceByUUID(service_uuid)
        logging.info('List all server ...')
        for service in services:
            logging.info(service)
        return service_specific

    def getCharacteristics(service):
        logging.info('get specified service:%s'%(service))
        characteristics = service.getCharacteristics()
        characteristics_first = characteristics[0].getHandle()

        logging.info('List all characteristics ...')
        for char in characteristics:
            print(char)
        return characteristics_first


