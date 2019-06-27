import os
import pandas as pd


def get_LPI(df_timestamp):
	df_headers = list(df_timestamp.columns)
	LPI        = len(df_headers[9:])/9   # Div by 3 (for address x timestamp x inquiry order x and) * 3 (for number of racial categories)
	return int(LPI)

def get_dataframes(status):
	df_timestamp = pd.read_csv(status)
	LPI          = get_LPI(df_timestamp)

	return df_timestamp,LPI

def get_row_info(row):
	handled_state = int(row['handled'])
	name          = row['first name'] + ' ' + row['last name']
	email         = row['email']
	phone_num     = row['phone number']
	race          = row['racial category']
	person_id     = row['person id']

	if str(row['address ' + str(handled_state + 1)]) == 'nan':
		address = None
		url     = None
	else:
            if(len(row['address ' + str(handled_state + 1)].split(',')) == 3):
                address       = row['address ' + str(handled_state + 1)].split(',')[1]
                url           = str(row['address ' + str(handled_state + 1)].split(',')[2][:-1])
            else:
                address       = row['address ' + str(handled_state + 1)].split(',')[0][1:]
                url           = str(row['address ' + str(handled_state + 1)].split(',')[1][:-1])


	return handled_state, name, email, phone_num, race, person_id, address, url
