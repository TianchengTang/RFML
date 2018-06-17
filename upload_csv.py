import pymysql as pl
import csv
import codecs
import os
import xlrd
import traceback


def get_file():
	path = input("Data Location: ")
	os.chdir(path)
	filename = os.listdir(path)
	return filename


def get_conn():
	db = pl.connect(host = 'localhost', port = 3306, user = 'root', passwd = 'Q064TestMan0227', db = 'mav19')
	return db

def load_calver_to_mysql(filename):
	column_name_list = ''

	with codecs.open(filename= filename, mode = 'rb', encoding = 'utf-8') as f:
		file = csv.reader(f)
		db = get_conn()
		cursor = db.cursor()
		cursor.execute('SELECT DATA_TYPE FROM information_schema.columns WHERE table_schema = \'mav19\' AND table_name = \'calver\';')
		data_type = cursor.fetchall()
		col_types = []
		db_col_types = []
		for i in data_type:
			if i[0] == 'varchar' or i[0] == 'char':
				col_types.append(str)
				db_col_types.append('\'%s\'')
			elif i[0] == 'int':
				col_types.append(int)
				db_col_types.append('\'%d\'')
			elif i[0] == 'float':
				col_types.append(float)
				db_col_types.append('\'%d\'')
		
		
		cursor.execute('SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = \'mav19\' AND table_name = \'calver\';')
		column_name = cursor.fetchall()
		for i in range(len(column_name)):
			column_name_list.join(column_name[i][0])
		print(column_name_list)
		
		command = "INSERT INTO calver("+column_name_list+") VALUES (" + ', '.join(db_col_types)+ ")"

		try:
			for row in file:
				row[9] = row[9].replace('.0', '')
				row[10] = row[10].replace('.0', '')
				row[11] = row[11].replace('.0', '')

				row = tuple(convert(value) for convert, value in zip(col_types, row))
		
				cursor.execute(command %(row))
				
			print("success!")
				
		except:
			traceback.print_exc()
			db.rollback()
			print("something went wrong...")
		
		db.commit()
		db.close()

def load_3gpp_to_mysql(filename, tablename):
	column_name_list = ''

	with codecs.open(filename= filename, mode = 'rb', encoding = 'utf-8') as f:
		file = csv.reader(f)
		db = get_conn()
		cursor = db.cursor()
		cursor.execute('SELECT DATA_TYPE FROM information_schema.columns WHERE table_schema = \'mav19\' AND table_name = \'tx_power\';')
		data_type = cursor.fetchall()
		col_types = []
		db_col_types = []
		for i in data_type:
			if i[0] == 'varchar' or i[0] == 'char':
				col_types.append(str)
				db_col_types.append('\'%s\'')
			elif i[0] == 'int':
				col_types.append(int)
				db_col_types.append('\'%d\'')
			elif i[0] == 'float':
				col_types.append(float)
				db_col_types.append('\'%d\'')
		
		
		cursor.execute('SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = \'mav19\' AND table_name = \'tx_power\';')
		column_name = cursor.fetchall()
		for i in range(len(column_name)):
			column_name_list.join(column_name[i][0])


		command = "INSERT INTO tx_power("+column_name_list+") VALUES (" + ', '.join(db_col_types)+ ")"


		try:
			for row in file:
				row[12] = row[12].replace('.0', '')
				row[14] = row[14].replace('.0', '')
				row[11] = row[11].replace('.0', '')
				row[13] = row[13].replace('.0', '')
				row[16] = row[16].replace('.0', '')

				row = tuple(convert(value) for convert, value in zip(col_types, row))
		
				cursor.execute(command %(row))
				
			print("success!")
				
		except:
			traceback.print_exc()
			db.rollback()
			print("something went wrong...")
		
		db.commit()
		db.close()

if __name__ == '__main__':
	filename = get_file()
	for i in filename:
		#if i == "CalVer.csv":
		#	load_calver_to_mysql(i)
		if i == "Tx Power.csv":
			load_3gpp_to_mysql(i, "tx_power")