import serial  # import serial for communication with the AksIM-2 and SubArc encoder
import time  # import time to initialize and properly sync readings from SubArc and the AskIM-2 angular position
import ast
import keyboard

"""This script is used for generating position/temperature calibration files,
for position calibration, change 'command' variable name to 'P', if for temperature change it to 'T' """

"""further note: if you're calibration temperature, YOU NEED TO FLUCTUATE THE AMBIENT ENVIRONMENT'S TEMPERATURE
slowly (over a couple hours/20 degrees) while doing so for whatever range you want to calibrate for"""

COMMAND = 'T'  # change between 'P' or 'T'

position_calibration_file = "[insert name]_position.txt"  # this is the file that will receive the calibration data
final_formatted_position_calibration_file = "[insert name]_position_final_formatted.txt"  # file for live angle position


"""
note: this script will generate all the necessary calibration data into [insert name].txt for a full rotation. This 
data includes all the SubArc MLX90393 hall sensor multi-pole magnetic readings, subdividing AS5600 bi-polar magnet 
readings, temperature data, and AksIM-2 angular position readings. The formatting of the data file is as follows:

[hall_sensor_on_array #1, B1x, B1y, B1z, hall_sensor_on_array #2, B2x, B2y, B2z, hall_sensor_on_array #3, B3x, B3y, B3z, 
hall_sensor_on_array #4, B4x, B4y, B4z, hall_sensor_on_array #5, B5x, B5y, B5z, AS5600 MPM sub-divisional angular
position, TMP117 temperature, AksIM-2 angular position]
]

With this data file, the DataFormatScript can be used

"""

temperature_calibration_file = '[insert name]_temperature.txt'
formatted_temperature_calibration_file = '[insert name]_temperature_formatted.txt'
final_formatted_temperature_calibration_file = '[insert name]_final_temperature_formatted.txt'

"""to properly use the temperature calibration script, you must first
use the position calibration script and select the command 'x' to be
sent to SubArc to read its values without incrementation, you must
do this while fluctuation temperature and generate the calibration
file that way, once you have that calibration file, it can be
formatted here for temperature compensation in the live angle 
positioning script"""

# if you want to end the command early, spam escape key

aksim2_serial = serial.Serial('COM18', 9600, timeout=2)  # initializes communication w/ AksIM-2 calibration encoder
subarc_serial = serial.Serial(port='COM4',baudrate=115200)  # initializes communication w/ SubArc calibration encoder

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

AkSIM2_angle_read_ascii = "?04:000"  # reads position bytes from the encoder

aksim2_initialization_list = ["v", "r", "V5", "n", "e", "Ce", "G0:1" "D015", "M5", "M5", "m", "j"]
# list of protocol to boot up the AksIM-2 encoder and start reading position

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
    aksim2_serial.write(AkSIM2_angle_read_ascii.encode())  # writes request for position bits
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


starting_aksim2_position = read_average_angle() + 20  # gets the starting position, adds slight buffer for loop
# if you use bit increment c to increment forward, change +20 to -20
current_angle_value = read_average_angle()
over_time_counter = 0  # once position at start, clock position for 500 counts, ensuring full rotation calibration
over_time_active = False  # activates overtime

end_position_early = False

if COMMAND == 'P':
    while over_time_counter < 500 and not end_position_early:  # while not at start
        f = open(position_calibration_file, "a")  # open the calibration file you named
        subarc_serial.write(b'b')  # increment SubArc backwards once
        value = subarc_serial.readline()  # read its I2C data
        valueInString = str(value, 'UTF-8')  # convert to readable value
        print(valueInString)
        current_angle_value = read_average_angle()  # log AksIM-2 position

        if len(valueInString) > 10:  # if the data successfully came through, continue to logging it to calibration file
            printVal = valueInString.replace(f'\r\n', '')  # remove formatting values
            f.write(f"{printVal}, {current_angle_value}\n")  # save the SubArc and AksIM-2 data to the calibration file

        f.close()  # close file

        if (abs(starting_aksim2_position - current_angle_value) <= 1 or over_time_active) and over_time_counter < 500:
            over_time_counter += 1  # increment overtime
            over_time_active = True  # allows loop to continue for 500 increments

        if keyboard.is_pressed('esc'):
            end_position_early = True

        #  if lagging or data collecting problems occur, try enabling this --------------
        #AksIM2_Serial.flushInput()
        #SubArcV3_Serial.flushInput()
        #  ------------------------------------------------------------------------------

    # once the calibration file is generated, it's formatted into a file used by  live angular position resolver script

temperature_done = False  # checks whether temp is done calibrating


