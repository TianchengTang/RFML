import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import itertools
import pymongo
import os
import glob


def file_finder():
    path = input('Please enter log files location: ')
    folders= os.listdir(path)
    os.chdir(path)
    logs = []
    for folder in folders:
        if os.path.isdir(folder):
            os.chdir(path+'\\'+folder)
            files = glob.glob("*.xml")
            if files:
                logs.append(path+'\\'+folder+'\\'+files[0])
            os.chdir(path)
        elif os.path.isfile(folder):
            files = glob.glob("*.xml")
            if files:
                logs.append(path+'\\'+folder+'\\'+files[0])
            else:
                print("No valid xml log found in this location.")
                exit()
        else:
            print("No valid xml log found in this location.")
            exit()
    return logs

logs = file_finder()

def generate_uuid(logs):

    root = ET.parse(logs[0]).getroot()
    for date in root.iter("Date"):
        month = [i.text for i in date.iter('MM')]
        day = [i.text for i in date.iter('DD')]
        year = [i.text for i in date.iter('YYYY')]
    
        
    for time in root.iter("Time"):
        for start_time in time.iter("Start"):
            hour = [i.text for i in start_time.iter('HH')]
            minute = [i.text for i in start_time.iter('MM')]
            second = [i.text for i in start_time.iter('SS')]
    UUID = str(len(logs))+month[0]+hour[0]+day[0]+minute[0]+year[0]+second[0]

    return UUID
UUID = generate_uuid(logs)

def check_call(log):
    root = ET.parse(log).getroot()
    

class Get_setup_info(object):
    
    def __init__(self, input_file, output_data):
        self.root = ET.parse(input_file).getroot()
        self.output_data = output_data

    def parse_xml(self):
        setup_info = {}
        for date in self.root.iter("Date"):
            month = [i.text for i in date.iter('MM')]
            day = [i.text for i in date.iter('DD')]
            year = [i.text for i in date.iter('YYYY')]
        format_date = month[0]+"."+day[0]+"."+year[0]
        setup_info['Date'] = format_date
        
        
        for station in self.root.iter("Tester"):
            name = [i.text for i in station.iter('Name')]
            
            for sw_config_info in station.iter('SWConfigInfo'):
                DLL = [i.text for i in sw_config_info.iter('N')][0]+'_'+[i.text for i in sw_config_info.iter('V')][0]
        setup_info['Station_ID'] = name[0]
        setup_info['DLL'] = DLL
        

        for uut_info in self.root.iter("UUT"):
            for band in uut_info.iter("Type"):
                Tech_band = band.text
            setup_info['Band'] = Tech_band
            for uutid in uut_info.iter("ID"):
                HW_ID = uutid.text
            setup_info['DUT_HW_ID'] = HW_ID
            for build in uut_info.iter("SWBuildID"):
                SW_Build_ID = build.text
            setup_info['DUT_SW_Build'] = SW_Build_ID
          
        print(setup_info)
        return setup_info, uid


#output_array = Get_setup_info(r'S:\User\tangtc\Testlog_analyzer\data\CRM439_sanity\Raw_Data\LTE-B1__3GPP_10MHz_Target_Sanity__Xvc\MAV19 Dev2__ELBOWZ__02May2018_15h25m14s.xml', [])
#setup_info = output_array.parse_xml()

class db_upload(object):

    def __init__(self, db_name, collection_name):
        self.db_name = db_name
        self.colleciton_name = collection_name
#connect to mongodb 
    def get_db_conn(self):
        db_connect = pymongo.MongoClient('10.63.100.195', 27017)
        db_connect[self.db_name].authenticate('developer', 'Dev1234')
        db = db_connect[self.db_name]
        db_collection = db[self.collection_name]
        return db_collection