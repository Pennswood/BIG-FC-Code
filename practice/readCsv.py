import csv

with open("csv.csv", newline='') as csvfile:
    output = []
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        output.append(row)

print(output)