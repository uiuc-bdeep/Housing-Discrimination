import xlwt
import xlrd
from xlutils.copy import copy
import pandas as pd
import datetime
import os
from tqdm import tqdm

print()

# delete old survey files if necessary
output_files = [f for f in os.listdir('output') if not f.startswith('.')]
if output_files:
	for output_file in tqdm(output_files, desc="Deleting Old Survey Files", bar_format="{l_bar}{bar}|  {n_fmt}/{total_fmt}   "):
		os.remove(os.getcwd() + '/output/' + output_file)
	print()

# find input files
TIMESTAMP_FILE = None
TEMPLATE_FILE = None
input_files = [f for f in os.listdir('input') if not f.startswith('.')]
for input_file in input_files:
	if ".csv" in input_file:
		TIMESTAMP_FILE = input_file
	if ".xls" in input_file:
		TEMPLATE_FILE = input_file

names = [
		['Jalen','Jackson'],
		['Lamar','Williams'],
		['DaQuan','Robinson'],
		['Nia','Harris'],
		['Ebony','James'],
		['Shanice','Thomas'],
		['Caleb','Peterson'],
		['Charlie','Myers'],
		['Ronnie','Miller'],
		['Aubrey','Murphy'],
		['Erica','Cox'],
		['Leslie','Wood'],
		['Jorge','Rodriguez'],
		['Pedro','Sanchez'],
		['Luis','Torres'],
		['Isabella','Lopez'],
		['Mariana','Morales'],
		['Jimena','Ramirez']
	]

currentDate = datetime.date.today()
month, day, year = str(currentDate.month), str(currentDate.day), str(currentDate.year)

df = pd.read_csv(os.getcwd() + '/input/' + TIMESTAMP_FILE)
cols = df.columns.tolist()
new_cols = cols[:9]
num_addresses = int(cols[-1].split(' ')[-1])
for i in range(1, num_addresses + 1):
	for first,last in names:
		if str(df.loc[df['first name'] == first,'address ' + str(i)].values[0]).lower() == 'nan':
			df.loc[df['first name'] == first,'address ' + str(i)] = None
		else: 
			#df.loc[df['first name'] == first,'address ' + str(i)] = df.loc[df['first name'] == first,'address ' + str(i)].values[0].split(',')[0].split('(')[1]
                        loc = df.loc[df['first name'] == first,'address ' + str(i)]
                        if(len(loc.values[0].split(',')) == 2):
                            df.loc[df['first name'] == first,'address ' + str(i)] = df.loc[df['first name'] == first,'address ' + str(i)].values[0].split(',')[0].split('(')[1]
                        else:
                            df.loc[df['first name'] == first,'address ' + str(i)] = "(" + df.loc[df['first name'] == first,'address ' + str(i)].values[0].split(',')[0][1:-3] + ") " + df.loc[df['first name'] == first,'address ' + str(i)].values[0].split(',')[1]

	new_cols.append('address ' + str(i))
df = df[new_cols]

file = xlrd.open_workbook(os.getcwd() + '/input/' + TEMPLATE_FILE)

for name in tqdm(names, desc="Writing New Survey Files", bar_format="{l_bar}{bar}|  {n_fmt}/{total_fmt}   "):
	myFile = copy(file)
	# get list of addresses for a specific person
	df_upper = df.loc[(df['first name'] == name[0]) & (df['last name'] == name[1])]
	df_upper = df_upper.reset_index(drop=True)
	df_upper = df_upper[df_upper.columns.tolist()[9:]]
	addresses = list(set(df_upper.iloc[0,:]))
	addresses = [x for x in addresses if (str(x) != 'nan' and x != None)]

	# create dataframe that is basically the first half of the 2nd sheet of the xls sheet
	df_upper = pd.DataFrame(index=range(1+len(addresses)), columns=['list name', 'name', 'label'])
	df_upper['list name'][0] = 'people_name'
	df_upper['name'][0] = name[0] + ' ' + name[1]
	df_upper['label'][0] = name[0] + ' ' + name[1]
	for i in range(len(addresses)):
		df_upper['list name'][i+1] = 'address_name'
		df_upper['name'][i+1] = addresses[i]
		df_upper['label'][i+1] = addresses[i]

	# create dataframe that is basically the second half of the 2nd sheet of the xls sheet
	sheet_2 = file.sheet_by_index(1)
	num_rows = sheet_2.nrows - 1 # nrows includes header row
	df_lower = pd.DataFrame(index=range(num_rows), columns=['list name', 'name', 'label'])
	for i in range(num_rows):
		df_lower['list name'][i] = sheet_2.row(i+1)[0].value
		df_lower['name'][i] = sheet_2.row(i+1)[1].value
		df_lower['label'][i] = sheet_2.row(i+1)[2].value

	# merge the dataframes together
	df_final = df_upper.append(df_lower, ignore_index=True)

	# overwrite the 2nd sheet with new name and addresses
	s = myFile.get_sheet(1)
	for i in range(len(df_final)):
		s.write(i+1, 0, df_final['list name'][i])
		s.write(i+1, 1, df_final['name'][i])
		s.write(i+1, 2, df_final['label'][i])
	
	# overwrite values in 3rd sheet
	s = myFile.get_sheet(2)
	s.write(1, 0, name[0] + '_' + name[1] + '_survey')		# title
	s.write(1, 1, name[0] + '_' + name[1] + '_survey_1_1_3')	# id string

	fileName = name[0]+'-'+name[1]+'_'+month+'_'+day+'_'+year+'.xls'

	myFile.save(os.getcwd() + '/output/' + fileName)

print()
