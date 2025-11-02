import ast
import statistics

# this script was used to find the average angle deviation between SubArc and the AksIM-2 from the live output log

error_map_log_from_aksim2 = 'AngleErrorMapRotationTest1.txt'  # error map file for data operation
error_map_for_graphing = 'AngleMapForGraphing.txt'  # used to generate graphs in Power BI


def print_average_std():  # function to find the average and standard deviation

    with open(error_map_log_from_aksim2, 'r') as infile:  # opens the data file
        data_list = []  # creates data list to store info temporarily

        for line in infile:  # goes through lines
            # Strip whitespace characters (like newline and spaces)
            line = line.strip()

            # Check if the line is not empty
            if line:
                try:  # making sure line isn't buggy
                    actual_line = line.replace("Angle Error: ", '')  # re-formats file
                    actual_line2 = actual_line.split(",")[0]  # Splits by the first space and keeps only the first part
                    data_list.append(abs(ast.literal_eval(actual_line2)))
                except:
                    pass

        # print(data_list)  # prints the data list that was formatted
        average = sum(data_list) / len(data_list)  # finds the average
        print(average)  # prints the average

        std_dev = statistics.stdev(data_list)  # finds the standard deviation 1 sigma
        print(std_dev)  # prints the standard deviation


def graphing_error_data():  # formats the data file used for visualization of angle error
    with open("CombinedRotationData.txt", 'r') as infile:
        with open(".txt", 'w') as outfile:
            data_list = []
            for line in infile:
                # Strip whitespace characters (like newline and spaces)
                line = line.strip()

                # Check if the line is not empty
                if line:
                    try:  # make sure line isn't buggy
                        actual_line = line.replace("Angle Error: ", '')  # formatting
                        actual_line2 = actual_line.split(",")[0]  # formatting
                        actual_line3 = line.replace("AksIM-2 Angle: ", '')  # formatting
                        actual_line4 = actual_line3.split(", ")[1]  # formatting
                        data_list.append(abs(ast.literal_eval(actual_line4)))  # appending new data
                        outfile.write(f"{abs(ast.literal_eval(actual_line4))}, {abs(ast.literal_eval(actual_line2))}\n")
                        # writes the new data
                    except:
                        pass
            # print(data_list)  # prints the data list that was formatted


# finds average error, standard deviation, and generates the graph-error-plotting file----------------------------------
graphing_error_data()

print_average_std()
# ----------------------------------------------------------------------------------------------------------------------
