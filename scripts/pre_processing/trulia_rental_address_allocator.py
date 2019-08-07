import re 
import os
import sys
import csv 
import random 
import linecache
import numpy as np
import pandas as pd

NUM_IDENTITES_PER_RACE = 6
NUM_RACIAL_GROUPS      = 3

def initialize_data_sheets(status, df_names, LPI):
	num_cols = (LPI*3) + 1
	timestamp_cols = ['handled']

	for i in range(1, num_cols):
		timestamp_cols.append('address ' + str(i))
		timestamp_cols.append('timestamp ' + str(i))
		timestamp_cols.append('inquiry order ' + str(i))

	df_new          = (pd.DataFrame(columns=timestamp_cols)).fillna(' ')		# empty dataframe with new columns for status sheet 

	df_timestamp    = df_names[df_names.columns[0:8]] 							# create a new dataframe from the return sheet

	df_timestamp    = pd.concat([df_timestamp, df_new], axis = 1).fillna(' ')	# concatenate old values with the new columns
	df_timestamp['handled'] = 0
	df_timestamp.to_csv(status,mode='w',index=False)

	return df_timestamp

def get_dataframes(names, status, LPI): 
	df_names = pd.read_csv(names) 						# create a dataframe with the names csv

	if os.path.isfile(status) == False: 				# check if the status sheet exists
		print('Status Sheet Not Initialized\nInitializing ...')
		df_timestamp= initialize_data_sheets(status, df_names, LPI)

	else: 
		# create a dataframe from saved status sheet csv
		df_timestamp = pd.read_csv(status)

	return df_names, df_timestamp

def test_output(df_csv,num_addr): 
	address = []
	#create a list with all addresses that were sent an inquiry
	for i in range(1,num_addr): 
		temp = list(df_csv['address ' + str(i)].values)
		for j in range(0,len(temp)): 
			temp[j] = temp[j].split(',')[0][1:]
		address = address + temp
	# remove duplicates
	address = list(set(address))

	# create a dictionary that maps an address to another dictionary that maps a racial group to a name
	address_dict = {}
	for add in address: 
		race_dict    = {'black': [], 'white': [], 'hispanic': []}
		address_dict.update({add:race_dict})

	# iterate through the dateframe to populate address_dict 
	for index, row in df_csv.iterrows(): 
		for i in range(1,num_addr):
			y = row['address ' + str(i)].split(',')[0][1:]
			address_dict[y][row['racial category']].append(row['first name']) 
	# is_correct maps an address to a 0 or 1
		# 0 - if the listing of the adress was NOT sent to all 3 racial categories
		# 1 - if the listing of the address was sent to all 3 racial categories
	is_correct = {}

	# populate is_correct
	for key,value in address_dict.items(): 
		# print('---------------------------------------------------------------------------------------------')
		# print(str(key) + ': ' + str(value))
		correct = 1
		for k,val in value.items(): 
			if len(val) != 1: 
				correct = 0
			if len(val) > 1: 
				print(k)
		is_correct.update({key:correct})

	# correct_address is a list of addresses which received an inquiry from all three racial groups
	correct_address = []
	for key, value in is_correct.items(): 
		if value == 1: 
			correct_address.append(key)
	correct_address = list(set(correct_address))
	print('Sent an inquiry: ' + str(len(address)))	
	print('Sent to all three racial groups(by dict): '+ str(len(correct_address)))

	counter = 0
	three_list = []
	for index, row in df_csv.iterrows(): 
		for i in range(1,num_addr): 
			if row['inquiry order ' + str(i)] == 3: 
				three_list.append(row['address ' + str(i)].split(',')[0][1:])
	three_list = list(set(three_list))
	print('Sent to all three racial groups(by counter): ' + str(len(three_list)))

	print('Set difference: ' + str(list(set(three_list) - set(correct_address))))

def get_partitions(df_rentals): 
	# cut the main rentals dataframe down by a criteria MAY NEED CHANGING IN THE FUTURE
	df_mod_rentals   = df_rentals.sample(frac = 1)

	# equally divide up the dataframe based on the number of races, in this case we have white, black, and hispanic
	split_df    = np.array_split(df_mod_rentals, 3)
	group_one   = split_df[0]
	#print(len(group_one))
	group_two   = split_df[1]
	#print(len(group_two))
	group_three = split_df[2]
	#print(len(group_three))
	group_one_addr = group_one['Address'].values
	group_two_addr = group_two['Address'].values
	group_three_addr = group_three['Address'].values


	#  calculate the Listings Per Identity by getting the minimum of the three groups and dividing it by the number of identities per race
	LPI         = int(min([len(group_one), len(group_two), len(group_three)])/NUM_IDENTITES_PER_RACE)

	return group_one, group_two, group_three, LPI

