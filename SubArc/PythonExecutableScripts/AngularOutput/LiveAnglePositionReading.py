import ast
import serial
import time
import statistics

angular_position_error_log_file = "[file name for angular position error logging].txt"
final_position_calibration_file = "[file name for provided/created position calibration file].txt"
final_temperature_calibration_file = "[file name for provided/created temperature calibration file].txt"

aksim2_serial = serial.Serial('COM18', 9600, timeout=2)  # initializes communication w/ AksIM-2 calibration encoder
SubArcV3_Serial = serial.Serial(port='COM4',baudrate=115200)  # initializes communication w/ SubArc calibration encoder

#for the SubArc protocol, b is for incrementing 1 tick backwards and read I2C data
#for the SubArc protocol, c is for incrementing 1 tick forward and read I2C data

#ASCII Commands for AksIM-2 initialization & angle reading
#----------------------------------------------------------------------------------------------------------------------

ascii_1 = "v"  # checks for E201 presence
ascii_2 = "r"  # returns the serial number
ascii_3 = "V5"  # selects 5v power
ascii_4 = "n"  # turns on the encoder with 5v power
ascii_5 = "e"  # checks current
ascii_6 = "Ce"  # enables EncoLink
ascii_7 = "G0:1"  # initializes SCK
ascii_8 = "D015"  # initializes CS
# the sck and cs get sent as one complete command to the AksIM-2
ascii_9 = "M5"  # sets clock frequency
ascii_10 = "m"  # verifies selected clock frequency
ascii_11 = "j"  # initializes EncoLink (AksIM-2 communication protocol)

aksim2_angle_read_ascii = "?04:000"  # reads position bytes from the encoder

aksim2_initialization_list = ["v", "r", "V5", "n", "e", "Ce", "G0:1" "D015", "M5", "M5", "m", "j"]

#Angle determining code variables
#-----------------------------------------------------------------------------------------------------------------------
counter = 0
angle = 0
angle_second = 0
angle_third = 0
angle_fourth = 0
temperature = 24.5
data_list = []
#-----------------------------------------------------------------------------------------------------------------------

#Debugging for when SubArc data won't come through----------------------------------------------------------------------
input_list_1 = [-1065, 91, 1135, -895, 633, -2258, 258, 28, -588,
                -1309, 206, 3228, 801, -437, 1782, 75, 22, 91422.2]
input_list_2 = [-102, 232, 1344, -1019, 136, -1089, 1315, -217, -1568,
                -86, 39, -2902, 1008, -18, 2848, 69, 22, 112014.8]
input_list_3 = [-342, 48, -500, 1348, 65, -252, 302, 345, 1389,
                -782, -339, -2788, -1809, -145, -778, 85.25, 23.59, 63486.2]
input_list_4 = [-681, 11, -1072, 1332, 355, 98, -638, 132, 1921,
                326, -72, -2141, -991, -372, -1107, 81.65, 23.78, 74113.0]
input_list_5 = [-775, 268, -1494, 1040, 507, -258, -31, -117, 2268,
                -1782, 205, -2204, -861, -384, 387, 78.31, 23.77, 83804.8]
input_list_6 = [-993, 792, -814, 804, 332, -1422, 297, 481, 1619,
                -1258, -367, -843, -1017, -152, 2137, 89.38, 23.25, 51329.0]
input_list_7 = [-116, 245, -1653, 1248, 272, 872, -339, -295, 548,
                -349, 373, 2737, -595, -220, -212, 70.93, 23.45, 105652.8]
#----------------------------------------------------------------------------------------------------------------------


def aksim2_initialization():  # function to initialize the AksIM-2

    for j, command in enumerate(aksim2_initialization_list):  # loops through aksim_2 initialization asciis
        aksim2_serial.write(command.encode())  # writes the ascii command to the AksIM-2
        response = aksim2_serial.read(aksim2_serial.in_waiting)  # reads the AksIM-2 serial response
        print("response", response.decode())  # for each response, print the readable value
        time.sleep(0.1)  # ensure system isn't overloaded with sufficient time space between initializations


aksim2_initialization()  # run the aksim2 initialization


def aksim2_read_angle():  # function to read the AksIM-2 angle now that its initialized

    aksim2_serial.flushInput()  # flush input to ensure only new data enters the AksIM-2
    aksim2_serial.write(aksim2_angle_read_ascii.encode())  # writes request for position bits
    aksim2_serial.flushOutput()  # flushes output to ensure no extra corrupted data is sent with position
    time.sleep(0.01)  # spaces ensuring no overload
    response1 = aksim2_serial.read(aksim2_serial.in_waiting)  # reads the first bits
    #print(response1.decode()) #debugging

    binary_value = bin(int(response1, 16))[2:].zfill(32)
    # converts to integer, then binary, cleans line and adds zeros to front to make the value to 32 bit position

    first_20_bits = binary_value[:20]  # gets the 20 bit encoder data of the binary AksIM-2 position value

    decimal_value = int(first_20_bits, 2)  # converts the 20 bit binary into an integer position number

    #print("Binary value:", binary_value) #debugging
    #print("First 20 bits:", first_20_bits) #debugging
    #print("Decimal value of first 20 bits:", decimal_value) #debugging

    angular_value = decimal_value/1048576 * 360  # use this value if wanting to visualize AksIM-2 angular position
    time.sleep(0.01)  # delay slightly to ensure no overloading
    return decimal_value  # returns that AksIM-2 integer position value


