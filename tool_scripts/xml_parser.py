import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import itertools
import pymongo

class Xml_parser:
    """
    Main parser for collecting information from past test result XML files.
    """
    def __init__(self, input_fp='', output_fp=None):
        """
        input_fp: XML path
        output_fp: Excel/CSV path
        """
        self.root = ET.parse(input_fp).getroot()
        if not output_fp:
            output_fp = input()
        self.output_fp = output_fp
        self.tables = None

    def result_generation_helper(self):
        """
        Core data processing function for XML. Subject to changes as input format and requirements change.
        :return: None
        """
        test_results = defaultdict(list)    # raw data collection
        for ds_collection in self.root.iter('DataSetCollection'):
            # Each test case run is organized under data set collection
            iterators = [ds_collection.iter('Name'), ds_collection.iter('Outputs'), ds_collection.iter('Inputs')]
            for name, output, inputs in zip(*iterators):    # for each testcase name, output collection and input collection...
                temp = defaultdict()
                for d in itertools.chain(inputs.iter('DI'), output.iter('DI')): # combine two iterators and loop over
                    for n, v in zip(d.iter('N'), d.iter('V')):                  # collect key-value pairs
                        temp[n.text] = v.text
                test_results[name.text].append(temp)                      # dictionary in form  of testcase->list of results(dict)
        final_res = defaultdict(dict)                                     # reshape data to form of testcase->dictionary of lists
        for testcase in test_results:
            d = defaultdict(list)
            for it in test_results[testcase]:
                for kpi in it:
                    d[kpi].append(it[kpi])
            final_res[testcase] = d
        self.tables = final_res

    def generate_excel(self):
        if not self.tables:
            # if table does not exist already, generate tables
            self.result_generation_helper()
        writer = pd.ExcelWriter(self.output_fp)
        for test in self.tables:
            test_name = test
            if len(test_name) > 31:
                test_name = test_name[:30]
            try:
                pd.DataFrame.from_dict(self.tables[test], orient='index').T.to_excel(writer, test_name)
            except:
                continue
                
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