def get_day_dict(df_rentals, day_num = 3):
	group_one, group_two, group_three, LPI = get_partitions(df_rentals)
	print('LPI: ' + str(LPI))
	day_trial_dict = {}
	for i in range(1,day_num + 1):
		if i == 1:
			race_dict = {'black': group_one, 'white': group_two, 'hispanic': group_three}
		elif i == 2:
			race_dict = {'black': group_two, 'white': group_three, 'hispanic': group_one}
		else:
			race_dict = {'black': group_three, 'white': group_one, 'hispanic': group_two}
		day_trial_dict.update({i:race_dict})

	return day_trial_dict, LPI

def main():
	if len(sys.argv) != 4:
		print('-------------------------------------------------')
		print('REQUIRED ARGUMENTS:')
		print('python trulia_rental_address_allocator.py <rentals sheet> <timestamp destination> <names sheet (1 or 2).')
		print('-------------------------------------------------')
		print('EXAMPLE:')
		print('python trulia_rental_address_allocator.py round_1/round_3_rentals_1.csv round_3/round_3_timestamps_1.csv 1')
		print('-------------------------------------------------')
		exit()


	if str(sys.argv[3]) != '1' and str(sys.argv[3]) != '2':
		print("Final argument must be a 1 or 2 corresponding to which set of identities to use")
		exit()

	round_directory  = '/home/ubuntu/Housing-Discrimination/rounds/'
	rentals_sheet     = round_directory + str(sys.argv[1])		# csv that contains detailed listing information
	time_status_sheet = round_directory + str(sys.argv[2]) 		# output destination of the schedule csv that is created
	names_sheet       = '/home/ubuntu/Housing-Discrimination/scripts/pre_processing/toxic_names_market_{}.csv'.format(str(sys.argv[3]))            # name_market.csv



	df_rentals = pd.read_csv(rentals_sheet)										# read in csv file
	df_rentals = df_rentals[pd.notnull(df_rentals['Address'])].drop_duplicates(subset = 'Address')			# drop duplicates in address
	print(df_rentals)
	print('csv length: ' + str(len(df_rentals)))
	day_trial_dict, LPI = get_day_dict(df_rentals) 		# day_trial_dict - a dictionary that maps the day to a dictionay which maps a race to a dataframe of address

	df_names, df_status_timestamp = get_dataframes(names_sheet, time_status_sheet,LPI) # initialize dataframes

	inquiry_order = {}																													# inquiry_order - a dictionary that maps an address to the number of occurences 
	loc = 1
	for key, value in day_trial_dict.items():																							# iterate through each key, value pair of day_trial_dict
		day_num = int(key)																												# get the day number													
		for i in range(loc, (LPI * day_num + 1)):																						# iterate from address 1 to address n 
			for index,row in df_status_timestamp.iterrows(): 																			# iterate through the timestamp data frame
				race          = row['racial category']																					# store racial category of current row in dataframe
				rand_row      = day_trial_dict[key][race].sample(n=1) 																	# select a random address 
				rand_row_add  = rand_row['Address'].values[0]																			# strip meta_data
				rand_row_url  = rand_row['URL'].values[0]																				# strip meta_data
				day_trial_dict[key][race] = day_trial_dict[key][race][~day_trial_dict[key][race]['Address'].isin([rand_row_add])]		# remove the address from the dataframe
				if rand_row_add not in inquiry_order: 																					# if the address is not in the inquiry_order dictionary, then add the key 
					inquiry_order.update({rand_row_add:1})
				else: 																													# if the address is, then increment the value 
					inquiry_order[rand_row_add] += 1

				# write it the address and timestamp into the dataframe
				df_status_timestamp.at[index, 'inquiry order ' + str(i)] = str(inquiry_order[rand_row_add]) 						
				df_status_timestamp.at[index,'address ' + str(i)] = '('+ str(rand_row_add) + ', ' + str(rand_row_url) + ')'
			loc += 1

	df_status_timestamp.to_csv(time_status_sheet,mode='w',index=False)

	test_output(df_status_timestamp,(LPI * NUM_RACIAL_GROUPS) + 1)



main()
