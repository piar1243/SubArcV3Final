import ast
import serial
import time
import math
import statistics

AksIM2_Serial = serial.Serial('COM18', 9600, timeout=2)
SubArcV3_Serial = serial.Serial(port='COM4', baudrate=115200)

# ASCII Commands for AksIM-2 initialization & angle reading
# ----------------------------------------------------------------------------------------------------------------------

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

# Angle determining code variables
# ----------------------------------------------------------------------------------------------------------------------

counter = 0
angle = 0
angle_second = 0
angle_third = 0
angle_fourth = 0

temperature = 24.5

input_list_1 = [-1065, 91, 1135, -895, 633, -2258, 258, 28, -588, -1309, 206, 3228, 801, -437, 1782, 75, 22]
input_list_2 = [-102, 232, 1344, -1019, 136, -1089, 1315, -217, -1568, -86, 39, -2902, 1008, -18, 2848, 69, 22,
                112014.8]
input_list_3 = [-342, 48, -500, 1348, 65, -252, 302, 345, 1389, -782, -339, -2788, -1809, -145, -778, 85.25, 23.59,
                63486.2]
input_list_4 = [-681, 11, -1072, 1332, 355, 98, -638, 132, 1921, 326, -72, -2141, -991, -372, -1107, 81.65, 23.78,
                74113.0]
input_list_5 = [-775, 268, -1494, 1040, 507, -258, -31, -117, 2268, -1782, 205, -2204, -861, -384, 387, 78.31, 23.77,
                83804.8]
input_list_6 = [-993, 792, -814, 804, 332, -1422, 297, 481, 1619, -1258, -367, -843, -1017, -152, 2137, 89.38, 23.25,
                51329.0]
input_list_7 = [-116, 245, -1653, 1248, 272, 872, -339, -295, 548, -349, 373, 2737, -595, -220, -212, 70.93, 23.45,
                105652.8]

data_list = []


# ----------------------------------------------------------------------------------------------------------------------


def aksim2_initialization():
    for j, command in enumerate(aksim2_initialization_list):
        AksIM2_Serial.write(command.encode())
        response = AksIM2_Serial.read(AksIM2_Serial.in_waiting)
        print("response", response.decode())
        response = None
        time.sleep(0.1)


#aksim2_initialization()


def aksim2_read_angle():
    AksIM2_Serial.flushInput()
    AksIM2_Serial.write(AkSIM2_angle_read_ascii.encode())
    AksIM2_Serial.flushOutput()
    time.sleep(0.01)
    response1 = AksIM2_Serial.read(AksIM2_Serial.in_waiting)
    # print(response1.decode()) #debugging

    binary_value = bin(int(response1, 16))[2:].zfill(32)  # pad to 32 bits

    first_20_bits = binary_value[:20]

    decimal_value = int(first_20_bits, 2)

    # print("Binary value:", binary_value) #debugging
    # print("First 20 bits:", first_20_bits) #debugging
    # print("Decimal value of first 20 bits:", decimal_value) #debugging
    angular_value = decimal_value / 1048576 * 360
    time.sleep(0.01)
    return decimal_value


def read_average_angle():
    average_angle = 0
    for k in range(5):
        average_angle += aksim2_read_angle()
    # print(f"Aksim-2 angle: {(average_angle/5)/1048576 * 360}")
    return average_angle / 5


# initialize file


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


# print("angle:\n")
# print(f"{data_list[0]}")


def find_angle_linear_method(checking_list):
    lowest_value_score = 1000000
    temp_array = []
    temporary_score = 0

    for line in data_list:
        #  print(checking_list[5])
        if checking_list[15] - 0.3 < line[15] < checking_list[15] + 0.3:
            for j in range(14):
                temporary_score += checking_list[j] - line[j]
            if abs(temporary_score) < abs(lowest_value_score):
                lowest_value_score = temporary_score
                # angle_fourth = angle_third
                # angle_third = angle_second
                # angle_second = angle
                temp_array = line
            temporary_score = 0

    return temp_array


# print_test------------------------------------------------------------------------------------------------------------
# print(find_angle_linear_method(input_list_1))
# print(find_angle_linear_method(input_list_2))
# print(find_angle_linear_method(input_list_3))
# print(find_angle_linear_method(input_list_4))
# print(find_angle_linear_method(input_list_5))
# print(find_angle_linear_method(input_list_6))
# print(find_angle_linear_method(input_list_7))
# ----------------------------------------------------------------------------------------------------------------------


