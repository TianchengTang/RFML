import os
import time
import xlrd
import csv
import codecs
import re

def creat_space():
#create workspace folder
	location = input("Raw Data Location: ")
	
	path = location + "\\" + "report_" + time.strftime('%d_%m_%y')
	#path = location + "\\" + "report_" + time.strftime('%H_%M_%S')
	os.mkdir(path)
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



def get_uuid(data_xlsx):
#generate uuid for this data entry
	test_info = data_xlsx.sheet_by_name("TestRunInfo")
	
	reshape = re.findall(r"\d+", test_info.col_values(5)[1]) + re.findall(r"\d+", test_info.col_values(6)[1])
	uuid = "".join(reshape)

	return uuid

def generate_csv(sheets, uuid):
#generate all data sheet

	
	for i in sheets[1:]:
		table = data_xlsx.sheet_by_name(i)
		title = table.row_values(4)
		
	
		s = '{sheet}.csv'
		with codecs.open(s.format(sheet = i), 'w', encoding= 'utf-8') as file:
			write = csv.writer(file)
			for row_num in range(table.nrows):
				if row_num == 3:
					row_value = table.row_values(4)
					row_value.insert(0, "UUID")
					del row_value[-16:-1]
					write.writerow(row_value)
				elif row_num > 4:
					row_value = table.row_values(row_num)
					row_value.insert(0, uuid)
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
	qmine(location, path)
	data_xlsx, sheets = load_sheet(path)
	uuid = get_uuid(data_xlsx)
	generate_csv(sheets, uuid)

