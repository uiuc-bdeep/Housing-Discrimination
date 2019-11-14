import sys
import csv

if len(sys.argv) != 3:
	print("Must include two url csvs as input")
	exit()

day1 = sys.argv[1]
day2 = sys.argv[2]
destination = "new_urls.csv"
print("Day 1: " + day1)
print("Day 2: " + day2)

urls1 = []
with open(day1, "r") as f1:
	for line in f1:
		urls1.append(line)

result = []
with open(day2, "r") as f2:
	for line in f2:
		if line not in urls1:
			result.append(str(line.split('\r')[0]))

print(result)

with open(destination, 'w') as f:
	csv_writer = csv.writer(f, delimiter=',')
	csv_writer.writerow(["URLs"])
	for url in result:
		csv_writer.writerow([str(url)])

print("Total new URLs: {}".format(len(result)))
print("Results written to " + destination)
