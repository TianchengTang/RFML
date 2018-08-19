import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import itertools
import pymongo

class XML_processor:
    def __init__(self, folder_path=None):
        self.folder = folder_path
        self.data = []

    def result_generation_helper(self, xml):
        root = ET.parse(xml).getroot()

        # Initialize a dict of lists for storing test results
        # test results are initially collected as dict[list[dict]]
        test_results = defaultdict(list)

        for collection in root.iter('TestCollection'):
            # Typically the file only contains one collection
            for test in collection.findall('Test'):
                # looping through all test result collections
                # each test has to have a name
                testarea = test.find('Name').text.rstrip()
                for ds_collection in test.findall('DataSetCollection'):
                    # looping through each test case in test collection
                    # may not exist
                    collection_name = ds_collection.find('Name')

                    # store result in each test case in a dict
                    temp = defaultdict()

                    for d in ds_collection.iter('DI'):
                        n, v = d.find('N'), d.find('V')
                        temp[n.text] = v.text

                    # attempt to use collection name
                    # if not successful, it is an input section
                    if collection_name is not None:
                        test_results[testarea +' ' + collection_name.text].append(temp)
                    else:
                        test_results[testarea + ' Inputs'].append(temp)

        # Given test_results in form dict[list[dict]]: testcase -> list of occurrences -> KPI
        # Transform to dict[dict[list]]: testcase -> KPI -> list of results
        final_res = defaultdict(list)
        for testcase in test_results:
            # KPI -> list of results
            d = defaultdict(list)
            for it in test_results[testcase]:
                for kpi in it:
                    d[kpi].append(it[kpi])
            final_res[testcase].append(d)
        self.data.append(final_res)

    def collect_data(self):
        if self.folder is None:
            self.folder = input()
        for xml_file in Path(self.folder).glob('*.xml'):
            self.result_generation_helper(xml_file)
            
                
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
        
        for time in self.root.iter("Time"):
            for start_time in time.iter("Start"):
                hour = [i.text for i in start_time.iter('HH')]
                minute = [i.text for i in start_time.iter('MM')]
                second = [i.text for i in start_time.iter('SS')]
        UUID = month[0]+hour[0]+day[0]+minute[0]+year[0]+second[0]
        print(UUID)
        
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


<<<<<<< HEAD
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
=======
output_array = Get_test_info(r'S:\User\tangtc\Testlog_analyzer\data\CRM439_sanity\Raw_Data\LTE-B1__3GPP_10MHz_Target_Sanity__Xvc\MAV19 Dev2__ELBOWZ__02May2018_15h25m14s.xml', [])
setup_info = output_array.parse_xml()
>>>>>>> 2df4d4daaf2033f117db783f2bf46076c2eaa55d
