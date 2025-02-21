import ast
import statistics
import scipy.stats as stats

def print_average_standard():

    with open("AngleErrorMapRotationTest1.txt", 'r') as infile:
        data_list = []

        for line in infile:
            # Strip whitespace characters (like newline and spaces)
            line = line.strip()

            # Check if the line is not empty
            if line:
                try:
                    actual_line = line.replace("Angle Error: ", '')
                    actual_line2 = actual_line.split(",")[0]  # Splits by the first space and keeps only the first part
                    if abs(ast.literal_eval(actual_line2)) < 0.2:
                        data_list.append(abs(ast.literal_eval(actual_line2)-0.0165))
                except:
                    pass

        print(data_list)
        average = sum(data_list) / len(data_list)
        print(average)

        std_dev = statistics.stdev(data_list)
        print(std_dev)


#print_average_standard()


def graphing_error_data():
    with open("CombinedRotationData.txt", 'r') as infile:
        with open("ErrorMap1.txt", 'w') as outfile:
            data_list = []
            for line in infile:
                # Strip whitespace characters (like newline and spaces)
                line = line.strip()

                # Check if the line is not empty
                if line:
                    try:
                        actual_line = line.replace("Angle Error: ", '')
                        actual_line2 = actual_line.split(",")[0]
                        actual_line3 = line.replace("AksIM-2 Angle: ", '')
                        actual_line4 = actual_line3.split(", ")[1]
                        data_list.append(abs(ast.literal_eval(actual_line4)))
                        outfile.write(f"{abs(ast.literal_eval(actual_line4))}, {abs(ast.literal_eval(actual_line2)-0.015)}\n")
                    except:
                        pass
            print(data_list)


graphing_error_data()

print_average_standard()
