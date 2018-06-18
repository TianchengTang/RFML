import pymongo
import mongoengine
import os
import xlrd
import glob
import sys
import re
import json

def get_file():
#get raw data file
	location = input("Data Location: ")
	os.chdir(location)

	filename = glob.glob('*.xlsx')[0]
	try:
		book = xlrd.open_workbook(filename)
	except:
		print("Cannot open excel. Please check data file.\n")
		exit()
	else:
		print("Data acquired, start analyzing data...\n")

	sheets = []
	for sheet in book.sheets():
		if sheet.merged_cells:
			sheets.append(sheet.name)
	return book, sheets


def get_range(sheet_name, total_test):
#get limits from data sheet
	table = book.sheet_by_name(sheet_name)
	title = table.row_values(4)
	mean_value = table.col_values(title.index("Mean"))[5:]
	total_test += len(mean_value)
	#status = table.col_values(title.index("Status"))[5:]

	try:
		Func_Min = table.col_values(title.index("Func Min"))[5:]
	except:
		Func_Min = []
	try:
		Func_Max = table.col_values(title.index("Func Max"))[5:]
	except:
		Func_Max = []
	try:
		Std_Min = table.col_values(title.index("Std Min"))[5:]
	except:
		Std_Min = []
	try:
		Std_Max = table.col_values(title.index("Std Max"))[5:]
	except:
		Std_Max = []
	try:
		Int_Min = table.col_values(title.index("Int Min"))[5:]
	except:
		Int_Min = []
	try:
		Int_Max = table.col_values(title.index("Int Max"))[5:]
	except:
		Int_Max = []
	try:
		Harsh_Min = table.col_values(title.index("Harsh Min"))[5:]
	except:
		Harsh_Min = []
	try:
		Harsh_Max = table.col_values(title.index("Harsh Max"))[5:]
	except:
		Harsh_Max = []

	if sheet_name == 'CalVer':
		Harsh_Max = []
		Harsh_Min = []

	limits = [Func_Min, Func_Max, Std_Min, Std_Max, Int_Min, Int_Max, Harsh_Min, Harsh_Max]

	return total_test, limits, mean_value


