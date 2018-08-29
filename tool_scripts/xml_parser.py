import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict, OrderedDict
import itertools
import pymongo

class XML_parser:
    def __init__(self, folder_path=None):
        self.folder = folder_path
        self.data = []
        self.testcases = set()

    def precheck(self, xml):
        """
        rtype: str
            returns "success" if all operations successful til call setup;
            else, returns failure reason.
        """
        root = ET.parse(xml).getroot()
        precheck_result = OrderedDict()
        for testname in root.iter("Test"):
            ## using ordered dict allows adding operations in sequence.
            if testname.attrib.get('I') == "3095":
                for child in testname.iter("PassFail"):
                    precheck_result['phonecomm'] = [i.text for i in child.iter("V")][0]
            if testname.attrib.get('I') == "10105":
                for child in testname.iter("PassFail"):
                    precheck_result['initbse'] = [i.text for i in child.iter("V")][0]
            if testname.attrib.get('I') == "10110":
                for child in testname.iter("PassFail"):
                    precheck_result['registration'] = [i.text for i in child.iter("V")][0]
            if testname.attrib.get('I') == "10115":
                for child in testname.iter("PassFail"):
                    precheck_result['callup'] = [i.text for i in child.iter("V")][0]
        for operation in precheck_result:
            if precheck_result[operation] != 'PASS':
                return operation
        return 'success'
    
        
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
                    
                    # one collection may have multiple data sets
                    for dataset in ds_collection.findall('DataSet'):

                        # store result in each test case in a dict
                        temp = defaultdict()
                        
                        # get all input key - value pairs, there might be numerous
                        inputs = dataset.find('Inputs')
                        for d in inputs.iter('DI'):
                            n, v = d.find('N'), d.find('V')
                            temp[n.text] = v.text
                            
                        # There might be multiple results in each output
                        # For each result, get name and use name to construct limit name
                        outputs = dataset.find('Outputs')
                        for result in outputs.findall('Result'):
                            kpi_name = result.find('DI').find('N')
                            kpi = result.find('DI').find('V')
                            temp[kpi_name.text] = kpi.text
                            
                            # limit related search
                            limit = result.find('Limits')
                            
                            if limit is None:
                                # limit does not exist
                                continue
                                
                            max_limit = limit.find('Max')
                            if max_limit is not None:
                                temp[kpi_name.text+'MAX_limit'] = max_limit.text
                            
                            min_limit = limit.find('Min')
                            if min_limit is not None:
                                temp[kpi_name.text+'MIN_limit'] = min_limit.text
                                
                            kpi_result = limit.find('PassFail').find('V')
                            if kpi_result is not None:
                                temp[kpi_name.text+'Result'] = kpi_result.text

                        # attempt to use collection name
                        # if not successful, it is an input section, use 'Input' instead
                        if collection_name is not None:
                            test_results['_'.join((testarea + collection_name.text).split()).lower()].append(temp)
                        else:
                            test_results['_'.join((testarea + 'Inputs').split()).lower()].append(temp)

        # Given test_results in form dict[list[dict]]: testcase -> list of occurrences -> KPI
        # Transform to dict[dict[list]]: testcase -> KPI -> list of results
        final_res = defaultdict()
        for testcase in test_results:
            self.testcases.add(testcase)
            # Transform to KPI -> list of results
            d = defaultdict(list)
            for it in test_results[testcase]:
                for kpi in it:
                    d[kpi].append(it[kpi])
            final_res[testcase] = d
        self.data.append(final_res)

    def collect_data(self):
        if self.folder is None:
            self.folder = input()
        for xml_file in Path(self.folder).glob('*.xml'):
            check_result = self.precheck(xml_file)
            if check_result == 'success':
                self.result_generation_helper(xml_file)
            else:
                print(check_result)
              
            
class mongodb_filler:
    def __init__(self, xml_parser):
        """
        xml_parser: XML_parser
            data source
        """
        self.xml_parser = xml_parser
        
    def generate_classes(self):
        doc_classes = {}
        for test in self.xml_parser.testcases:
            values = {
                'uuid': StringField(default='12345'),
                'testcasename': StringField(default='test', required=True),
                'data': DictField(),
            }
            doc_classes[test] = type(test, 
                                     (mongoengine.Document, ), 
                                     values,
                                    )                                 
        self.doc_classes = doc_classes
        
    def fill_database(self):
        self.generate_classes()
        for doc in self.xml_parser.data:
            for testcase in doc:
                doc_class = self.doc_classes[testcase]
                new_doc = doc_class(testcasename=testcase, data=doc[testcase])
                new_doc.save()
                
                
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
