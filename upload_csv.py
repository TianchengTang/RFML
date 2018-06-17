import pymongo
import mongoengine
import csv
import json
import os
import pandas
import traceback


def get_file():
#get data file
	path = input("Data Location: ")
	os.chdir(path)
	filename = os.listdir(path)
	return filename


def get_db_conn():
#connect to mongodb remotely
	db_connect = pymongo.MongoClient('10.63.100.195', 27017)
	db_connect['TestMan001'].authenticate('developer', 'Dev1234')
	db = db_connect['TestMan001']
	return db

def load_csv_to_mysql(filename, collection):
#load csv file to collection
	db_collection = db[collection]
	data = pandas.read_csv(filename)
	data_json = json.loads(data.to_json(orient='records'))
	db_collection.insert(data_json)


if __name__ == '__main__':
	db = get_db_conn()
	filename = get_file()
	for i in filename:
		if i[-3:] == 'csv':
			load_csv_to_mysql(i, i[:-4])