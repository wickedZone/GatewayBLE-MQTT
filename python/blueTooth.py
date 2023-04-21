import sys
import logging
import time
from bluepy.btle import Scanner, DefaultDelegate,UUID, Peripheral
from binascii import hexlify
from multiprocessing import Process, Event
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(filename)s: %(levelname)s: %(message)s')

BLUE_NAME = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
SERVER_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
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
            devices = scanner.scan(5.0,passive=True)
            #BLEScanner().start()
        except Exception as e:
            #time.sleep(10)
            
            devices = scanner.scan(5.0,passive=False)
        names=[]
        for dev in devices:
            logging.info("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            for (adtype, desc, value) in dev.getScanData():
               
                if value in buleName and dev.addr not in [d.addr for d in scanned_dev]:
                    names.append(value)
                    devices_list.append(Peripheral(dev))
                logging.info("  %s = %s" % (desc, value))
        logging.info('device:{}'.format(devices_list))

        return devices_list,names

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


def main():
    devices = bluetooth.scannerDevices(BLUE_NAME,ScanDelegate)
    server = bluetooth.getServices(devices,SERVER_UUID)
    characteristic = bluetooth.getCharacteristics(server)


    devices.withDelegate(NotifyDelegate(devices))

    for descriptor in devices.getDescriptors(characteristic,server.hndEnd):
        if (descriptor.uuid==0x2902):
            print(f'Client Characteristic Configuration found at handle 0x{format(descriptor.handle,"02X")}')
            hEcgCCC=descriptor.handle

    devices.writeCharacteristic(hEcgCCC,bytes([1, 0]))

    # tmp_data = devices.readCharacteristic(0x11)
    # print(tmp_data)
 
    while True:
        if devices.waitForNotifications(1.0):
            continue
        print("Waiting... Waited more than one sec for notification")
        # devices.disconnect()


if __name__ == '__main__':
    logging.info("bluetooth.py running")
    main()