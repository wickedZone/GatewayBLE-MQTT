   #include "Nicla_System.h"
  #include "Arduino_BHY2.h"
  #include <ArduinoBLE.h>

  #define BLE_SENSE_UUID(val) ("19b10000" val "-537e-4f6c-d104768a1214")

  const int VERSION = 0x00000001;

  BLEService service("6e400001-b5a3-f393-e0a9-e50e24dcca9e");



  BLECharacteristic gyroyaccel(BLE_SENSE_UUID("6001"), BLERead | BLENotify, 7 * sizeof(int16_t));   

  

  // String to calculate the local and device name
  String name;
  uint16_t identificador;
  SensorXYZ accelerometer(SENSOR_ID_ACC);
  SensorXYZ gyroscope(SENSOR_ID_GYRO);


  void setup(){
    Serial.begin(115200);

    Serial.println("Start");


    //Sensors initialization
    BHY2.begin();

    accelerometer.begin();
    gyroscope.begin();
    if (!BLE.begin()){
      Serial.println("Failed to initialized Bluetooth® Low Energy!");

      while (1)
        ;
    }


    

    BLE.setLocalName("NICLA2");
    BLE.setDeviceName("NICLA2");
    BLE.setAdvertisedService(service);

    // Add all the previously defined Characteristics

   
    service.addCharacteristic(gyroyaccel);

    
    BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);

    


    


    BLE.addService(service);
    BLE.advertise();
    identificador=extractNumberFromMAC(BLE.address());
  }
  
uint16_t extractNumberFromMAC(String mac) {
  uint16_t result = 0;
  int count = 0;
  for (int i = mac.length() - 1; i >= 0; i--) {
    if (isDigit(mac[i])) {
      result += (mac[i] - '0') * pow(10, count);
      count++;
      if (count == 4) {
        break;
      }
    }
  }
  return result;
}

  void loop(){
   
    while (BLE.connected()){
      BHY2.update();


      int16_t x, y, z;

      x = gyroscope.x();
      y = gyroscope.y();
      z = gyroscope.z();
    
      int16_t xx, yy, zz;
      xx = accelerometer.x();
      yy = accelerometer.y();
      zz = accelerometer.z();

      int16_t id=identificador;
      int16_t accelerometerValues[] = {id,x, y, z,xx,yy,zz};
      gyroyaccel.writeValue(accelerometerValues, sizeof(accelerometerValues));
      delay(25);
  
   
    }
      
    
       
  }

  

void blePeripheralDisconnectHandler(BLEDevice central){
  nicla::leds.setColor(red);
  while (!BLE.connected()) {
    // Attempt to reconnect to the central device
    BLE.advertise();
    BLEDevice central = BLE.central();
    if (central) {
      Serial.println("Connected to central device");
      nicla::leds.setColor(green);
    } else {
      Serial.println("Failed to connect to central device");
      nicla::leds.setColor(red);
    }
  }
}

 