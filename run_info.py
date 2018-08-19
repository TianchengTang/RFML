import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import itertools
import pymongo

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
        return setup_info


output_array = Get_setup_info(r'S:\User\tangtc\Testlog_analyzer\data\CRM439_sanity\Raw_Data\LTE-B1__3GPP_10MHz_Target_Sanity__Xvc\MAV19 Dev2__ELBOWZ__02May2018_15h25m14s.xml', [])
setup_info = output_array.parse_xml()

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