import serial
import time
import math

AksIM2_Serial = serial.Serial('COM18', 9600, timeout=2)
SubArcV3_Serial = serial.Serial(port='COM4',baudrate=115200)

#ASCII Commands for AksIM-2 initialization & angle reading
#----------------------------------------------------------------------------------------------------------------------

ascii_1 = "v"  # (check for E201 presence)
ascii_2 = "r"  # (get interface serial number)
ascii_3 = "V5"  # (select 5 V power for the encoder)
ascii_4 = "n"  # (enable power output)
ascii_5 = "e"  # (verify current consumption)
ascii_6 = "Ce"  # (enable EncoLink Master library in the E201)
ascii_7 = "G0:1"  # (set SCK polarity and phase)
ascii_8 = "D015"  # (set CS communication delay)
ascii_9 = "M5"  # (set clock frequency)
ascii_10 = "m"  # (verify selected clock frequency)
ascii_11 = "j"  # (initialize EncoLink library and get basic encoder parameters)
AkSIM2_angle_read_ascii = "?04:000"  # (read 4 bytes of position from the encoder (suitable for single-turn encoder)

aksim2_initialization_list = ["v", "r", "V5", "n", "e", "Ce", "G0:1" "D015", "M5", "M5", "m", "j"]

#----------------------------------------------------------------------------------------------------------------------


def aksim2_initialization():

    for j, command in enumerate(aksim2_initialization_list):
        AksIM2_Serial.write(command.encode())
        response = AksIM2_Serial.read(AksIM2_Serial.in_waiting)
        print("response", response.decode())
        response = None
        time.sleep(0.1)


aksim2_initialization()


def aksim2_read_angle():

    AksIM2_Serial.flushInput()
    AksIM2_Serial.write(AkSIM2_angle_read_ascii.encode())
    AksIM2_Serial.flushOutput()
    time.sleep(0.01)
    response1 = AksIM2_Serial.read(AksIM2_Serial.in_waiting)
    #print(response1.decode()) #debugging

    binary_value = bin(int(response1, 16))[2:].zfill(32)  # pad to 32 bits

    first_20_bits = binary_value[:20]

    decimal_value = int(first_20_bits, 2)

    #print("Binary value:", binary_value) #debugging
    #print("First 20 bits:", first_20_bits) #debugging
    #print("Decimal value of first 20 bits:", decimal_value) #debugging
    angular_value = decimal_value/1048576 * 360
    time.sleep(0.01)
    return decimal_value


def read_average_angle():
    average_angle = 0
    for k in range(5):
        average_angle += aksim2_read_angle()
    print(average_angle/5)
    return average_angle/5


while True:

    f = open("DoubleRingTest1.txt", "a")
    SubArcV3_Serial.write(b'c')
    value = SubArcV3_Serial.readline()
    valueInString = str(value,'UTF-8')
    print(valueInString)
    average_angle_value = read_average_angle()
    if len(valueInString) > 10:
        printVal = valueInString.replace(f'\r\n', '')

        f.write(f"{printVal}, {average_angle_value}\n")
    f.close()
    #AksIM2_Serial.flushInput()
    #SubArcV3_Serial.flushInput()


