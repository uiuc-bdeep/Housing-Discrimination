import xlwt
import xlrd
from xlutils.copy import copy
import pandas as pd
import datetime
import os

TIMESTAMP_FILE = None
files = os.listdir()
for file in files:
	if "timestamp" in file:
		TIMESTAMP_FILE = file

print('\nOld survey files have been deleted.\n')

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

df = pd.read_csv(os.getcwd() + '/' + TIMESTAMP_FILE)
cols = df.columns.tolist()
new_cols = cols[:9]
num_addresses = int(cols[-1].split(' ')[-1])
for i in range(1, num_addresses + 1):
	df['address ' + str(i)] = df['address ' + str(i)].str.split(',', expand=True)[0].str.split('(', expand=True)[1]
	new_cols.append('address ' + str(i))
df = df[new_cols]

df2 = pd.read_csv('other survey stuff.csv')
file = xlrd.open_workbook('test_template.xls')
myFile = copy(file)

for name in names:
	# get list of addresses for a specific person
	df_temp = df.loc[(df['first name'] == name[0]) & (df['last name'] == name[1])]
	df_temp = df_temp.reset_index(drop=True)
	df_temp = df_temp[df_temp.columns.tolist()[9:]]
	addresses = list(df_temp.iloc[0,:])

	# create dataframe that is basically the 2nd sheet of the xls sheet
	df_temp = pd.DataFrame(index=range(1+len(addresses)), columns=['list name', 'name', 'label'])
	df_temp['list name'][0] = 'people_name'
	df_temp['name'][0] = name[0] + ' ' + name[1]
	df_temp['label'][0] = name[0] + ' ' + name[1]
	for i in range(len(addresses)):
		df_temp['list name'][i+1] = 'address_name'
		df_temp['name'][i+1] = addresses[i]
		df_temp['label'][i+1] = addresses[i]
	df_temp = df_temp.append(df2, ignore_index=True)

	# overwrite the 2nd sheet with new name and addresses
	s = myFile.get_sheet(1)
	for i in range(len(df_temp)):
		s.write(i+1, 0, df_temp['list name'][i])
		s.write(i+1, 1, df_temp['name'][i])
		s.write(i+1, 2, df_temp['label'][i])
	
	# overwrite values in 3rd sheet
	s = myFile.get_sheet(2)
	s.write(1, 0, name[0] + '_' + name[1] + '_survey')		# title
	s.write(1, 1, name[0] + '_' + name[1] + '_survey_1_1')	# id string

	fileName = 'TX_'+name[0]+'-'+name[1]+'_'+month+'_'+day+'_'+year+'.xls'

	myFile.save(os.getcwd() + '/surveys/' + fileName)

	print(fileName + ' has been written.')

print()
