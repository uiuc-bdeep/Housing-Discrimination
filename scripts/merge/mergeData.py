import pandas as pd
import os
import datetime, pytz
from tqdm import tqdm

OUTPUT_FILE = 'toxic_rerun_final.csv'
TRULIA_ADDRESSES_FILE = 'round_1_census.csv'
TIMESTAMP_FILE = 'rerun_1_timestamps_5_10_19.csv'

for file in os.listdir('input'):
	if 'census' in file:
		TRULIA_ADDRESSES_FILE = file
	elif 'timestamp' in file:
		TIMESTAMP_FILE = file
	else:
		pass

def inquiryParse(d):
	if '/' in d:
		tmp = d.split('/') # 3,16,19 20:25
		tmp2 = tmp[2].split(' ') #19,20:25
		tmp3 = tmp2[1].split(':')# 20,25
		month, day, year, hour, minute = int(tmp[0]), int(tmp[1]), int('20' + tmp2[0]), int(tmp3[0]), int(tmp3[1])
	if '-' in d:
		tmp = d.split('-')
		tmp2 = tmp[2].split(' ')
		tmp3 = tmp2[1].split(':')
		year, month, day, hour, minute = int('20' + tmp[0]), int(tmp[1]), int(tmp2[0]), int(tmp3[0]), int(tmp3[1])
	if len(str(year)) != 4:
		year = int(str(year)[2:])
	return pytz.timezone('America/Chicago').localize(datetime.datetime(year, month, day, hour, minute))

def responseParse(d):
	tz = d.split('-')[-1]
	year, month, day, hour, minute = int(d[0:4]), int(d[5:7]), int(d[8:10]), int(d[11:13]), int(d[14:16])
	if tz == '07:00': # (PST)
		return pytz.timezone('America/Los_Angeles').localize(datetime.datetime(year, month, day, hour, minute))
	elif tz == '04:00': # (EST)
		return pytz.timezone('America/New_York').localize(datetime.datetime(year, month, day, hour, minute))
	else: # tz == '06:00' (CST)
		return pytz.timezone('America/Chicago').localize(datetime.datetime(year, month, day, hour, minute))

def time_of_day(d, type_):
	curr_date = inquiryParse(d) if type_ == "inquiry" else responseParse(d)
	curr_minutes = curr_date.hour*60 + curr_date.minute
	if curr_minutes <= 119: 	# 00-01:59
		return "00-02"
	elif curr_minutes <= 239: 	# 02-03:59
		return "02-04"
	elif curr_minutes <= 359: 	# 04-05:59
		return "04-06"
	elif curr_minutes <= 479: 	# 06-07:59
		return "06-08"
	elif curr_minutes <= 599: 	# 08-09:59
		return "08-10"
	elif curr_minutes <= 719: 	# 10-11:59
		return "10-12"
	elif curr_minutes <= 839: 	# 12-13:59
		return "12-14"
	elif curr_minutes <= 959: 	# 14-15:59
		return "14-16"
	elif curr_minutes <= 1079: 	# 16-17:59
		return "16-18"
	elif curr_minutes <= 1199: 	# 18-19:59
		return "18-20"
	elif curr_minutes <= 1319: 	# 20-21:59
		return "20-22"
	else: 						# 22-23:59
		return "22-24"

def find(A, x):
	for i in range(len(A)):
		if A[i] == x:
			return abs((((len(A) - 1) - i) % len(A)) + 1)
	return -1

def timestampSubParse(d):
	temp = inquiryParse(d) - datetime.timedelta(hours=6)
	if temp.minute < 10:
		return "{}/{}/{} {}:0{}".format(temp.month, temp.day, temp.year, temp.hour, temp.minute)
	else:
		return "{}/{}/{} {}:{}".format(temp.month, temp.day, temp.year, temp.hour, temp.minute)

def getWeekday(date):
	return {
		0: 'Monday',
		1: 'Tuesday',
		2: 'Wednesday',
		3: 'Thursday',
		4: 'Friday',
		5: 'Saturday',
		6: 'Sunday'
	}[date.weekday()]

