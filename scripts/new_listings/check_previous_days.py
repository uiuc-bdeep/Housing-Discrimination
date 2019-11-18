import csv

url_dic = {}
days = ['11_07', '11_11', '11_12', '11_13', '11_14']

def add_url_to_dic(url, day):
    if url in url_dic:
        url_dic[url][day] = 1
    else:
        url_dic[url] = {day: 1}

def fill_missing_days(days):
    for url in url_dic.keys():
        for day in days:
            if day not in url_dic[url].keys():
                url_dic[url][day] = 0

def check_dic_value(days, url):
    url_found = 0
    for day in days:
        if url_found == 0 and url_dic[url][day] == 1:
            url_found = 1
        elif url_found == 1 and url_dic[url][day] == 0:
            url_found = 2
        elif url_found == 2 and url_dic[url][day] == 1:
            return 1
    return 0

for day in days:
    url_path = "../../rounds/new_listings/day_{}/urls_{}.csv".format(day, day)
    with open(url_path, "r") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            url = row[0]
            if url == "URL":
                continue
            add_url_to_dic(url, day)

fill_missing_days(days)
count_total = 0
count_bad = 0
for url in url_dic.keys():
    count_total += 1
    count_bad += check_dic_value(days, url)
print("Number incorrectly identified: {}".format(count_bad))
print("Total number of URLs: {}".format(count_total))

