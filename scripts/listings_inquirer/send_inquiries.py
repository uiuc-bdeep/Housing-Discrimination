import sys
from time import sleep

from handle_listing_page import send_message
from handle_input_data import get_LPI,get_dataframes,get_row_info
from handle_webdriver import start_firefox,restart

def print_progress(handled_state,LPI,parameter_day_trial,person_id,name):
	print("HANDLING STATE : " + str(handled_state) + '/' + str(LPI * parameter_day_trial) + '\n' +
		  str(person_id) + '. ' + str(name) + '\n' + '---------------------------------')

def main():
        if len(sys.argv) != 3 and len(sys.argv) != 4:
            print('-------------------------------------------------')
            print('REQUIRED ARGUMENTS:')
            print('python send_inquiries.py <path_to_timestamp_file> <Day (1, 2, or 3)> <Send (0 or 1) (Default = 1)>')
            print('-------------------------------------------------')
            print('EXAMPLE - SENDING OUT ROUND 2 DAY 3')
            print('python send_inquiries.py ../../rounds/round_2/round_2_timestamps_1.csv 3 1')
            print('-------------------------------------------------')
            exit()

	time_status_sheet   = sys.argv[1]  # timestamp output csv
	parameter_day_trial = int(sys.argv[2])  # tests are split into three days. Each unique listing is sent and inquiry each day.
        parameter_send      = 1
        if len(sys.argv) == 4:
	    parameter_send = int(sys.argv[3])  # can be a value of 0 or 1. 0 will fill out the inquiry form, but will not click the send button. 1 Will click the send button. 

	df_status, LPI = get_dataframes(time_status_sheet)  # get all required dataframes

	driver = start_firefox()
	handled_state = list(df_status['handled'].values)
																																		# find the where the script left off last and set it to row_index
	row_index     = handled_state.index(min(handled_state))
	row           = df_status.iloc[row_index]

	if int(row['handled']) >= (LPI * 3):
		print("Finished sending all addresses\nExiting...\n---------------------------------")
		exit()		 

	handled_state, name, email, phone_num,race, person_id, address, url = get_row_info(row)

	if handled_state < (LPI * parameter_day_trial):
		print_progress(handled_state,LPI,parameter_day_trial,person_id,name)

		if url != None:
			time_stamp     = send_message(driver,name, email, phone_num, address, url,parameter_send)  	# send out the inquiry and return the timestamp of when the inquiry was sent out

			while time_stamp == "RESTART DRIVER":
				print('//////////////////////// RESTART ////////////////////////')
				restart(True,driver)

			if time_stamp == "SOLD" or time_stamp == 'WAITLIST':
				time_stamp = ''
		else:
			print('Is NA')
			time_stamp = ''

		df_status.loc[row_index,'handled'] += 1
		df_status.loc[row_index,'timestamp ' + str(handled_state+1)] = time_stamp

		df_status.to_csv(time_status_sheet,mode='w',index=False)
		print('Timestamp  : ' + str(time_stamp) + '\n' + '---------------------------------')
		sleep(15) #sleep here to add delay between inquiries
		restart(True,driver)
	else:
		print('All names have been handled\nexiting... \n ---------------------------------')
		exit()

if __name__ == '__main__':
	main()
