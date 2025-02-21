import ast
import serial
import time
import math
import statistics

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

#Angle determining code variables
#----------------------------------------------------------------------------------------------------------------------

counter = 0
angle = 0
angle_second = 0
angle_third = 0
angle_fourth = 0

temperature = 24.5

input_list_1 = [-1065, 91, 1135, -895, 633, -2258, 258, 28, -588, -1309, 206, 3228, 801, -437, 1782, 75, 22, 91422.2]
input_list_2 = [-102, 232, 1344, -1019, 136, -1089, 1315, -217, -1568, -86, 39, -2902, 1008, -18, 2848, 69, 22, 112014.8]
input_list_3 = [-342, 48, -500, 1348, 65, -252, 302, 345, 1389, -782, -339, -2788, -1809, -145, -778, 85.25, 23.59, 63486.2]
input_list_4 = [-681, 11, -1072, 1332, 355, 98, -638, 132, 1921, 326, -72, -2141, -991, -372, -1107, 81.65, 23.78, 74113.0]
input_list_5 = [-775, 268, -1494, 1040, 507, -258, -31, -117, 2268, -1782, 205, -2204, -861, -384, 387, 78.31, 23.77, 83804.8]
input_list_6 = [-993, 792, -814, 804, 332, -1422, 297, 481, 1619, -1258, -367, -843, -1017, -152, 2137, 89.38, 23.25, 51329.0]
input_list_7 = [-116, 245, -1653, 1248, 272, 872, -339, -295, 548, -349, 373, 2737, -595, -220, -212, 70.93, 23.45, 105652.8]


data_list = []

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
    #print(f"Aksim-2 angle: {(average_angle/5)/1048576 * 360}")
    return average_angle/5


#initialize file


with open("Dual100Mag&AS5600&Temp&Aksim-2Test3Post-Formatted.txt", 'r') as infile:

    for line in infile:
        # Strip whitespace characters (like newline and spaces)
        line = line.strip()
        # Check if the line is not empty
        if line:
            try:
                data_list.append((ast.literal_eval(line))[0][0])
            except (SyntaxError, ValueError) as e:
                pass


#print("angle:\n")
#print(f"{data_list[0]}")


def find_angle_linear_method(checking_list):

    lowest_value_score = 1000000
    temp_angle = 0
    temporary_score = 0
    for line in data_list:
        #  print(checking_list[5])
        if checking_list[15] - 0.001 < line[15] < checking_list[15] + 0.001:
            for j in range(14):
                temporary_score += checking_list[j] - line[j]
            if abs(temporary_score) < abs(lowest_value_score):
                lowest_value_score = temporary_score
                #angle_fourth = angle_third
                #angle_third = angle_second
                #angle_second = angle
                temp_angle = line[17]
            temporary_score = 0

    return temp_angle/1048576 * 360

#print_test------------------------------------------------------------------------------------------------------------
#print(find_angle_linear_method(input_list_1))
#print(find_angle_linear_method(input_list_2))
#print(find_angle_linear_method(input_list_3))
#print(find_angle_linear_method(input_list_4))
#print(find_angle_linear_method(input_list_5))
#print(find_angle_linear_method(input_list_6))
#print(find_angle_linear_method(input_list_7))
#----------------------------------------------------------------------------------------------------------------------


def read_data():

    reading_list = []
    matching_list = []
    SubArcV3_Serial.write(b'b')
    value = SubArcV3_Serial.readline()
    valueInString = str(value,'UTF-8')

    if len(valueInString) > 100:
        reading_list.append((ast.literal_eval(valueInString)))
        for i in range(len(reading_list[0])):
            matching_list.append(reading_list[0][i])


        for i in range(5):
            number = (i) * 3
            #print(data_list[0])
            matching_list.pop(number)

        matching_list = list(matching_list)

    if len(valueInString) > 100:
        #print(f"{matching_list[0]}\n")
        return matching_list


def less_than_value(list1, val):
    close_value = 100
    temp_value = 0
    for line in list1:
        if line[16] < val:
            if val-line[16] < close_value:
                close_value = val-line[16]
                temp_value = line[16]
    return temp_value


def smallest_value(list1):
    smallest_val = 1000
    for line in list1:
        if line[16] < smallest_val:
            smallest_val = line[16]
    return smallest_val


def tune_for_temperature(the_list):
    temperature = the_list[16]
    temp_cal = 25.5
    temp_close = 100
    temp_close2 = 100
    temp_data_list = []
    ratio_list_1 = []
    ratio_list_2 = []
    return_ratios = []
    final_return_list = []
    with open("AverageTemperatureCalDataFINAL.txt", 'r') as infile_temp:
        for liner in infile_temp:
            temp_data_list.append((ast.literal_eval(liner))[0])

    for nline in temp_data_list:
        if abs(nline[16] - temperature) < temp_close:
            temp_close = abs(nline[16] - temperature)
            ratio_list_1 = nline
    #print(ratio_list_1)

    for nline in temp_data_list:
        if abs(nline[16] - temp_cal) < temp_close2:
            temp_close2 = abs(nline[16] - temp_cal)
            ratio_list_2 = nline
    #print(ratio_list_2)

    counterp = 0
    for liner in ratio_list_1:
        return_ratios.append(ratio_list_2[counterp] / liner)
        counterp += 1

    print(return_ratios)
    counters = 0
    peak_ratios = [0.91, 1, 0.88, 0.89, 1, 0.91, 1, 1, 1, 1.11, 1, 1, 0.91, 1, 0.91]
    for liner in the_list:
        if counters < 15:
            final_return_list.append(int(liner * return_ratios[counters]*peak_ratios[counters]))
        else:
            final_return_list.append(liner)
        counters += 1
    return final_return_list


repeat_value = 0
while True:

    angle_list = []
    angle_list_1 = []
    for i in range(1):
        try:
            input_list_0 = read_data()

            input_list_1 = tune_for_temperature(input_list_0)

            print(input_list_1)

            average_angle = find_angle_linear_method(input_list_1)
            #if average_angle != repeat_value:
            angle_list.append(average_angle)
            #print(find_angle_linear_method(input_list_1))
        except:
            pass
    try:
        repeat_value = statistics.median(angle_list)
        f = open("AngleErrorMapRotationTest1TempComp.txt", "a")
        f.write(f"Angle Error: {-0.095 + (((read_average_angle())/1048576 * 360)-statistics.median(angle_list))}, AksIM-2 Angle: {read_average_angle()/1048576 * 360}, SubArc_V1 Angle: {statistics.median(angle_list)}\n")
        print(f"Angle Error: {-0.095 + (((read_average_angle())/1048576 * 360)-statistics.median(angle_list))}, AksIM-2 Angle: {read_average_angle()/1048576 * 360}, SubArc_V1 Angle: {statistics.median(angle_list)}")
        f.close()
        print(read_average_angle())

    except:
        pass




