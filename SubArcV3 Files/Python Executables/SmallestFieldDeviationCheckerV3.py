import ast

input_file = "Dual100Mag&AS5600&Temp&Aksim-2Test3Post-Formatted.txt"
output_file = "Text2Out.txt"
output_file_2 = "greatest_change.txt"
current_number = 0
line_count = 0
total_count = 0
previous_line = []
current_line = []
previous_line_0 = []
previous_line_1 = []
previous_line_2 = []
previous_line_3 = []
previous_line_4 = []
final_list = []
current_line = []
previous_line01 = []

with open(input_file, 'r') as infile:

    with open(output_file, 'w') as outfile:
        counter10 = 0
        for line in infile:

            line = ast.literal_eval(line.strip())

            if counter10 == 0:

                current_line = line
                print(current_line[0][0][1])
                previous_line01 = line

            if counter10 > 0:

                current_line = line
                for i in range(15):
                    outfile.write(f"{abs(current_line[0][0][i]) - abs(previous_line01[0][0][i])}, ")

                previous_line01 = line
                outfile.write("\n")

            counter10+=1


with open(output_file, 'r') as in2file:
    with open(output_file_2, 'w') as out2file:
        for line2 in in2file:
            line2 = ast.literal_eval(line2.strip())
            final_list.append(line2)
            greatest_change_temp = 0
            counter2 = 0
            counter_abs = []
            for number in final_list[0]:
                if abs(number) > abs(greatest_change_temp):
                    greatest_change_temp = number
            for number in final_list[0]:
                counter2 += 1
                if abs(number) >= abs(greatest_change_temp):
                    counter_abs.append(counter2)

            out2file.write(f"{greatest_change_temp}\n")


            final_list = []

with open(input_file, 'r') as file6, open(output_file_2, 'r') as file7:
    # Use zip to iterate over both files simultaneously
    for line6, line7 in zip(file6, file7):
        # Process the lines from both files

        change_val = ast.literal_eval(line7.strip())
        if change_val == 0:
            print(f"File1: {line6.strip()}")
            print(f"File2: {line7.strip()}")

def print_lowest_change():
    counter3 = 0
    with open(output_file_2, 'r') as in2file:

        for line2 in in2file:
            line2 = ast.literal_eval(line2.strip())
            if abs(int(line2)) > abs(counter3):
                counter3 = int(line2)

        print(counter3)

    with open(output_file_2, 'r') as in2file:

        for line2 in in2file:
            line2 = ast.literal_eval(line2.strip())
            if abs(counter3) > abs(int(line2)):
                counter3 = int(line2)

        print(counter3)



#print_lowest_change()

print("File complete.")