def read_average_angle():  # averages the angle of the AksIM-2 input into the calibration file to make it more accurate
    average_angle = 0  # sets the averaging variable to 0 initially
    for k in range(5):
        average_angle += aksim2_read_angle()  # reads AksIM-2 angle 5 times, adds each value to the averaging variable
    print(average_angle/5)  # prints out the average AksIM-2 position for that specific stepper motor increment
    return average_angle/5  # returns accurate AksIM-2 position be logged in the calibration file

#initialize file


with open(final_position_calibration_file, 'r') as infile:  # opens position calibration file

    for line in infile:
        line = line.strip()  # takes all spaces out of formated file
        if line:
            try:
                data_list.append((ast.literal_eval(line))[0][0])  # strips away any extra cover lists
            except (SyntaxError, ValueError) as e:  # passes through the blank lines
                pass


# this function takes in the checking list with the SubArc readings already calibrated for temperature and mounting
def find_angle_linear_method(checking_list):  # method for finding the nearest angular position with live SubArc data
    # currently, I'm working on a faster method to reduce the amount of computing power required for each encoder
    # I'm looking to find better hall sensors so I can get the response time down to under 1/1000s instead of 1/100s

    lowest_value_score = 1000000
    temp_angle = 0
    temporary_score = 0
    for line in data_list:  # loops throughout the data list
        if checking_list[15] - 0.001 < line[15] < checking_list[15] + 0.001:
            # checks if sub-divisional AS5600 BPM value is within a specific range of the current SubArc AS5600 reading
            for j in range(14):  # checks each calibrated position line with the same sub-divisional section
                temporary_score += checking_list[j] - line[j]
                # assigns temporary score to how close the field values are for that AksIM-2 position
            if abs(temporary_score) < abs(lowest_value_score):  # creates new low score and saves index if even closer
                lowest_value_score = temporary_score
                #angle_fourth = angle_third
                #angle_third = angle_second
                #angle_second = angle
                temp_angle = line[17]
                # once lowest score (highest magnetic field match) found, return logged AksIM-2 position for fields
            temporary_score = 0  # resets temporary score

    return temp_angle/1048576 * 360  # returns the position in degrees as it is logged in 20bit integer

# debugging testing for positions
#print_test------------------------------------------------------------------------------------------------------------
#print(find_angle_linear_method(input_list_1))
#print(find_angle_linear_method(input_list_2))
#print(find_angle_linear_method(input_list_3))
#print(find_angle_linear_method(input_list_4))
#print(find_angle_linear_method(input_list_5))
#print(find_angle_linear_method(input_list_6))
#print(find_angle_linear_method(input_list_7))
#----------------------------------------------------------------------------------------------------------------------


# function reading the SubArc magnetic field data, temperature data, implementing temperature and mounting compensation
def read_data():

    reading_list = []  # creates a list for what data it will be reading
    matching_list = []  # creates a list for what data it will be matching against
    SubArcV3_Serial.write(b'b')
    # increments SubArc read data and turn encoder backwards on calibration stand, use char 'x' to just read data
    value = SubArcV3_Serial.readline()  # reads the data from SubArc and equals it to the value
    value_in_string = str(value,'UTF-8')  # converts data to readable in string value

    if len(value_in_string) > 100:  # checks if the line isn't corrupted
        reading_list.append((ast.literal_eval(value_in_string)))
        # using string value, appends SubArc data to reading_list
        for i in range(len(reading_list[0])):  # appends the actual data to the matching list for final format
            matching_list.append(reading_list[0][i])

        for i in range(5):  # removes the encoders numbers from the list to match with the calibration data
            number = (i) * 3  # finds the number
            #print(data_list[0])
            matching_list.pop(number)  # removes the number

        matching_list = list(matching_list)  # ensures the matching list is a list type

    if len(value_in_string) > 100:  # making sure the line isn't corrupt
        #print(f"{matching_list[0]}\n")
        return matching_list
        # returns the matching list compensated for temperature and mounting, sent to compare position calibration file


