 #include <Wire.h>
#include "Adafruit_MLX90393.h"
#define stepPin 6 //defined arduino pins for rotating calibration stand stepper motor
#define dirPin 7
Adafruit_MLX90393 sensor = Adafruit_MLX90393();//uses adafruit MLX90393 sensor library to pull magnetic field readings from each sensor
#define MLX90393_CS 10 //cs pin on arduino
#include <Adafruit_TMP117.h> //uses the adafruit TMP117 sensor library and the adafruit sensor library
#include <Adafruit_Sensor.h>

Adafruit_TMP117  tmp117; //defines the tmp117 temperature sensor
double temper = 0;
int ill = 101;
String t_holder = "[24.5]"; //temperatures
String e_holder = "[0.1]";

float mag1 = 0;
float mag2 = 0;
int magnetStatus = 0; //magnet status of AS5600
 
int lowbyte; //AS5600 angle bits 7:0
word highbyte; //AS5600 angle bits 7:0 11:8
int rawAngle; //AS5600 angle out of 4096 (12 bits)
float degAngle; //AS5600 12 bit angle output out of 360

float mag_comp_val_x = 0;
float mag_comp_val_y = 0;
float mag_comp_val_z = 0;

float field_x_ca_val = 0;
float field_y_ca_val = 0;
float field_z_ca_val = 0;

void setup(void)
{
  pinMode(stepPin,OUTPUT); //activate pins
  pinMode(dirPin,OUTPUT);
  Serial.begin(115200); //begin serial

  Wire.begin(); //begin wire
  Wire.setClock(800000L); //set the clock cycle to the fastest possible cycle time


  TCA9548A(6); //switch to warmup
  
  while (!Serial) delay(10);  //will pause to wait for the Serial console to open

  if (!tmp117.begin()) { //initializes the TMP117 temperature sensor
    Serial.println("TMP117 disconnect");
    while (1) { delay(10); }
  }
  Serial.println("TMP117"); //printing to show that the sensor was intitialized

  
  
  TCA9548A(1); //switch to hall sensor 1
  Serial.println("active");

  while (!Serial) //wait for serial again to ensure no bugs
    delay(10);

   
  if (! sensor.begin_I2C(0x0c)) { //communicates to the standard MLX90393 (will change depending on which MLX90393 version you get)
    Serial.println("MLX90393 disconnect");
    while (1) { delay(10); }
  }
  Serial.println("MLX90393"); //indicates the MLX90393 has been activated and found
for (int i = 0; i < 6; i++){ //loops through all the different MLX90393 and defines their gain to the max, sets to max resolution, and most time effective and accurate sampling rate
  
  TCA9548A(i); //sets the multiplexer to the specific MLX90393 sensor
  
  sensor.setGain(MLX90393_GAIN_5X); //sets the MLX90393 gain to the max for best resolution
  // You can check the gain too
  Serial.print("Gain: ");
  switch (sensor.getGain()) { //defines the different gains available (pulled from the Adafruit libraries)
    case MLX90393_GAIN_1X: Serial.println("1 x"); break;
    case MLX90393_GAIN_1_33X: Serial.println("1.33 x"); break;
    case MLX90393_GAIN_1_67X: Serial.println("1.67 x"); break;
    case MLX90393_GAIN_2X: Serial.println("2 x"); break;
    case MLX90393_GAIN_2_5X: Serial.println("2.5 x"); break;
    case MLX90393_GAIN_3X: Serial.println("3 x"); break;
    case MLX90393_GAIN_4X: Serial.println("4 x"); break;
    case MLX90393_GAIN_5X: Serial.println("5 x"); break;
  }
.
  sensor.setResolution(MLX90393_X, MLX90393_RES_17); //sets the sensor resolution for each axis, goes to the max
  sensor.setResolution(MLX90393_Y, MLX90393_RES_17);
  sensor.setResolution(MLX90393_Z, MLX90393_RES_16);

  sensor.setOversampling(MLX90393_OSR_1); //sets oversampling rate to 1 so SubArc sampling time remains high

  sensor.setFilter(MLX90393_FILTER_5); //get the highest digital filter setting from MLX90393 for high accuracy at high resolution

}

}

