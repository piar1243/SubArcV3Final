import ast

""" the purpose of this test is to 1) check whether the entire file, for each smallest increment, has a change of 
greater than +-10uT, and 2) to generate a file that represents the change in all the positions"""

input_file = "Dual100Mag&AS5600&Temp&Aksim-2Test3Post-Formatted.txt"  # formatted position calibration file
formatted_testing_file = "Text2Out.txt"  # output file for the formatted data that is operated on
output_greatest_change_file = "greatest_change.txt"  # output file of the greatest change between each line


# variables used in testing code
previous_line = []  # for subtracting the difference between lines to find the greatest change between them
current_line = []
previous_line01 = []
final_list = []  # final list of greatest change between each smallest increment

with open(input_file, 'r') as infile:  # formats data file for checking the change between each line

    with open(formatted_testing_file, 'w') as outfile:  # outputs the formatted testing file for position
        counter10 = 0  # counter to track looping through position file
        for line in infile:  # loops through the position file

            line = ast.literal_eval(line.strip())  # removes the white space

            if counter10 == 0:  # checks if its the first pass through the loop

                current_line = line  # sets the current line
                previous_line01 = line  # defines the previous line
                # this portion is used to skip past the initialization data at the beginning

            if counter10 > 0:  # if we are past th initialization data

                current_line = line  # sets the current line
                for i in range(15):  # takes the difference between each value of the current and previous line
                    outfile.write(f"{abs(current_line[0][0][i]) - abs(previous_line01[0][0][i])}, ")  # write difference

                previous_line01 = line  # change current to previous line before looping again
                outfile.write("\n")  # moves to next line

            counter10 += 1  # increments the loop counter

# finds the greatest change number across all magnetic field changes for each line
with open(formatted_testing_file, 'r') as in2file:  # opens the now formatted data
    with open(output_greatest_change_file, 'w') as out2file:  # writes the difference to the formatted data
        for line2 in in2file:  # loops through the formatted data
            line2 = ast.literal_eval(line2.strip())  # remove whitespace
            final_list.append(line2)  # append that line to the final list
            greatest_change_temp = 0  # change
            counter2 = 0  # defines the second counter to loop through the final list again
            counter_abs = []  # absolute value of changes (doesn't matter about + or -)
            for number in final_list[0]:  # loops through the numbers of the final list line
                if abs(number) > abs(greatest_change_temp):  # checks if they are greater than the change
                    greatest_change_temp = number  # saves greatest change
            for number in final_list[0]:
                counter2 += 1  # loops through the next greatest
                if abs(number) >= abs(greatest_change_temp):  # checks if they are greater than the change
                    counter_abs.append(counter2)  # appends the counter

            out2file.write(f"{greatest_change_temp}\n")  # appends the greatest change number for that line

            final_list = []  # appends the greatest change for that line to the list of greatest changes for the file

# prints the lines if there was not at least a +-10uT change
with open(input_file, 'r') as file6, open(output_greatest_change_file, 'r') as file7:
    # Use zip to iterate over both files simultaneously
    for line6, line7 in zip(file6, file7):
        # Process the lines from both files

        change_val = ast.literal_eval(line7.strip())  # removes whitespace to get the change value
        if change_val == 0:
            print(f"File1: {line6.strip()}")
            print(f"File2: {line7.strip()}")  # prints the lines if there was not at least a +-10uT change


def print_lowest_change():  # used the print the lowest change from the output file so you don't have to manually check
    counter3 = 0  # looping counter
    with open(output_greatest_change_file, 'r') as in3file:  # opens greatest change logged file

        for line3 in in3file:  # checks if each file has a lowest greatest change
            line3 = ast.literal_eval(line3.strip())
            if abs(int(line3)) > abs(counter3) or abs(counter3) > abs(int(line3)):  # checks if lower than the last line
                counter3 = int(line3)  # sets counter3 equal to the lowest greatest change

        print(counter3)  # prints lowest greatest change value, if 0, then there isn't a +-10uT change of all increments


print("File complete.")
