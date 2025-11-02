import ast
import serial
import time

aksim2_serial = serial.Serial('COM18', 9600, timeout=2)  # initializes communication w/ AksIM-2 calibration encoder
SubArcV3_serial = serial.Serial(port='COM4', baudrate=115200)  # initializes communication w/ SubArc calibration encoder

position_calibration_file_reference = "[file name].txt"

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

# Angle determining code variables -------------------------------------------------------------------------------------
counter = 0
angle = 0
angle_second = 0
angle_third = 0
angle_fourth = 0
temperature = 24.5
data_list = []
# ----------------------------------------------------------------------------------------------------------------------

#debugging input lists for when SubArc isn't connected -----------------------------------------------------------------
input_list_1 = [-1065, 91, 1135, -895, 633, -2258, 258, 28, -588,
                -1309, 206, 3228, 801, -437, 1782, 75, 22]

input_list_2 = [-102, 232, 1344, -1019, 136, -1089, 1315, -217, -1568,
                -86, 39, -2902, 1008, -18, 2848, 69, 22, 112014.8]

input_list_3 = [-342, 48, -500, 1348, 65, -252, 302, 345, 1389,
                -782, -339, -2788, -1809, -145, -778, 85.25, 23.59,63486.2]

input_list_4 = [-681, 11, -1072, 1332, 355, 98, -638, 132, 1921,
                326, -72, -2141, -991, -372, -1107, 81.65, 23.78, 74113.0]

input_list_5 = [-775, 268, -1494, 1040, 507, -258, -31, -117, 2268,
                -1782, 205, -2204, -861, -384, 387, 78.31, 23.77, 83804.8]

input_list_6 = [-993, 792, -814, 804, 332, -1422, 297, 481, 1619,
                -1258, -367, -843, -1017, -152, 2137, 89.38, 23.25, 51329.0]

input_list_7 = [-116, 245, -1653, 1248, 272, 872, -339, -295, 548,
                -349, 373, 2737, -595, -220, -212, 70.93, 23.45, 105652.8]
# ---------------------------------------------------------------------------------------------------------------------


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


with open(position_calibration_file_reference, 'r') as infile:   # opens position calibration file
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


# debugging commands for when SubArc data is unavailable----------------------------------------------------------------
# print(find_angle_linear_method(input_list_1))
# print(find_angle_linear_method(input_list_2))
# print(find_angle_linear_method(input_list_3))
# print(find_angle_linear_method(input_list_4))
# print(find_angle_linear_method(input_list_5))
# print(find_angle_linear_method(input_list_6))
# print(find_angle_linear_method(input_list_7))
# ----------------------------------------------------------------------------------------------------------------------


# function reading the SubArc magnetic field data, temperature data, implementing temperature and mounting compensation
def read_data(movement_direction):

    reading_list = []  # creates a list for what data it will be reading
    matching_list = []  # creates a list for what data it will be matching against
    if movement_direction == 'b':
        SubArcV3_serial.write(b'b')
    if movement_direction == 'c':
        SubArcV3_serial.write(b'c')
    # increments SubArc read data and turn encoder backwards on calibration stand, use char 'x' to just read data
    value = SubArcV3_serial.readline()  # reads the data from SubArc and equals it to the value
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


def find_angle_linear_method_line_list(checking_list):  # function for finding the closest data line in calibration file
    lowest_value_score = 1000000  # arbitrary variable value defined for changing
    magnet_list = []  # list of magnetic values to be appended
    magnet_list_debug = []
    temp_angle = 0
    temporary_score = 0  # value to use for function
    check = 0
    perm_index = 0  # value to use for the permanent index of the closest data line in the calibration file
    for index, line in enumerate(data_list, start=0):  # gets the values in the SubArc data list
        #  print(checking_list[5])
        if checking_list[15] - 0.3 < line[15] < checking_list[15] + 0.3:  # checks if between the AS5600 BPM tolerance
            for j in range(14):  # assigns temporary score to determine if its closer or further than last pass
                temporary_score += checking_list[j] - line[j]  # builds temporary score with value comparison
            if abs(temporary_score) < abs(lowest_value_score):  # checks if new score is better
                lowest_value_score = temporary_score  # sets new score as check up
                # angle_fourth = angle_third
                # angle_third = angle_second
                # angle_second = angle
                magnet_list = line
                perm_index = index
            temporary_score = 0

    magnet_list.append(perm_index)  # adds the index of the line that was the closes to the SubArc reading
    magnet_list_debug = magnet_list[:19]  # grabs all the SubArc data from that calibration line
    return magnet_list_debug  # returns the magnet list exactly as in position calibration file, not just close