void loop(void) {

  if (Serial.available() > 0) { //reads incoming byte from the python script
    char incomingByte = Serial.read();

  

  TCA9548A(6); //switches to the temperature sensor
  sensors_event_t temp; // create an empty event to be filled (from adafruit library)
  tmp117.getEvent(&temp); //fill the empty event object with the current measurements
  
  checkMagnetPresence(); //checks if the AS5600 is there, sends error if not
  ReadRawAngle(); //reads subdividing AS5600 position
  mag1 = degAngle; //sets the mag1 reading to the AS5600 position
   
  TCA9548A(5); // moves to the 5th MLX90393 (the Bexternal sensor)
  float x, y, z; //defines axis magnetic fields
   
  if (sensor.readData(&x, &y, &z)) {} //checks if sensor read data (from adafruit library)
  else {
    Serial.println("Unable to read XYZ data from the sensor.");
  }
  sensors_event_t event;
  sensor.getEvent(&event);
  mag_comp_val_x = event.magnetic.x; //sets the magnetic values to variables to subtract from regular MLX90393 readings
  mag_comp_val_y = event.magnetic.y;
  mag_comp_val_z = event.magnetic.z;
   
  
  for (int i = 0; i < 5; i++){ //loops through the MLX90393 array
    TCA9548A(i);
    float x, y, z; //defines the axis magnetic fields

    if (sensor.readData(&x, &y, &z)) {} //checks if sensor read data (from adafruit library)
    else {
        Serial.println("Unable to read XYZ data from the sensor.");
    }

    sensors_event_t event; // create an empty event to be filled (from adafruit library)
    sensor.getEvent(&event); //fill the empty event object with the current measurements
    Serial.print(String(i) + ", "); //print which hall sensor in the array your on in serial
    //Serial.print("X: "); 
  // Serial.print("["); 
  //all these values are picked up by python script when activited in the Serial communication protocol
    Serial.print(trun(int(event.magnetic.x - mag_comp_val_x + field_x_ca_val))); //prints the true X axis magnetic field for that hall sensor in the array
    Serial.print(", "); 
    Serial.print(int(trun(event.magnetic.y - mag_comp_val_y + field_y_ca_val))); //prints the true Y axis magnetic field for that hall sensor in the array
    Serial.print(", "); 
    Serial.print(int(trun(event.magnetic.z - mag_comp_val_z + field_z_ca_val))); //prints the true Z axis magnetic field for that hall sensor in the array
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
  Serial.print(degAngle); // prints the AS5600 angle
  Serial.print(", "); //adds the , because the data needs to be formatted correctly for the python script
  Serial.println(temp.temperature); //finally adds the temperature add the end of the string

if (incomingByte == 'b'){ //backwards stepper increment is B sending from the python script

   digitalWrite(dirPin, LOW);
   digitalWrite(stepPin,HIGH); 
   delayMicroseconds(20000);
   digitalWrite(stepPin,LOW); 
   delayMicroseconds(20000);

  
}

if (incomingByte == 'c'){ //forwards stepper increment is C sending from the python script

   digitalWrite(dirPin, HIGH);
   digitalWrite(dirPin, HIGH);
   digitalWrite(stepPin,HIGH);    
   delayMicroseconds(20000);
   digitalWrite(stepPin,LOW); 
   delayMicroseconds(20000);

  
}
}
}

void TCA9548A(uint8_t bus) //function to switch the sensors with the same I2C going to the multiplexer, function from adafruit
{
  Wire.beginTransmission(0x70); //TCA9548A address is 0x70
  Wire.write(1 << bus); //sending byte selects the number bus
  Wire.endTransmission();
}

int trun(int number) { //truncate function
    return (number / 10);
}


void ReadRawAngle() //reads the raw angle from the AS5600 (library function from curious scientist as5600 tutorial)
{ 

  Wire.beginTransmission(0x36); //connect to the sensor
  Wire.write(0x0D); //figure 21 - register map: Raw angle (7:0)
  Wire.endTransmission(); //end transmission
  Wire.requestFrom(0x36, 1); //request from the sensor
  
  while(Wire.available() == 0); //wait until it becomes available 
  lowbyte = Wire.read(); //Reading the data after the request
 
  Wire.beginTransmission(0x36);
  Wire.write(0x0C);
  Wire.endTransmission();
  Wire.requestFrom(0x36, 1);
  while(Wire.available() == 0);  
  highbyte = Wire.read();
  highbyte = highbyte << 8; //shifting to left
  rawAngle = highbyte | lowbyte; //int is 16 bits (as well as the word)
  degAngle = rawAngle * 0.087890625; 
}

void checkMagnetPresence(){ //checks the magnetic presence of the AS5600 (library function from curious scientist as5600 tutorial)
  while((magnetStatus & 32) != 32) //while the magnet is not adjusted to the proper distance - 32: MD = 1
  {
    magnetStatus = 0; //reset reading
    Wire.beginTransmission(0x36); //connect to the sensor
    Wire.write(0x0B); //figure 21 - register map: Status: MD ML MH
    Wire.endTransmission(); //end transmission
    Wire.requestFrom(0x36, 1); //request from the sensor
    while(Wire.available() == 0); //wait until it becomes available 
    magnetStatus = Wire.read(); //Reading the data after the request
    Serial.println(magnetStatus, BIN);
  }      
}