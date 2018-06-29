import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict

class Xml_parser:
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
        # Core data processing function for XML.
        # subject to significant changes as input format changes.
        test_results = defaultdict(list)
        for ds_collection in self.root.iter('DataSetCollection'):
            for name, output in zip(ds_collection.iter('Name'), ds_collection.iter('Outputs')):
                temp = defaultdict()
                for d in output.iter('DI'):
                    for n, v in zip(d.iter('N'), d.iter('V')):
                        temp[n.text] = v.text
                test_results[name.text].append(temp)
        final_res = defaultdict(dict)
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

if __name__=='__main__':
    input_ = input('Please input XML file location')
    output_ = input('Please output report location')
    parser = Xml_parser(input_, output_)
    parser.generate_excel()