def compare_result(mean_value, limits):
#compare measured data with different limits to get result
	Func_fail = 0
	Std_fail = 0
	Int_fail = 0
	Harsh_fail = 0
	pass_count = 0
	dataNA_count = 0

	Func_Min = limits[0]
	Func_Max = limits[1]
	Std_Min = limits[2]
	Std_Max = limits[3]
	Int_Min = limits[4]
	Int_Max = limits[5]
	Harsh_Min = limits[6]
	Harsh_Max = limits[7]

	if len(Harsh_Min) == 0 and len(Harsh_Max) == 0:
		noHarsh_limit = 1
	else:
		noHarsh_limit = 0

	if len(Int_Min) == 0 and len(Int_Max) == 0: 
		noInt_limit = 1
	else:
		noInt_limit = 0

	if len(Std_Min) == 0 and len(Std_Max) == 0: 
		noStd_limit = 1
	else:
		noStd_limit = 0

	if len(Func_Min) == 0 and len(Func_Max) == 0: 
		noFunc_limit = 1
	else:
		noFunc_limit = 0

	missLimit = 0

	def Harsh_comp(pass_count, Harsh_fail, missLimit_count, noHarsh_limit):
		if noHarsh_limit == 0:

			if Harsh_Min[i] == '' and Harsh_Max[i] != '': #case2: missing min part of harsh limit
				if Harsh_Max[i] < mean_value[i]:
					Harsh_fail  += 1

				elif Harsh_Max[i] >= mean_value[i]:
					pass_count += 1
			elif Harsh_Min[i] != '' and Harsh_Max[i] == '': #case3: missing max part of harsh limit
				if Harsh_Min[i] > mean_value[i]:
					Harsh_fail += 1
					
				elif Harsh_Min[i] <= mean_value[i]:
					pass_count += 1
			elif Harsh_Min[i] != '' and Harsh_Max[i] != '': #case4: normal compare
				if Harsh_Min[i] <= mean_value[i] and Harsh_Max[i] >= mean_value[i]:
					pass_count += 1
				else:
					Harsh_fail += 1
			elif Harsh_Min[i] == '' and Harsh_Max[i] == '':
				missLimit_count += 1
				pass_count += 1
			else:
				print("Exception found for Harsh limit compare.")
		else:
			pass_count += 1
		return pass_count, Harsh_fail, missLimit_count

	def Int_comp(pass_count, Harsh_fail, Int_fail, missLimit_count, noHarsh_limit, noInt_limit):
		if noInt_limit == 0:
			if Int_Min[i] == '' and Int_Max[i] != '': 
				if Int_Max[i] < mean_value[i]:
					Int_fail  += 1
					
				elif Int_Max[i] >= mean_value[i]:
					pass_count, Harsh_fail, missLimit_count = Harsh_comp(pass_count, Harsh_fail, missLimit_count, noHarsh_limit)
			elif Int_Min[i] != '' and Int_Max[i] == '': 
				if Int_Min[i] > mean_value[i]:
					Int_fail += 1
					
				elif Int_Min[i] <= mean_value[i]:
					pass_count, Harsh_fail, missLimit_count = Harsh_comp(pass_count, Harsh_fail, missLimit_count, noHarsh_limit)
			elif Int_Min[i] != '' and Int_Max[i] != '': 
				if Int_Min[i] <= mean_value[i] and Int_Max[i] >= mean_value[i]:
					pass_count, Harsh_fail, missLimit_count = Harsh_comp(pass_count, Harsh_fail, missLimit_count, noHarsh_limit)
				else:
					Int_fail += 1
			elif Int_Min[i] == '' and Int_Max[i] == '':
				missLimit_count += 1
				pass_count, Harsh_fail, missLimit_count = Harsh_comp(pass_count, Harsh_fail, missLimit_count, noHarsh_limit)
			else:
				print("Exception found for Int limit compare.")
		else:
			pass
		return pass_count, Harsh_fail, Int_fail, missLimit_count	

	def Std_comp(pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count, noHarsh_limit, noInt_limit, noStd_limit):
		if noStd_limit == 0:
			if Std_Min[i] == '' and Std_Max[i] != '': 
				if Std_Max[i] < mean_value[i]:
					Std_fail  += 1
					
				elif Std_Max[i] >= mean_value[i]:
					pass_count, Harsh_fail, Int_fail, missLimit_count = Int_comp(pass_count, Harsh_fail, Int_fail, missLimit_count, noHarsh_limit, noInt_limit)
			elif Std_Min[i] != '' and Std_Max[i] == '': 
				if Std_Min[i] > mean_value[i]:
					Std_fail += 1
					
				elif Std_Min[i] <= mean_value[i]:
					pass_count, Harsh_fail, Int_fail, missLimit_count = Int_comp(pass_count, Harsh_fail, Int_fail, missLimit_count, noHarsh_limit, noInt_limit)
			elif Std_Min[i] != '' and Std_Max[i] != '': 
				if Std_Min[i] <= mean_value[i] and Std_Max[i] >= mean_value[i]:
					pass_count, Harsh_fail, Int_fail, missLimit_count = Int_comp(pass_count, Harsh_fail, Int_fail, missLimit_count, noHarsh_limit, noInt_limit)
				else:
					Std_fail += 1
			elif Std_Min[i] == '' and Std_Max[i] == '':
				missLimit_count += 1
				pass_count, Harsh_fail, Int_fail, missLimit_count = Int_comp(pass_count, Harsh_fail, Int_fail, missLimit_count, noHarsh_limit, noInt_limit)
			else:
				print("Exception found for Std limit compare.")
		else:
			pass
		return pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count
	
	def Func_comp(pass_count, Harsh_fail, Int_fail, Std_fail, Func_fail, missLimit_count, noHarsh_limit, noInt_limit, noStd_limit, noFunc_limit):
		if noFunc_limit == 0:
			if Func_Min[i] == '' and Func_Max[i] != '': 
				if Func_Max[i] < mean_value[i]:
					Func_fail  += 1
					
				elif Func_Max[i] >= mean_value[i]:
					pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count = Std_comp(pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count,noHarsh_limit, noInt_limit, noStd_limit)
			elif Func_Min[i] != '' and Func_Max[i] == '': 
				if Func_Min[i] > mean_value[i]:
					Func_fail += 1
					
				elif Func_Min[i] <= mean_value[i]:
					pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count = Std_comp(pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count, noHarsh_limit, noInt_limit, noStd_limit)
			elif Func_Min[i] != '' and Func_Max[i] != '': 
				if Func_Min[i] <= mean_value[i] and Func_Max[i] >= mean_value[i]:
					pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count = Std_comp(pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count, noHarsh_limit, noInt_limit, noStd_limit)
				else:
					Func_fail += 1
			elif Func_Min[i] == '' and Func_Max[i] == '':
				missLimit_count += 1
				pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count = Std_comp(pass_count, Harsh_fail, Int_fail, Std_fail, missLimit_count, noHarsh_limit, noInt_limit, noStd_limit)
			else:
				print("Exception found for Func limit compare.")
		else:
			pass		
		return pass_count, Harsh_fail, Int_fail, Std_fail, Func_fail, missLimit_count	

	for i in range(len(mean_value)):
		missLimit_count = 0

		if mean_value[i] >= 900 or mean_value[i] <= -900:
				dataNA_count += 1
		else:
			pass_count, Harsh_fail, Int_fail, Std_fail, Func_fail, missLimit_count = Func_comp(pass_count, Harsh_fail, Int_fail, Std_fail, Func_fail, missLimit_count, noHarsh_limit, noInt_limit, noStd_limit, noFunc_limit)
		
		if missLimit_count == 4:
			missLimit += 1
			pass_count -= 1



	results = [Func_fail, Std_fail, Int_fail, Harsh_fail, noFunc_limit, noStd_limit, noInt_limit, noHarsh_limit, missLimit, pass_count, dataNA_count]
	return results

