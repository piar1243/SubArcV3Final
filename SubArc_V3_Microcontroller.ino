 #include <Wire.h>
#include "Adafruit_MLX90393.h"
#define stepPin 6
#define dirPin 7
Adafruit_MLX90393 sensor = Adafruit_MLX90393();
#define MLX90393_CS 10
#include <Adafruit_TMP117.h>
#include <Adafruit_Sensor.h>

Adafruit_TMP117  tmp117;
double temper = 0;
int ill = 101;
String t_holder = "[24.5]";
String e_holder = "[0.1]";

float mag1 = 0;
float mag2 = 0;
int magnetStatus = 0; //value of the status register (MD, ML, MH)
 
int lowbyte; //raw angle 7:0
word highbyte; //raw angle 7:0 and 11:8
int rawAngle; //final raw angle 
float degAngle; //raw angle in degrees (360/4096 * [value between 0-4095])

float mag_comp_val_x = 0;
float mag_comp_val_y = 0;
float mag_comp_val_z = 0;

float field_x_ca_val = 0;
float field_y_ca_val = 0;
float field_z_ca_val = 0;

void setup(void)
{
  pinMode(stepPin,OUTPUT); 
  pinMode(dirPin,OUTPUT);
  Serial.begin(115200);

  Wire.begin();
  Wire.setClock(800000L);


  TCA9548A(6); 
  
  while (!Serial) delay(10);     // will pause Zero, Leonardo, etc until serial console opens


  // Try to initialize!
  if (!tmp117.begin()) {
    Serial.println("Failed to find TMP117 chip");
    while (1) { delay(10); }
  }
  Serial.println("TMP117");

  
  
  TCA9548A(1);
  Serial.println("active");

  while (!Serial)
    delay(10);

 // Serial.println("Adafruit SHT4x test");
  //if (! sht4.begin()) {
  //  Serial.println("Couldn't find SHT4x");
   // while (1) delay(1);
 // }
  //sht4.setPrecision(SHT4X_HIGH_PRECISION);
  
 // sht4.setHeater(SHT4X_NO_HEATER);
  

  /* Wait for serial on USB platforms. */
  while (!Serial) {
      delay(10);
  }


   
  if (! sensor.begin_I2C(0x0c)) {          // hardware I2C mode, can pass in address & alt Wire
  //if (! sensor.begin_SPI(MLX90393_CS)) {  // hardware SPI mode
    Serial.println("No sensor found ... check your wiring?");
    while (1) { delay(10); }
  }
  Serial.println("MLX90393");
for (int i = 0; i < 6; i++){
  
  TCA9548A(i);
  
  sensor.setGain(MLX90393_GAIN_5X);
  // You can check the gain too
  Serial.print("Gain: ");
  switch (sensor.getGain()) {
    case MLX90393_GAIN_1X: Serial.println("1 x"); break;
    case MLX90393_GAIN_1_33X: Serial.println("1.33 x"); break;
    case MLX90393_GAIN_1_67X: Serial.println("1.67 x"); break;
    case MLX90393_GAIN_2X: Serial.println("2 x"); break;
    case MLX90393_GAIN_2_5X: Serial.println("2.5 x"); break;
    case MLX90393_GAIN_3X: Serial.println("3 x"); break;
    case MLX90393_GAIN_4X: Serial.println("4 x"); break;
    case MLX90393_GAIN_5X: Serial.println("5 x"); break;
  }

  // Set resolution, per axis. Aim for sensitivity of ~0.3 for all axes.
  sensor.setResolution(MLX90393_X, MLX90393_RES_17);
  sensor.setResolution(MLX90393_Y, MLX90393_RES_17);
  sensor.setResolution(MLX90393_Z, MLX90393_RES_16);

  // Set oversampling
  sensor.setOversampling(MLX90393_OSR_1);

  // Set digital filtering
  sensor.setFilter(MLX90393_FILTER_5);

}



  
}