def less_than_value(list1, val):  # goes through the temperature compensation file to format temperature data
    close_value = 100  # not going over 100 degrees, but if you do make sure to increase this value
    temp_value = 0  # checks from 100 to 0 degrees in the file
    for line in list1:  # list 1 is the temperature calibration data
        if line[16] < val:  # if the line is less than the value of temperature mark that temperature value
            if val-line[16] < close_value:
                close_value = val-line[16]
                temp_value = line[16]
    return temp_value  # return the temperature value trying to get analyzed


def smallest_value(list1):
    smallest_val = 1000
    for line in list1:
        if line[16] < smallest_val:
            smallest_val = line[16]
    return smallest_val  # trying to d


def tune_for_temperature_and_mounting(the_list):  # the_list is the formatted SubArc data from the most recent reading
    temperature = the_list[16]  # temperature is the temperature from the SubArc data most recently read
    temp_cal = 25.5
    # sets temperature position calibrated at, in case fluctuated, please add function to read position calibration file
    temp_close = 100  # defines variables for the temp it could be, doesn't need to be anything specific
    temp_close2 = 100
    temp_data_list = []  # list for temp data
    ratio_list_1 = []  # list for ratios it creates 1
    ratio_list_2 = []  # list of rations it creates 2
    return_ratios = []  # the ratios it returns
    final_return_list = []  # the final SubArc value return list with the ratios factored in
    with open(final_temperature_calibration_file, 'r') as infile_temp:  # open the temperature calibration file
        for liner in infile_temp:  # creates infile data and then formated the temperature data
            temp_data_list.append((ast.literal_eval(liner))[0])

    for nline in temp_data_list:  # loops through the temperature calibration list
        if abs(nline[16] - temperature) < temp_close:  # finds which temperature line in the calibration file matches
            temp_close = abs(nline[16] - temperature)
            ratio_list_1 = nline

    for nline in temp_data_list:  # finds the second ration based temperature calibration from the calibration list
        if abs(nline[16] - temp_cal) < temp_close2:
            temp_close2 = abs(nline[16] - temp_cal)
            ratio_list_2 = nline  # returns the line in the calibration list with the current live SubArc temperature

    counterp = 0
    for liner in ratio_list_1:
        # gets the returning ratios by looping through the lists and dividing magnetic field values
        return_ratios.append(ratio_list_2[counterp] / liner)
        counterp += 1

    #print(return_ratios)--------------------------------------------------------------------
    counters = 0
    peak_ratios = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    # MANUALLY INPUT THESE RATIOS ONCE CALIBRATED MOUNTING IMPERFECTIONS (THAT CALIBRATION PROGRAM RETURNS THESE RATIOS)
    for liner in the_list:
        if counters < 15:
            final_return_list.append(int(liner * return_ratios[counters]*peak_ratios[counters]))
            # accounts for temp and mounting ratios and modifies them together into one set of ratios for SubArc
        else:
            final_return_list.append(liner)
        counters += 1
    return final_return_list  # returns the final list of ratios to be implemented in the SubArc field readings


repeat_value = 0  # takes the median of the SubArc values ovr multiple sensing to get accurate position
while True:  # always is going to output the live angular position and deviation between AksIM-2
    # if not on calibration stand, remove AksIM-2 code and just use the SubArc values, there will be no AksIM-2 error

    angle_list = []
    angle_list_1 = []
    for i in range(1):  # repeats reading SubArc values for the value in range
        try:
            input_list_0 = read_data()  # reads the SubArc data, gets SubArc data as input_list_0

            input_list_1 = tune_for_temperature_and_mounting(input_list_0)
            #implements calibration ratios from temperature and mounting compensation into SubArc data to input_list_1

            average_angle = find_angle_linear_method(input_list_0)  # uses calibrated SubArc data to find position
            #if average_angle != repeat_value:
            angle_list.append(average_angle)  # adds the angle found in this loop to the angle list
            #print(find_angle_linear_method(input_list_1))
        except:  # catches errors and exceptions with SubArc data
            pass
    try:
        SubArc_angle = statistics.median(angle_list)  # repeat_value is the actual SubArc actual position value averaged
        f = open(angular_position_error_log_file, "a")  # opens the angular position error log file

        # write the angle error between SubArc and the AksIM-2, as well as their individual readings to the error log
        f.write(f"Angle Error: {(((read_average_angle())/1048576 * 360)-statistics.median(angle_list))}, " 
                f"AksIM-2 Angle: {read_average_angle()/1048576 * 360},"
                f" SubArc_V1 Angle: {statistics.median(angle_list)}\n")

        # prints the angle error between SubArc and the AksIM-2, as well as their individual readings to the error log
        print(f"Angle Error: {(((read_average_angle())/1048576 * 360)-statistics.median(angle_list))}, "
              f"AksIM-2 Angle: {read_average_angle()/1048576 * 360},"
              f" SubArc_V1 Angle: {statistics.median(angle_list)}")

        f.close()  # closes file for next cyle of writing

    except:  # catches any last errors
        pass
