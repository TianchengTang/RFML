"""
Dynamic class reference:
    https://www.python-course.eu/python3_classes_and_type.php
"""
from mongoengine import *

# Read test case names
with open('test_case_names.txt', 'rt') as f:
    tests = []
    for item in f.readlines():
        tests.append(item.rstrip())

def generate_document_classes(tests):
    """
        generate classes for all tests.

        tests: List[str]
            test case names
        return: dict
            dictionary of class name -> class mapping

    """
    test_classes = {}   # test case to class mapping

    # define common fields for all document classes
    values = {
        'uuid': StringField(default='12345'),
        'testcasename': StringField(default='test', required=True),
        'data': DictField(),
    }

    for test in tests:
        test_classes[test] = type(
            test,
            (Document, ),
            values,
        )
    return test_classes

def write_to_db(processor, test_classes):
    """
        Save all data to MongoDB.

        processor: XML_processor
            XML Processor containing data from XML files
        test_classes: dict
            dictionary of class name -> class mapping
        return: None

    """
    for xml_doc in processor.data:
        for testcase in xml_doc:
            doc_class = test_classes[testcase]
            new_doc = doc_class(testcasename=testcase, data=xml_doc[testcase])
            new_doc.save()


if __name__ == '__main__':
    test_classes = generate_document_classes()
    write_to_db(processor, test_classes)
