import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import itertools

class XML_processor:
    def __init__(self, folder_path=None):
        self.folder = folder_path
        self.data = defaultdict(list)
    
    def result_generation_helper(self, xml):
        root = ET.parse(xml).getroot()
        
        test_results = defaultdict(list)
        for collection in root.iter('TestCollection'):
            for test in collection.findall('Test'):
                # each test has to have a name
                testarea = test.find('Name').text.rstrip()
                for ds_collection in test.findall('DataSetCollection'):
                    # may not exist
                    collection_name = ds_collection.find('Name')

                    temp = defaultdict()

                    for d in ds_collection.iter('DI'):
                        n, v = d.find('N'), d.find('V')
                        temp[n.text] = v.text
                    if collection_name is not None:
                        test_results[testarea +' ' + collection_name.text].append(temp)
                    else:
                        test_results[testarea + ' Inputs'].append(temp)
        print(test_results['LTE_SpectrumEmissionMask SEM Detail'])

        for testcase in test_results:
            d = defaultdict(list)
            for it in test_results[testcase]:
                for kpi in it:
                    d[kpi].append(it[kpi])
            self.data[testcase].append(d)
    
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
        
        
        for station in self.root.iter("Tester"):
            name = [i.text for i in station.iter('Name')]
            
            for sw_config_info in station.iter('SWConfigInfo'):
                DLL = [i.text for i in sw_config_info.iter('N')][0]+'_'+[i.text for i in sw_config_info.iter('V')][0]
        setup_info['Station_ID'] = name[0]
        setup_info['DLL'] = DLL
       
        for build in self.root.iter("SWBuildID"):
            SW_Build_ID = build.text
        setup_info['DUT_SW_Build'] = SW_Build_ID

        for DUT in self.root.iter("DI"):
            for i in DUT.iter('N'):
                if i.text == "UUTID":
                    HW_ID = [i.text for i in DUT.iter('V')][0]
        setup_info['DUT_HW_ID'] = HW_ID

        return setup_info


output_array = Get_test_info(r'S:\User\tangtc\Testlog_analyzer\data\CRM439_sanity\Raw_Data\LTE-B1__3GPP_10MHz_Target_Sanity__Xvc\MAV19 Dev2__ELBOWZ__02May2018_15h25m14s.xml', [])
setup_info = output_array.parse_xml()