"""inputs position calibration file, which quadrant of sinusoid to check, and the nearest current
 SubArc reading for reference in where to search inside the position calibration file for"""


def find_peaks(checking_list, top_or_bottom, field_val_in_array):  
    """the following function finds the nearest hypothetical peaks in
     the SubArc position calibration file in reference to the nearest live SubArc reading"""
    # extra variables used for debugging -------------------------------------------------------------------------------
    lowest_value_score = 1000000
    magnet_list = []
    temp_val = 0
    temp_angle = 0
    temporary_score = 0
    # ------------------------------------------------------------------------------------------------------------------
    slope_direction = "positive"  # defines whether the sinusoid is going up for top peak or down for bottom peak
    checking_value = True  # checking value on the top True of bottom False
    peak_val = []  # here is where the peak values are logged

    for line in data_list:  # loops through the position calibration file
        #  print(checking_list[5]) # debugging
        if line[17] == checking_list[17]:  # checks if the lines match up with the nearest SubArc position in cal file
            #print("checked")
            if top_or_bottom == "top":  # if the peak being scanned is the top area

                #print("checked2")
                index_start = checking_list[18]  # starts the index for finding the peak

                if data_list[index_start + 20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                    # if in the first quadrant will keep incrementing until it reaches the top peak
                    slope_direction = "positive"  # the slope direction is positive in quadrant 1
                    while data_list[index_start][field_val_in_array] <= 0:
                        index_start += 40  # once the peak is found, other if statements are ignored and peak returned

                if data_list[index_start + 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                    # if in the second quadrant will keep decreasing until it reaches the top peak
                    slope_direction = "negative"  # the slope direction is negative in quadrant 2
                    while data_list[index_start][field_val_in_array] <= 0:
                        index_start -= 40  # once the peak is found, other if statements are ignored and peak returned

                if data_list[index_start][field_val_in_array] > 0:  # extra check to make sure its on the positive side
                    #print(index_start)
                    if slope_direction == "positive":  # if the slope direction is positive but its in quadrant 1

                        while checking_value:  # while the check value is true it will keep checking each increment
                            if data_list[index_start+20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                                # while the slops is still increasing
                                #print("checked3")
                                index_start += 20  # increase the index keep pushing up the position file towards peak
                                peak_val = data_list[index_start]  # the peak value is at the top, it will be returned
                            else:
                                checking_value = False  # can skip now and return the peak value
                    if slope_direction == "negative":  # extra check to make sure its on the negative side

                        while checking_value: # while the check value is true it will keep checking each increment
                            if data_list[index_start-20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                                # while the slops is still increasing
                                #print("checked3") debugging
                                index_start -= 20  # decrease the index keep pushing up the position file towards peak
                                peak_val = data_list[index_start]  # the peak value is at the top, it will be returned
                            else:
                                checking_value = False

            if top_or_bottom == "bottom":  # if the peak being scanned is the bottom area (quadrants 3 and 4)

                #print("checked2")
                index_start = checking_list[18] # starts the index for finding the peak

                if data_list[index_start + 20][field_val_in_array] >= data_list[index_start][field_val_in_array]:
                    # if in the fourth quadrant will keep incrementing until it reaches the bottom peak
                    slope_direction = "positive"  # positive slope, must increment backwards towards sinusoid bottom
                    while data_list[index_start][field_val_in_array] > 0:
                        index_start -= 40  # increments backwards through file
                        # increments backwards, once the peak found, other if statements are ignored and peak returned

                if data_list[index_start + 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                    # if in the fourth quadrant will keep incrementing until it reaches the bottom peak
                    slope_direction = "negative" # negative slope, must increment forwards towards sinusoid bottom
                    while data_list[index_start][field_val_in_array] > 0:
                        index_start += 40  # increments forwards through file
                        # increments forwards, once the peak found, other if statements are ignored and peak returned

                if data_list[index_start][field_val_in_array] < 0:  # extra check to make sure its on the negative side
                    #print(index_start)
                    if slope_direction == "negative":  # if the slope direction is negative but its in quadrant 3

                        while checking_value:  # while the check value is true it will keep checking each increment
                            if data_list[index_start + 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                                # while the slops is still decreasing
                                # print("checked3")
                                index_start += 20  # increases the index until the position is no longer decreasing
                                peak_val = data_list[index_start]  # returns peak value once position isn't decreasing
                            else:
                                checking_value = False  # breaks loop to return peak
                    if slope_direction == "positive":  # if the slope direction is positive but its in quadrant 4

                        while checking_value:  # while the check value is true it will keep checking each increment
                            if data_list[index_start - 20][field_val_in_array] < data_list[index_start][field_val_in_array]:
                                # while the slops is still increasing
                                # print("checked3")
                                index_start -= 20  # decreases the index until the position is no longer decreasing
                                peak_val = data_list[index_start]  # returns peak value once position isn't decreasing
                            else:
                                checking_value = False # breaks loop to return peak

            else:  # catches any corrupt data
                pass
    peak_val.append(slope_direction)  # appends the slope direction to the peak value
    peak_val = peak_val[:19]
    # returns the peak value from all 19 values in position calibration file line identified as peak/trough
    return peak_val  # returns the peak/trough value, name is just peak


def find_real_peaks(slope_val, field_val_in_array):  # this script now increments SubArc to find real peaks
    # those real peaks are then compared with the theoretical ones found from the position file
    # the ratio between those peaks is where the calibration ratio comes from that is used in the live angle output
    top_bottom_values = []  # array to hold the top and bottom peak values

    if slope_val == "positive":  # if the slope is positive
        input_list_init = read_data('c')  # increment forwards to get to peak
        for number in range(80):  # increments to get away from any motor gear tolerance
            intermediate = read_data('c')
            intermediate = []
        next_val = read_data('c')  # starts tracking the actual position movement

        while next_val[field_val_in_array] >= input_list_init[field_val_in_array]:  # while the slope is positive
            input_list_init = next_val  # change the value to update while loop condition
            for number in range(5):  # increment by 5
                intermediate = read_data('c')
                intermediate = []
                #print("pls no")
            next_val = read_data('c')  # log the next value

        top_val = next_val[field_val_in_array]  # once the next_val is found, the field value inside should be the peak
        input_list_init_2 = read_data('b')  # to log the bottom peak
        for idea in range(100):
            # increment 100 times to ensure gears make contact reversing direction (20bit res is very small)
            intermediate = read_data('b')
            intermediate = []
        next_val_2 = read_data('b')  # log the next value at end of 100 increments

        while next_val_2[field_val_in_array] <= input_list_init_2[field_val_in_array]:  # while not at the trough
            input_list_init_2 = next_val_2
            for number in range(5):  # increment 5 each time to speed up the calibration process
                intermediate = read_data('b')
                intermediate = []
            next_val_2 = read_data('b')  # read the data coming from the value

        bottom_val = next_val_2[field_val_in_array]  # once the bottom value is found (while loop break) = trough

        top_bottom_values = [top_val, bottom_val]  # sends off top and bottom values

    if slope_val == "negative":  # if the slope is negative
        input_list_init = read_data('b')  # increment backwards to get to peak
        for number in range(80):  # runs motor to ensure gears touch as 20bit resolution is small to get contact gears
            intermediate = read_data('b')
            intermediate = []
        next_val = read_data('b')  # logs the next values for while loop

        while next_val[field_val_in_array] >= input_list_init[field_val_in_array]:  # loops until peak value found
            input_list_init = next_val  # change the value to update while loop condition
            for number in range(5):   # increment by 5 to speed up calibration process
                intermediate = read_data('b')
                intermediate = []
            next_val = read_data('b')  # log the next value
            print("loop")  # allows for debugging on which side of sinusoid is on

        top_val = next_val[field_val_in_array]  # logs the values as the top peak value when out of while loop
        input_list_init_2 = read_data('c')
        for number in range(100):  # to begin incrementation to find bottom trough increments 100 times, contact gears
            intermediate = read_data('c')
            intermediate = []

        next_val_2 = read_data('c')  # logs the next values for while loop

        while next_val_2[field_val_in_array] <= input_list_init_2[field_val_in_array]:  # loops until trough value found
            input_list_init_2 = next_val_2  # increment forwards to get to peak
            for number in range(5):
                intermediate = read_data('c')
                intermediate = []
            next_val_2 = read_data('c') # logs the next values for while loop

        bottom_val = next_val_2[field_val_in_array]  # logs the bottom trough value when broken out of while loop

        top_bottom_values = [top_val, bottom_val]  # combines the top and bottom values into list

    return top_bottom_values  # returns list with top and bottom values to be divided against the cal file ones


# used to find all the scaling ratios for specified axes/hall sensors that are out of tune
def check_nearest_subdivisions(datalist):
    indices = [0, 2, 3, 5, 6, 8, 9, 11, 12, 14]  # which SubArc field values will you be calibrating?
    # for a full calibration, calibrate x, y, and z axis for all 15 5 hall sensors in the SubArc hall array
    field_to_check = 0
    final_ratio_list = []
    for i in indices:  # loops through all the specified x, y, z fields for each hall sensor specified in indices
        closest_data_line = find_angle_linear_method_line_list(datalist)  
        # finds the closest data line to achieve in the position calibration in reference to the position calibration
        top_peak_cal = find_peaks(closest_data_line, "top", indices[i])  # finds the top peak
        bottom_peak_cal = find_peaks(closest_data_line, "bottom", indices[i])  # finds the bottom peak
        print(f"closest data line: {closest_data_line}")  # prints the line that was closest to SubArc amplitude value
        print(f"top peak: {top_peak_cal}")  # prints the top peak line
        print(f"bottom peak: {bottom_peak_cal}")   # prints the trough line
        # once the hypothetical peaks located from the position calibration file, now the live SubArc ones are found
        peaks_real = find_real_peaks(top_peak_cal[18], indices[i])  # finds the real peaks from the SubArc values
        # peaks_real is a small array returning [top_peak, bottom_peak]
        print(peaks_real)  # print the real peaks lines
        top_peak_ratio = top_peak_cal[indices[i]]/(peaks_real[0])  
        # finds the ratio between the predicted and top peak values so they can be scaled in live angle positioning
        bottom_peak_ratio = bottom_peak_cal[indices[i]]/ (peaks_real[1])
        # finds the ratio between the predicted and bottom peak values so they can be scaled in live angle positioning
        print(f"top peak ratio {top_peak_ratio}")  # prints the top peak ratio for specific hall sensor and axis
        print(f"bottom peak ratio {bottom_peak_ratio}")  # prints the top peak ratio for specific hall sensor and axis

        final_ratio_list.append([top_peak_ratio, bottom_peak_ratio])
        # adds the top and bottom peak ratios for that specific hall sensor its axis to list with all other ratios

    return final_ratio_list  # once all mounting peak calibration ratios are found, they are returned as a final list


average_placing_1 = []  # keeps track of average SubArc position values for loop

while True:  # once code is run, the program will begin to execute

    angle_list = []  # keeping a list of the SubArc angles to average for the angles 
    for i in range(1):  # looping through to keep an average, this time loop can be chosen no enabled time efficiency
        try:
            input_list_1 = [-1041, 440, 892, -577, 193, -1718, 628, 501, 424,
                            -2510, -254, -1808, -761, 381, 1955, 352.71, 26.09, 333344.0]  # starting reference input
            # change this input value depending upon your mounting misalignment
            input_list_2 = read_data('b')  # gets data from SubArc and increments 1 backwards

            average_placing_1 = find_angle_linear_method(input_list_2)  # finds the SubArc angular position
            average_placing_1 = average_placing_1[:19]
        except:  # catch any corrupt SubArc readings and continue program
            pass
    try:
        print(f"SubArc_V1 Angle: {average_placing_1}")  # prints the SubArc angle with the average placing
        check_nearest_subdivisions(average_placing_1)  # check next line for details
        # prints the list of top and bottom peak ratios for each hall sensor and axis
        print('-----------------------------------------------------------------------------------------')  # spacing

    except:  # catch any corrupt SubArc readings and continue program
        pass
