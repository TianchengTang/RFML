import os
import time
import xlrd
import csv
import codecs
import re
import difflib

def creat_space():
#create workspace folder
	location = input("Raw Data Location: ")
	
	#path = location + "\\" + "report_" + time.strftime('%d_%m_%y')
	#path = location + "\\" + "report_" + time.strftime('%H_%M_%S')
	path = location
	#os.mkdir(path)
	os.chdir(path)

	return location, path

def qmine(location, path):
#call dataminer to generate report excel file
	limit_choose = input("Choose limit type(leave blank if not sure): ")

	if limit_choose.lower() == "func":
		limit = "Func"
	elif limit_choose.lower() == "std":
		limit = "Func, Std"
	elif limit_choose.lower() == "int":
		limit = "Func, Std, Int"
	elif limit_choose.lower() == "Harsh":
		limit = "Func, Std, Int, Harsh"
	else:
		limit = "Func, Std, Int, Harsh"

	cmd = "dataminer -r " + location + " -o " + path + "\complete_detail.xlsx" + " -ss -sup -lup -lsp -shb -sud -skipDetail -generateSummary -autoFD -autoLD"
	#cmd = "dataminer -r " + location + " -o " + path + "\complete_detail.xlsx" + " -ss -sup -lup -lsp -shb -sud -skipDetail -generateSummary -autoFD -autoLD " + limit
	os.popen(cmd)

	print("Generating Data Sheet...\n")

	while True:
		if os.listdir(path):
			print("Data sheet generated.\n")
			time.sleep(10)
			break

def check_call_status(data_xlsx):
	status_sheet = data_xlsx.sheet_by_name("Call Status")
	band_list = status_sheet.col_values(3)[5:]
	items = status_sheet.col_values(0)[5:]
	result = status_sheet.col_values(33)[5:]
	bands = list(set(band_list))

	call_status = []
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
		elif 1.122<=score < 2.222:
			call_status.append(i)
			call_status.append("Registration Success but Call Failed")
		elif 1.111<=score<1.122:
			call_status.append(i)
			call_status.append("Registration Failed, Call Failed")
	print(call_status)
	return call_status

def get_basic_info(data_xlsx):
#generate csv file for each sheet in excel file


	test_info = data_xlsx.sheet_by_name("TestRunInfo")
	DUT_SW_Build = list(set(test_info.col_values(3)[1:]))[0]
	DUT_HW_ID= list(set(test_info.col_values(1)[1:]))[0]
	Station_ID = list(set(test_info.col_values(4)[1:]))[0]
	Date = test_info.col_values(5)[1]
	DLL_Name = list(set(test_info.col_values(10)[1:]))[0]
	DLL_Version = list(set(test_info.col_values(11)[1:]))[0]
	Test_Tree_list = test_info.col_values(7)[1:]


	#generate uuid for this data entry

	reshape = re.findall(r"\d+", test_info.col_values(5)[1]) + re.findall(r"\d+", test_info.col_values(6)[1])
	uuid = "".join(reshape)

	return DUT_SW_Build, DUT_HW_ID, Station_ID, Date, DLL_Name, DLL_Version, uuid

def generate_csv(sheets, DUT_SW_Build, DUT_HW_ID, Station_ID, Date, DLL_Name, DLL_Version, uuid, call_status):
	#get all data sheet

	
	for i in sheets[1:]:
		table = data_xlsx.sheet_by_name(i)
		title = table.row_values(4)
		bands = table.col_values(title.index("Band"))[5:]
		call_status_column = []
		for j in bands:
			p = call_status.index(j)
			call_status_column.append(call_status[p+1])
	
		s = '{sheet}.csv'
		with codecs.open(s.format(sheet = i), 'w', encoding= 'utf-8') as file:
			write = csv.writer(file)
			for row_num in range(table.nrows):
				if row_num > 4:
					row_value = table.row_values(row_num)
					row_value.insert(0, uuid)
					row_value.insert(1, DUT_SW_Build)
					row_value.insert(2, DUT_HW_ID)
					row_value.insert(3, Station_ID)
					row_value.insert(4, Date)
					row_value.insert(5, DLL_Name)
					row_value.insert(6, DLL_Version)
					row_value.insert(7, call_status_column[row_num-5])
					del row_value[-16:-1]
					write.writerow(row_value)
	

	print("csv files generated.")

def load_sheet(path):
#get sheets from excel file	
	file_name = os.listdir(path)
	try:
		data_xlsx = xlrd.open_workbook(file_name[0])
	except:
		print("Cannot open excel file. Please check data sheet.\n")
		exit()
	else:	
		sheets = []
		for sheet in data_xlsx.sheets():
			if sheet.merged_cells:
				sheets.append(sheet.name)
	
	return data_xlsx, sheets


if __name__ == '__main__':
#main function

	location, path = creat_space()
	#qmine(location, path)
	data_xlsx, sheets = load_sheet(path)
	call_status = check_call_status(data_xlsx)
	DUT_SW_Build, DUT_HW_ID, Station_ID, Date, DLL_Name, DLL_Version, uuid = get_basic_info(data_xlsx)
	generate_csv(sheets, DUT_SW_Build, DUT_HW_ID, Station_ID, Date, DLL_Name, DLL_Version, uuid, call_status)