if COMMAND == 'T':
    while not temperature_done:
        f = open(temperature_calibration_file, "a")  # open the calibration file you named
        subarc_serial.write(b'x')  # prompts SubArc to be read without position
        value = subarc_serial.readline()  # read its I2C data
        valueInString = str(value, 'UTF-8')  # convert to readable value
        print(valueInString)
        current_angle_value = read_average_angle()  # log AksIM-2 position

        if len(valueInString) > 10:  # if the data successfully came through, continue to logging it to calibration file
            printVal = valueInString.replace(f'\r\n', '')  # remove formatting values
            f.write(f"{printVal}, {current_angle_value}\n")  # save the SubArc and AksIM-2 data to the calibration file

        f.close()  # close file
        if keyboard.is_pressed('esc'):  # spam escape when done calibrating temperature to exit loop
            temperature_done = True


with open(position_calibration_file if COMMAND == 'P' else temperature_calibration_file, 'r') as infile:
    with open(final_formatted_position_calibration_file if COMMAND == 'P' else
              formatted_temperature_calibration_file, 'w') as outfile:
        data_list = []  # creates list to add formatted data to
        for line in infile:  # goes through the lines of the calibration file
            line = line.strip()  # strip all newlines and spaces

            if line:  # Check if the line is empty
                try:
                    data_list.append(ast.literal_eval(line))  # try getting the line of data
                except:
                    pass
            try:
                data_list[0] = list(data_list[0])  # getting the line data in a list format
                for i in range(5):
                    number = i*3  # goes through all the encoder numbers and removes them
                    #print(data_list[0])
                    data_list[0].pop(number)  # remove the encoder number from the list
                    number = 0
                outfile.write(f"{data_list},\n")  # write the new data list to the final formatted calibration file
                data_list = []  # clears the data list so it can operate on the next calibration file line
            except:  # catches corrupt lines as a final check and continues formatting
                pass


if COMMAND == 'P':
    print("position calibration has been completed")
if COMMAND == 'T':
    print("temperature calibration has been completed, now generating final formatted file")


""" this next portion of the code formats all the temperature data into an average file with magnetic values for each 
temperature to find the ratios later on in live angle positioning"""


def less_than_value(list1, val):  # for looping through the temp comp, finds the lower value to average
    close_value = 100  # arbitrarily large
    temp_value = 0
    for line4 in list1:  # loops through the lines and checks their temperature values
        if line4[16] < val:  # finds the lower value
            if val-line4[16] < close_value:  # changes temp and close value if going lower
                close_value = val-line4[16]
                temp_value = line4[16]
    return temp_value  # returns the temp value from the lowest range value of that temperature line


def smallest_value(list1):  # finds the smallest temperature value in the range of the calibration file
    smallest_val = 1000
    for line5 in list1:
        if line5[16] < smallest_val:  # continues looping to find the smallest value then break loop
            smallest_val = line5[16]
    return smallest_val  # returns the smallest value to be used in the range of looping of averaging fields for temps


def average_temperature_compensation():  # takes the temperature fields and averages them for each temperature
    with open(formatted_temperature_calibration_file, 'r') as infile2:  # file used in the code
        with open(final_formatted_temperature_calibration_file, 'w') as outfile2:  # used in live angle positioning
            data_list2 = []  # open data list to write the data to for the final formatted file
            for line2 in infile2:
                line2 = line2.strip()  # takes all spaces out of formated file
                if line2:
                    try:
                        data_list2.append(ast.literal_eval(line2)[0][0])  # strips away any extra cover lists
                    except (SyntaxError, ValueError) as e:   # passes through the blank lines
                        pass

            #  data_list2[0] = list(data_list2[0])
            # print(data_list2)
            # print(smallest_value(data_list2))

            smallest_val = smallest_value(data_list2)  # finds the smallest value in the temperature compensation
            temporary_class = 40.00  # temporary temperature for looping
            while temporary_class > smallest_val:  # while the temporary temperature is greater than the smallest value\
                print('finished')
                #print(temporary_class)
                temporary_class = less_than_value(data_list2, temporary_class)  # checks if the temp is less than

                average_row_array = []  # new array for the averages to send to final file
                average_counter = 1
                first_slot = 0
                for row in data_list2:  # loops through data list 2

                    if row[16] == temporary_class:  # checks if its on that specific temperature
                        if first_slot > 0:
                            average_counter += 1  # continues the average counting until temp changes
                            counter = 0
                            #("detected")
                            for value in average_row_array:
                                average_row_array[counter] = value + row[counter]  # adds the values together
                                #print(average_row_array[counter])
                                counter += 1
                        else:
                            average_row_array = row
                            first_slot = 1

                counter3 = 0  # sets up the next counter for the temperature number

                for value2 in average_row_array:
                    average_row_array[counter3] = value2/average_counter  # averages the values by dividing count
                    counter3 += 1
                average_row_array[16] = round(average_row_array[16], 2)  # rounds the average field values 2 decimals
                #print(average_row_array)
                outfile2.write(f"{average_row_array},\n")  # outputs the average field values for that temp
    print('temperature calibration is done')


average_temperature_compensation()  # runs command for final temperature cal file generation

"""NOTE: USE THE final temp and pos calibration files for the live angle positioning"""
""" now the final formatted temp/pos calibration have been generated, you will use them for the live angular position
 resolving along with the peak calibration file ratios if SubArc out of tune"""