'''
def call_status(sheet_name):
	table = book.sheet_by_name(sheet_name)
	title = table.row_values(4)
	mean_value = table.col_values(title.index("Mean"))[5:]
	testcase = table.col_values(title.index("Result"))[5:]
	band = table.col_values(title.index("Band"))[5:]
	call_setup = []
	for i in range(len(testcase)):
		if testcase[i] == "Registration Failures":
			if mean_value[i] == 0.0:
				continue
			else:
				call_setup.append("Band "+ str(int(band[i]))+" registration failed.")
		elif testcase[i] == "Registration - Final Status":
			if mean_value[i] == 1.0:
				continue
			else:
				if "Band "+str(int(band[i]))+" registration failed." not in call_setup:
					call_setup.append("Band "+ str(int(band[i])) +" registration failed.")
				else:
					continue
		elif testcase[i] == "Start Call Failures":
			if mean_value[i] == 0.0:
				continue
			else:
				call_setup.append("Band "+ str(int(band[i])) + " start call failed.")
		elif testcase[i] == "Start Call - Final Status":
			if mean_value[i] == 1.0:
				continue
			else:
				if "Band "+ str(int(band[i])) + " start call failed." not in call_setup:
					call_setup.append("Band "+ str(int(band[i])) + " start call failed.")
				else:
					continue
		elif testcase[i] == "Handover Success":
			if mean_value[i] == 1.0:
				continue
			else:
				call_setup.append("Band "+ str(int(band[i])) + " handover failed.")
		elif testcase[i] == "Handover - Final Status":
			if mean_value[i] == 1.0:
				continue
			else:
				if "Band "+ str(int(band[i])) + " handover failed." not in call_setup:
					call_setup.append("Band "+ str(int(band[i])) + " handover failed.")
				else:
					continue
	return call_setup
	print(call_setup)
'''