def read_data():
    reading_list = []
    matching_list = []
    SubArcV3_Serial.write(b'b')
    value = SubArcV3_Serial.readline()
    valueInString = str(value, 'UTF-8')

    if len(valueInString) > 100:
        reading_list.append((ast.literal_eval(valueInString)))
        for i in range(len(reading_list[0])):
            matching_list.append(reading_list[0][i])

        for i in range(5):
            number = (i) * 3
            # print(data_list[0])
            matching_list.pop(number)

        matching_list = list(matching_list)

    if len(valueInString) > 100:
        # print(f"{matching_list[0]}\n")
        print(f"read data: {matching_list}")
        return matching_list


def read_data_2():
    reading_list = []
    matching_list = []
    SubArcV3_Serial.write(b'c')
    value = SubArcV3_Serial.readline()
    valueInString = str(value, 'UTF-8')

    if len(valueInString) > 100:
        reading_list.append((ast.literal_eval(valueInString)))
        for i in range(len(reading_list[0])):
            matching_list.append(reading_list[0][i])

        for i in range(5):
            number = (i) * 3
            # print(data_list[0])
            matching_list.pop(number)

        matching_list = list(matching_list)

    if len(valueInString) > 100:
        # print(f"{matching_list[0]}\n")
        print(f"read data 2: {matching_list}")
        return matching_list


def find_angle_linear_method_line_list(checking_list):
    lowest_value_score = 1000000
    magnet_list = []
    magnet_list_debug = []
    temp_angle = 0
    temporary_score = 0
    check = 0
    perm_index = 0
    for index, line in enumerate(data_list, start=0):
        #  print(checking_list[5])
        if checking_list[15] - 0.3 < line[15] < checking_list[15] + 0.3:
            for j in range(14):
                temporary_score += checking_list[j] - line[j]
            if abs(temporary_score) < abs(lowest_value_score):
                lowest_value_score = temporary_score
                # angle_fourth = angle_third
                # angle_third = angle_second
                # angle_second = angle
                magnet_list = line
                perm_index = index
            temporary_score = 0

    magnet_list.append(perm_index)
    magnet_list_debug = magnet_list[:19]
    return magnet_list_debug


