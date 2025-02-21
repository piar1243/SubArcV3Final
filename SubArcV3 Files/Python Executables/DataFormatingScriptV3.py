import ast

counter = 0
angle = 0
temperature = 24.5


# Open the text file
with open("Dual100Mag&AS5600&Temp&Aksim-2Test4(temp_cal1)FullFINAL.txt", 'r') as infile:
    with open('Dual100Mag&AS5600&Temp&Aksim-2Test4(temp_cal1)FullFINALPost-Formatted.txt', 'w') as outfile:
        data_list = []

        for line in infile:
            # Strip whitespace characters (like newline and spaces)
            line = line.strip()

            # Check if the line is not empty
            if line:
                try:
                    data_list.append(ast.literal_eval(line))
                except:
                    pass
            try:
                data_list[0] = list(data_list[0])
                for i in range(5):
                    number = (i)*3
                    #print(data_list[0])
                    data_list[0].pop(number)
                    number = 0
                outfile.write(f"{data_list},\n")
                data_list = []
            except:
                pass