def check_call_status(data_xlsx):
#check call status for each band
	status_sheet = data_xlsx.sheet_by_name("Call Status")
	band_list = status_sheet.col_values(3)[5:]
	items = status_sheet.col_values(0)[5:]
	result = status_sheet.col_values(33)[5:]
	bands = [int(i) for i in list(set(band_list))]

	call_status = []
	call_fail = []
	registration_fail = []
	test_skip = []
	for i in bands:
		score = 0
		for j in range(len(band_list)):
			if band_list[j] == i:
				 if items[j] == "Registration Failures":
				 	if result[j] == 0.0:
				 		score+=0.002
				 	else:
				 		score+=0.001
				 elif items[j] == "Registration - Final Status":
				 	if result[j] == 1.0:
				 		score+=0.02
				 	else:
				 		score+=0.01
				 elif items[j] == "Start Call Failures":
				 	if result[j] == 0.0:
				 		score+=0.2
				 	else:
				 		score+=0.1
				 elif items[j] == "Start Call - Final Status":
				 	if result[j] == 1.0:
				 		score+=2
				 	else:
				 		score+=1
		if score == 2.222:
			call_status.append(i)
			call_status.append("Call Success")
		elif score <= 0.011:
			call_status.append(i)
			call_status.append("Registration Failed, Test Skipped")
			test_skip.append(i)
		elif 1.122<=score < 2.222:
			call_status.append(i)
			call_status.append("Registration Success but Call Failed")
			call_fail.append(i)
		elif 1.111<=score<1.122:
			call_status.append(i)
			call_status.append("Registration Failed, Call Failed")
			registration_fail.append(i)


	
	return call_status, call_fail, registration_fail, test_skip


def get_db_conn():
#connect to mongodb remotely
	db_connect = pymongo.MongoClient('10.63.100.195', 27017)
	db_connect['TestMan001'].authenticate('developer', 'Dev1234')
	db = db_connect['TestMan001']
	db_collection = db['Summary']
	return db_collection


def prepare_data(book):
#gather general data for upload

	test_info = book.sheet_by_name("TestRunInfo")
	DUT_SW_Build = list(set(test_info.col_values(3)[1:]))[0]
	DUT_HW_ID = list(set(test_info.col_values(1)[1:]))[0]
	Station_ID = list(set(test_info.col_values(4)[1:]))[0]
	Date = test_info.col_values(5)[1]
	DLL_Name = list(set(test_info.col_values(10)[1:]))[0]
	DLL_Version = list(set(test_info.col_values(11)[1:]))[0]
	DLL = DLL_Name + "_" + DLL_Version
	
	reshape = re.findall(r"\d+", test_info.col_values(5)[1]) + re.findall(r"\d+", test_info.col_values(6)[1])
	uuid = "".join(reshape)
	upload = {}
	upload["Basic Info"] = {'UUID': uuid, 'DUT_SW_Build': DUT_SW_Build, 'DUT_HW_ID': DUT_HW_ID, 'Station_ID': Station_ID, 'Date': Date, 'DLL': DLL}

	return upload



if __name__ == '__main__':
	book, sheets = get_file()
	db_collection = get_db_conn()
	#initiate 

	total_pass = 0
	total_fail = 0
	total_null = 0
	total_test = 0
	result = []
	upload = prepare_data(book)

	for i in sheets[1:]:
	
		section_result = []
			
		total_test, limits, mean_value = get_range(i, total_test)
		section_result = compare_result(mean_value, limits)
			
			
		section_fail = section_result[0] + section_result[1] + section_result[2] + section_result[3]
		section_test = len(mean_value)

		#results = [Func_fail, Std_fail, Int_fail, Harsh_fail, noFunc_limit, noStd_limit, noInt_limit, noHarsh_limit, missLimit, pass_count, dataNA_count]
		upload[i] = {'test_name': i, 'test_count': section_test, 'pass_count': section_result[9], 'fail_count': section_fail, 'Func_fail': section_result[0], 'Std_fail': section_result[1], 'Int_fail': section_result[2], 'Harsh_fail': section_result[3], 'null_count': section_result[8], 'dataNA_count': section_result[10]}
		

	call_status, call_fail, registration_fail, test_skip = check_call_status(book)
	upload["Call Fail"] = call_fail
	upload["Registration Fail"] = registration_fail
	upload["Test skipped"] = test_skip

	data_json = json.dumps(upload)
	data_json = json.loads(data_json)

	db_collection.insert(data_json)
	print("upload suscess!")