void loop(void) {

  if (Serial.available() > 0) {
    // Read the incoming byte
    char incomingByte = Serial.read();

  

  TCA9548A(6);
  sensors_event_t temp; // create an empty event to be filled
  tmp117.getEvent(&temp); //fill the empty event object with the current measurements
  

   checkMagnetPresence();
   ReadRawAngle();
   mag1 = degAngle;
   
   TCA9548A(5);
   float x, y, z;
   
   if (sensor.readData(&x, &y, &z)) {
  } else {
      Serial.println("Unable to read XYZ data from the sensor.");
  }
  sensors_event_t event;
  sensor.getEvent(&event);
  mag_comp_val_x = event.magnetic.x;
  mag_comp_val_y = event.magnetic.y;
  mag_comp_val_z = event.magnetic.z;
   
  
  for (int i = 0; i < 5; i++){
    TCA9548A(i);
    float x, y, z;

    
    

  if (sensor.readData(&x, &y, &z)) {
  } else {
      Serial.println("Unable to read XYZ data from the sensor.");
  }

  sensors_event_t event;
  sensor.getEvent(&event);
  Serial.print(String(i) + ", ");
  //Serial.print("X: "); 
 // Serial.print("["); 
  Serial.print(trun(int(event.magnetic.x - mag_comp_val_x + field_x_ca_val)));
  Serial.print(", "); 
  Serial.print(int(trun(event.magnetic.y - mag_comp_val_y + field_y_ca_val)));
  Serial.print(", "); 
  Serial.print(int(trun(event.magnetic.z - mag_comp_val_z + field_z_ca_val)));
  Serial.print(", "); 

 // Serial.print("]");
  if (i < 4){
//  Serial.print(", "); 
  }
  //Serial.println(temper);

    
  }
   
  // Serial.print("]");
 //  Serial.print("]");
 //  Serial.println("]");
   //Serial.println();
  Serial.print(degAngle);
  Serial.print(", "); 
  Serial.println(temp.temperature);

if (incomingByte == 'b'){

   digitalWrite(dirPin, LOW);
   digitalWrite(stepPin,HIGH); 
   delayMicroseconds(20000);    // by changing this time delay between the steps we can change the rotation speed
   digitalWrite(stepPin,LOW); 
   delayMicroseconds(20000);

  
}

if (incomingByte == 'c'){

   digitalWrite(dirPin, HIGH);
   digitalWrite(dirPin, HIGH);
   digitalWrite(stepPin,HIGH);    
   delayMicroseconds(20000);    // by changing this time delay between the steps we can change the rotation speed
   digitalWrite(stepPin,LOW); 
   delayMicroseconds(20000);

  
}
}
}

void TCA9548A(uint8_t bus)
{
  Wire.beginTransmission(0x70);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus*
  Wire.endTransmission();
}

int trun(int number) {
    return (number / 10);
}


void ReadRawAngle()
{ 
  //Serial.println("active33");
  //7:0 - bits
  Wire.beginTransmission(0x36); //connect to the sensor
  Wire.write(0x0D); //figure 21 - register map: Raw angle (7:0)
  Wire.endTransmission(); //end transmission
  Wire.requestFrom(0x36, 1); //request from the sensor
  
  while(Wire.available() == 0); //wait until it becomes available 
  lowbyte = Wire.read(); //Reading the data after the request
 
  //11:8 - 4 bits
  Wire.beginTransmission(0x36);
  Wire.write(0x0C); //figure 21 - register map: Raw angle (11:8)
  Wire.endTransmission();
  Wire.requestFrom(0x36, 1);
  while(Wire.available() == 0);  
  highbyte = Wire.read();
  highbyte = highbyte << 8; //shifting to left
  rawAngle = highbyte | lowbyte; //int is 16 bits (as well as the word)
  degAngle = rawAngle * 0.087890625; 
}

void checkMagnetPresence(){
  while((magnetStatus & 32) != 32) //while the magnet is not adjusted to the proper distance - 32: MD = 1
  {
    //Serial.println("active22");
    magnetStatus = 0; //reset reading
    Wire.beginTransmission(0x36); //connect to the sensor
    Wire.write(0x0B); //figure 21 - register map: Status: MD ML MH
    Wire.endTransmission(); //end transmission
    Wire.requestFrom(0x36, 1); //request from the sensor
    while(Wire.available() == 0); //wait until it becomes available 
    magnetStatus = Wire.read(); //Reading the data after the request
    Serial.println(magnetStatus, BIN); //print it in binary so you can compare it to the table (fig 21)      
  }      
  //Serial.println("Magnet found!");
}
