import ast

import serial as serial

input_list_1 = [-1065, 91, 1135, -895, 633, -2258, 258, 28, -588, -1309, 206, 3228, 801, -437, 1782, 75, 22, 91422.2]


def format_data():
    with open("Dual100Mag&AS5600&Temp&Aksim-2Test4(temp_cal1)FINALPost-Formatted.txt", 'r') as infile:
        with open('formatted_data_file_test.txt', 'w') as outfile:
            data_list = []

            for line in infile:
                # Strip whitespace characters (like newline and spaces)
                line = line.strip()

                # Check if the line is not empty
                if line:
                    try:
                        data_list.append(ast.literal_eval(line))
                    except (SyntaxError, ValueError) as e:
                        pass

                data_list[0] = list(data_list[0])
                for i in range(4):
                    number = (i) * 3
                    # print(data_list[0])
                    data_list[0].pop(number)
                    number = 0
                outfile.write(f"{data_list},\n")
                data_list = []


#format_data()


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


def average_temperature_compensation():
    with open("Dual100Mag&AS5600&Temp&Aksim-2Test4(temp_cal1)FullFINALPost-Formatted.txt", 'r') as infile2:
        with open('AverageTemperatureCalData.txt', 'w') as outfile2:
            data_list2 = []
            for line in infile2:
                # Strip whitespace characters (like newline and spaces)
                line = line.strip()

                # Check if the line is not empty
                if line:
                    try:
                        data_list2.append(ast.literal_eval(line)[0][0])
                    except (SyntaxError, ValueError) as e:
                        pass

            #  data_list2[0] = list(data_list2[0])
           # print(data_list2)
           # print(smallest_value(data_list2))
            smallest_val = smallest_value(data_list2)
            temporary_class = 40.00
            while temporary_class > smallest_val:
                #print(temporary_class)
                temporary_class = less_than_value(data_list2, temporary_class)
               # print(temporary_class)
                average_row_array = []
                average_counter = 1
                first_slot = 0
                for row in data_list2:

                    if row[16] == temporary_class:
                        if first_slot > 0:
                            average_counter += 1
                            counter = 0
                            #("detected")
                            for value in average_row_array:
                                average_row_array[counter] = value + row[counter]
                                #print(average_row_array[counter])
                                counter += 1
                        else:
                            average_row_array = row
                            first_slot = 1

                counter3 = 0

                for value2 in average_row_array:
                    average_row_array[counter3] = value2/average_counter
                    counter3 += 1
                average_row_array[16] = round(average_row_array[16],2)
                #print(average_row_array)
                outfile2.write(f"{average_row_array},\n")
                data_list = []


average_temperature_compensation()





def tune_for_temperature(the_list):
    temperature = the_list[16]
    temp_cal = 30.08
    temp_close = 100
    temp_close2 = 100
    temp_data_list = []
    ratio_list_1 = []
    ratio_list_2 = []
    return_ratios = []
    final_return_list = []
    with open("AverageTemperatureCalData.txt", 'r') as infile_temp:
        for liner in infile_temp:
            temp_data_list.append((ast.literal_eval(liner))[0])

    for nline in temp_data_list:
        if abs(nline[16] - temperature) < temp_close:
            temp_close = abs(nline[16] - temperature)
            ratio_list_1 = nline
    print(ratio_list_1)

    for nline in temp_data_list:
        if abs(nline[16] - temp_cal) < temp_close2:
            temp_close2 = abs(nline[16] - temp_cal)
            ratio_list_2 = nline
    print(ratio_list_2)

    counterp = 0
    for liner in ratio_list_1:
        return_ratios.append(ratio_list_2[counterp] / liner)
        counterp += 1

    print(return_ratios)
    counters = 0
    for liner in the_list:
        if counters < 15:
            final_return_list.append(int(liner * return_ratios[counters]))
        else:
            final_return_list.append(liner)
        counters += 1
    return final_return_list











angle_list = []
try:
    input_list_1 = [-1088, 297, 1276, -1686, -9, -2694, -2507, 411, -1536, -1415, 128, 1626, 1023, 751, 2723, 25.66, 25.54]
    input_list_final = tune_for_temperature(input_list_1)
    print(input_list_final)
except:
    pass

