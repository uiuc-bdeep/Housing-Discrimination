import csv
import sys

if len(sys.argv) != 2:
    print("Must include day as argument (format mm_dd)")
    print("Example: python graph_listings_daily.py 11_07")
    exit()

def count_given_day(day, new_urls):
    count = 0
    url_file = "../../rounds/new_listings/day_{}/urls_{}.csv".format(day_1, day_1)
    with open(url_file, "r") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if row[0] in new_urls:
                count += 1
    return count


days = ['11_11', '11_12', '11_13', '11_14']
day_1 = sys.argv[1]
new_listings_file = "../../rounds/new_listings/day_{}/days_on_trulia_{}.csv".format(day_1, day_1)
new_urls = []
with open(new_listings_file, "r") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        url = row[0]
        if url != "URL":
            new_urls.append(url)

print("Original number of listings = {}".format(len(new_urls)))
for day in days:
    day_count = count_given_day(day, new_urls)
    print(day, day_count)