if __name__ == '__main__':

	print()

	# delete old output data if necessary
	if OUTPUT_FILE in os.listdir('output'):
		os.remove(os.getcwd() + '/output/' + OUTPUT_FILE)
		print("Old output data has been deleted. \n")

	inquiry_dict = {}

	# get addresses
	df_trulia = pd.read_csv(os.getcwd() + '/input/' + TRULIA_ADDRESSES_FILE)
	# Do NOT want to drop duplicates here
	#df_trulia = df_trulia.drop_duplicates(subset = 'Address')
	#df_trulia =i df_trulia.reset_index(drop=True)
	
	print("Acquired Trulia addresses. \n")

	individual_timestamp_dfs = []

	# create individual address timestamp dataframes
	df_timestamp = pd.read_csv(os.getcwd() + '/input/' + TIMESTAMP_FILE)
	num_inquiries = int(df_timestamp.columns.tolist()[-1].split(" ")[-1])
	df_timestamp['person_name'] = df_timestamp['first name'] + ' ' + df_timestamp['last name']
	for i in tqdm(range(1, num_inquiries + 1), desc="Writing Timestamp Dataframes", bar_format="{l_bar}{bar}|  {n_fmt}/{total_fmt}   "):
		cols = ['person id', 'person_name', 'gender', 'racial category',
			'education level', 'address ' + str(i), 'timestamp ' + str(i), 'inquiry order ' + str(i)]
		tempDF = df_timestamp[cols]
		address_list = [x for x in tempDF['address ' + str(i)].values if str(x) not in (' ','','nan','NaN')]
		tempDF = tempDF.reset_index(drop=True)
		if len(address_list) != 0:
			print(tempDF['address ' + str(i)])
			tempDF['address ' + str(i)] = tempDF['address ' + str(i)].str.split(',', expand=True)[0].str.split('(', expand=True)[1].astype(int)
			for j in range(len(tempDF)):
				inquiry_dict[(tempDF['person_name'][j], tempDF['address ' + str(i)][j])] = tempDF['inquiry order ' + str(i)][j]
			old_columns=['person id', 'person_name', 'gender', 'racial category',
					'education level', 'address ' + str(i), 'timestamp ' + str(i)]
			new_columns=['person id', 'person_name', 'gender', 'racial category',
					'education level', 'trial id', 'timestamp inquiry sent out']
			tempDF = tempDF[old_columns]
			tempDF = tempDF.rename(index=str, columns={ old_columns[k]: new_columns[k] for k in range(len(new_columns))})
			individual_timestamp_dfs.append(tempDF)

	print()

	individual_timestamp_dfs_merge_trulia = []

	# join trulia addresses file with each individual timestamp dataframe
	for individual_timestamp_df in tqdm(individual_timestamp_dfs, desc="Merging Timestamp Dataframes with Trulia Addresses", bar_format="{l_bar}{bar}|  {n_fmt}/{total_fmt}   "):
		individual_timestamp_df_merge_trulia = pd.merge(df_trulia, individual_timestamp_df,
			#left_on=['Address'],
			#right_on=['inquiry_address'],
			left_on=['ID'],
			right_on=['trial id'],
			how='right')
		individual_timestamp_df_merge_trulia = individual_timestamp_df_merge_trulia.sort_values('person id')
		individual_timestamp_dfs_merge_trulia.append(individual_timestamp_df_merge_trulia)

	print()

	# combine above dataframes
	df_final = None
	flag = True
	for individual_timestamp_df_merge_trulia in tqdm(individual_timestamp_dfs_merge_trulia, desc="Combining Merged Timestamp Dataframes", bar_format="{l_bar}{bar}|  {n_fmt}/{total_fmt}   "):
		if flag:
			df_final = individual_timestamp_df_merge_trulia
			flag = False
		else:
			df_final = df_final.append(individual_timestamp_df_merge_trulia, ignore_index=True)
	
	print()

	# merge file with combined responses
	df_final = pd.merge(df_final, pd.read_csv(os.getcwd() + '/input/responses_concatenated.csv'),
			left_on=['person_name', 'trial id'], #'inquiry_address'],
			right_on=['people_name_selection/person_name', 'trial_id_'], #'address_selection/property'],
			how='left')

	# create new column for "timeDiff" and "response"
	diffs = []
	resp = []
	for i in tqdm(range(len(df_final)), desc="Creating 'timeDiff' and 'response' Columns", bar_format="{l_bar}{bar}|   "):
		# dateTime_selection/timestamp := timestamp of response received
		# timestamp inquiry sent out := timestamp of inquiry sent out
		if len(str(df_final['timestamp inquiry sent out'][i])) > 5 and len(str(df_final['dateTime_selection/timestamp'][i])) > 5:
			# decrease 'timestamp inquiry sent out' column by 5 hours
			df_final['timestamp inquiry sent out'][i] = timestampSubParse(str(df_final['timestamp inquiry sent out'][i]))
			# append to time diff column
			diffs.append(responseParse(str(df_final['dateTime_selection/timestamp'][i])) - inquiryParse(str(df_final['timestamp inquiry sent out'][i])))
			diffs[-1] = (diffs[-1].days*24*60) + (diffs[-1].seconds/60.0)
			resp.append(1)
		else:
			diffs.append("")
			resp.append(0)

	df_final['timeDiff'] = pd.Series(diffs) # timeDiff is in minutes
	df_final['response'] = pd.Series(resp)
	
	print()

	D = {}
	for i in range(len(df_final)):
		if df_final['response'][i] == 1:
			if not (df_final['person_name'][i], df_final['trial id'][i]) in D:
				D[(df_final['person_name'][i], df_final['trial id'][i])] = [responseParse(df_final['dateTime_selection/timestamp'][i])]
			else:
				D[(df_final['person_name'][i], df_final['trial id'][i])].append(responseParse(df_final['dateTime_selection/timestamp'][i]))

	for key in D:
		D[key].sort()
		D[key].reverse()

	roundNumbers = []
	addressIDs = []
	order = []
	totalResponses = []
	inquiryOrder = []
	inquiryWeekday = []
	responseWeekday = []
	income = []
	references = []
	credit = []
	employment = []
	coRenters = []
	family = []
	smoking = []
	pets = []
	criminal_history = []
	eviction_history = []
	rental_history = []
	government_housing_vouchers = []
	inquiry_time_of_day = []
	response_time_of_day = []
	for i in tqdm(range(len(df_final)), desc="Creating Additional Columns", bar_format="{l_bar}{bar}|   "):
		trial_id = str(df_final['trial id'][i])
		if trial_id == 'nan':
			roundNumbers.append('')
			addressIDs.append('')
		else:
			roundNumbers.append(str(int(df_final['trial id'][i]))[:-3])
			addressIDs.append(str(int(df_final['trial id'][i]))[-3:])
		#print(str(int(df_final['ID'][i])))
		# for matches
		if df_final['response'][i] == 1:
			order.append(find(D[(df_final['person_name'][i], df_final['trial id'][i])], responseParse(df_final['dateTime_selection/timestamp'][i]))) #address_selection/property
			totalResponses.append(len(D[(df_final['person_name'][i], df_final['trial id'][i])]))
			inquiryOrder.append(inquiry_dict[(df_final['person_name'][i], df_final['trial id'][i])]) #inquiry_address
			inquiryWeekday.append(getWeekday(inquiryParse(str(df_final['timestamp inquiry sent out'][i]))))
			responseWeekday.append(getWeekday(responseParse(str(df_final['dateTime_selection/timestamp'][i]))))
			inquiry_time_of_day.append(time_of_day(str(df_final['timestamp inquiry sent out'][i]), "inquiry"))
			response_time_of_day.append(time_of_day(str(df_final['dateTime_selection/timestamp'][i]), "response"))

			if str(df_final['screening_selection/screening_terms'][i] != 'nan'):
				income.append(1) if 'Income' in df_final['screening_selection/screening_terms'][i] else income.append(0)
				references.append(1) if 'References' in df_final['screening_selection/screening_terms'][i] else references.append(0)
				credit.append(1) if 'Credit' in df_final['screening_selection/screening_terms'][i] else credit.append(0)
				employment.append(1) if 'Employment/Job' in df_final['screening_selection/screening_terms'][i] else employment.append(0)
				coRenters.append(1) if 'Co-renters/Roommates' in df_final['screening_selection/screening_terms'][i] else coRenters.append(0)
				family.append(1) if 'Family' in df_final['screening_selection/screening_terms'][i] else family.append(0)
				smoking.append(1) if 'Smoking' in df_final['screening_selection/screening_terms'][i] else smoking.append(0)
				pets.append(1) if 'Pets' in df_final['screening_selection/screening_terms'][i] else pets.append(0)
				criminal_history.append(1) if 'Criminal History' in df_final['screening_selection/screening_terms'][i] else criminal_history.append(0)
				eviction_history.append(1) if 'Eviction History' in df_final['screening_selection/screening_terms'][i] else eviction_history.append(0)
				rental_history.append(1) if 'Rental History' in df_final['screening_selection/screening_terms'][i] else rental_history.append(0)
				government_housing_vouchers.append(1) if 'Government Housing Vouchers' in df_final['screening_selection/screening_terms'][i] else government_housing_vouchers.append(0) 
		else:
			if len(str(df_final['timestamp inquiry sent out'][i])) > 5:
				inquiryOrder.append(inquiry_dict[(df_final['person_name'][i], df_final['trial id'][i])]) #inquiry_address
				inquiryWeekday.append(getWeekday(inquiryParse(str(df_final['timestamp inquiry sent out'][i])))) 
			else:
				#inquiryOrder.append('n/a')
				inquiryOrder.append(inquiry_dict[(df_final['person_name'][i], df_final['trial id'][i])]) #inquiry_address
				inquiryWeekday.append('')
			
			# for non-matches
			order.append('')
			totalResponses.append(0)
			responseWeekday.append('')
			income.append('')
			references.append('')
			credit.append('')
			employment.append('')
			coRenters.append('')
			family.append('')
			smoking.append('')
			pets.append('')
			criminal_history.append('')
			eviction_history.append('')
			rental_history.append('')
			government_housing_vouchers.append('')

	# add columns to df
	df_final['round'] = pd.Series(roundNumbers)
	df_final['address_id'] = pd.Series(addressIDs)
	df_final['response_order'] = pd.Series(order)
	df_final['total_responses'] = pd.Series(totalResponses)
	df_final['inquiry_order'] = pd.Series(inquiryOrder)
	df_final['inquiry_weekday'] = pd.Series(inquiryWeekday)
	df_final['response_weekday'] = pd.Series(responseWeekday)
	df_final['Income'] = pd.Series(income)
	df_final['References'] = pd.Series(references)
	df_final['Credit'] = pd.Series(credit)
	df_final['Employment/Job'] = pd.Series(employment)
	df_final['Co-renters/Roommates'] = pd.Series(coRenters)
	df_final['Family'] = pd.Series(family)
	df_final['Smoking'] = pd.Series(smoking)
	df_final['Pets'] = pd.Series(pets)
	df_final['criminal_history'] = pd.Series(criminal_history)
	df_final['eviction_history'] = pd.Series(eviction_history)
	df_final['rental_history'] = pd.Series(rental_history)
	df_final['government_housing_vouchers'] = pd.Series(government_housing_vouchers)
	df_final["response_time_of_day"] = pd.Series(response_time_of_day)
	df_final["inquiry_time_of_day"] = pd.Series(inquiry_time_of_day)

	# rename certain columns
	df_final = df_final.rename(index=str, columns={"coding_option_selection/coding_option": "response_medium", "automated_message_selection/person_or_computer": "person_or_computer", "dateTime_selection/timestamp": "timestamp_response_received"})
	# reorder columns
	cols = df_final.columns.tolist()
	x    = enumerate(cols)
	for xx in x: 
		print(xx)

	# real columns
	cols = [cols[1]] + cols[121:123] + cols[2:43] + cols[44:84] + [cols[112],cols[111],cols[107],cols[110],cols[114],cols[113],cols[85],cols[105],cols[117]] + cols[119:121] + cols[123:]
	df_final = df_final[cols]

	# make sure all column names do not have spaces
	cols = df_final.columns.tolist()
	new_headers = [col.replace(" ", "_") for col in cols]
	df_final = df_final.dropna(subset=['Address'])
	df_final.to_csv(os.getcwd() + '/output/' + OUTPUT_FILE, 
		columns=cols,
		header = new_headers,
		index=False)
	print(OUTPUT_FILE + ' has been written. \n')

	# delete responses_concatenated.csv, since we don't need it anymore
	#os.remove(os.getcwd() + '/input/responses_concatenated.csv')