def find_peaks(checking_list, top_or_bottom, field_val_in_array):
    lowest_value_score = 1000000
    magnet_list = []
    temp_val = 0
    temp_angle = 0
    temporary_score = 0
    slope_direction = "positive"
    checking_value = True
    peak_val = []


    for line in data_list:
        #  print(checking_list[5])
        if line[17] == checking_list[17]:
            #print("checked")
            if top_or_bottom == "top":

                #print("checked2")
                index_start = checking_list[18]

                if data_list[index_start + 20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                    slope_direction = "positive"
                    while data_list[index_start][field_val_in_array] <= 0:
                        index_start += 40

                if data_list[index_start + 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                    slope_direction = "negative"
                    while data_list[index_start][field_val_in_array] <= 0:
                        index_start -= 40

                if data_list[index_start][field_val_in_array] > 0:  # extra check to make sure its on the positive side
                    #print(index_start)
                    if slope_direction == "positive":

                        while checking_value:
                            if data_list[index_start+20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                                #print("checked3")
                                index_start += 20
                                peak_val = data_list[index_start]
                            else:
                                checking_value = False
                    if slope_direction == "negative":

                        while checking_value:
                            if data_list[index_start-20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                                #print("checked3")
                                index_start -= 20
                                peak_val = data_list[index_start]
                            else:
                                checking_value = False

            if top_or_bottom == "bottom":

                #print("checked2")
                index_start = checking_list[18]

                if data_list[index_start + 20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                    slope_direction = "positive"
                    while data_list[index_start][field_val_in_array] > 0:
                        index_start -= 40

                if data_list[index_start + 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                    slope_direction = "negative"
                    while data_list[index_start][field_val_in_array] > 0:
                        index_start += 40

                if data_list[index_start][field_val_in_array] < 0:  # extra check to make sure its on the negative side
                    #print(index_start)
                    if slope_direction == "negative":

                        while checking_value:
                            if data_list[index_start + 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                                # print("checked3")
                                index_start += 20
                                peak_val = data_list[index_start]
                            else:
                                checking_value = False
                    if slope_direction == "positive":

                        while checking_value:
                            if data_list[index_start - 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                                # print("checked3")
                                index_start -= 20
                                peak_val = data_list[index_start]
                            else:
                                checking_value = False

            else:
                pass
    peak_val.append(slope_direction)
    peak_val = peak_val[:19]
    return peak_val


def find_real_peaks(slope_val, field_val_in_array):
    top_bottom_values = []


    print("cali")

    if slope_val == "positive":
        input_list_init = read_data()
        for number in range(80):
            intermediate = read_data()
            intermediate = []
        next_val = read_data()

        while next_val[field_val_in_array] >= input_list_init[field_val_in_array]:
            input_list_init = next_val
            for number in range(5):
                intermediate = read_data()
                intermediate = []
                #print("pls no")
            next_val = read_data()

        top_val = next_val[field_val_in_array]
        input_list_init_2 = read_data_2()
        for idea in range(100):
            intermediate = read_data_2()
            intermediate = []
        next_val_2 = read_data_2()

        while next_val_2[field_val_in_array] <= input_list_init_2[field_val_in_array]:
            input_list_init_2 = next_val_2
            for number in range(5):
                intermediate = read_data_2()
                intermediate = []
            next_val_2 = read_data_2()

        bottom_val = next_val_2[field_val_in_array]

        top_bottom_values = [top_val, bottom_val]

    if slope_val == "negative":
        input_list_init = read_data_2()
        for number in range(80):
            intermediate = read_data_2()
            intermediate = []
        next_val = read_data_2()

        while next_val[field_val_in_array] >= input_list_init[field_val_in_array]:
            input_list_init = next_val
            for number in range(5):
                intermediate = read_data_2()
                intermediate = []
            next_val = read_data_2()
            print("loop")

        top_val = next_val[field_val_in_array]
        input_list_init_2 = read_data()
        for number in range(100):
            intermediate = read_data()
            intermediate = []

        next_val_2 = read_data()

        while next_val_2[field_val_in_array] <= input_list_init_2[field_val_in_array]:
            input_list_init_2 = next_val_2
            for number in range(5):
                intermediate = read_data()
                intermediate = []
            next_val_2 = read_data()

        bottom_val = next_val_2[field_val_in_array]

        top_bottom_values = [top_val, bottom_val]

    return top_bottom_values


def check_nearest_subdivisions(datalist):
    indicies = [0, 2, 3, 5, 6, 8, 9, 11, 12, 14]
    field_to_check = 0
    final_ratio_list = []
    for i in indicies:
        closest_data_line = find_angle_linear_method_line_list(datalist)
        top_peak_cal = find_peaks(closest_data_line, "top", indicies[i])
        bottom_peak_cal = find_peaks(closest_data_line, "bottom", indicies[i])
        print(f"closest data line: {closest_data_line}")
        print(f"top peak: {top_peak_cal}")
        print(f"bottom peak: {bottom_peak_cal}")
        peaks_real = find_real_peaks(top_peak_cal[18], indicies[i])  # peaks_real is a small array returning [top_peak, bottom_peak]
        print(peaks_real)
        top_peak_ratio = top_peak_cal[indicies[i]]/(peaks_real[0])
        bottom_peak_ratio = bottom_peak_cal[indicies[i]]/ (peaks_real[1])
        print(f"top peak ratio {top_peak_ratio}")
        print(f"bottom peak ratio {bottom_peak_ratio}")

        final_ratio_list.append([top_peak_ratio, bottom_peak_ratio])


    return final_ratio_list


average_placing_1 = []

while True:

    angle_list = []
    for i in range(1):
        try:
            input_list_1 = [-1041, 440, 892, -577, 193, -1718, 628, 501, 424, -2510, -254, -1808, -761, 381, 1955, 352.71, 26.09, 333344.0]
            input_list_2 = read_data()

            # print(input_list_1)
            average_placing_1 = find_angle_linear_method(input_list_2)
            average_placing_1 = average_placing_1[:19]
        except:
            pass
    try:
        print(f"SubArc_V1 Angle: {average_placing_1}")
        check_nearest_subdivisions(average_placing_1)
        print('-----------------------------------------------------------------------------------------')

    except:
        pass

