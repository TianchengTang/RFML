from mongoengine import *

# Read test case names
with open('test_case_names.txt', 'rt') as f:
    tests = []
    for item in f.readlines():
        tests.append(item.rstrip())

# generate classes for all tests
test_classes = {}   # test case to class mapping

for test in tests:
    values = {
    'uuid': StringField(default='12345'),
    'testcasename': StringField(default='test', required=True),
    'data': DictField(),
}

    test_classes[test] = type(
        test,
        (Document, ),
        values,
    )


## Save all data to MongoDB
for doc in processor.data:
    for testcase in doc:
        doc_class = test_classes[testcase]
        new_doc = doc_class(testcasename=testcase, data=doc[testcase])
        new_doc.save()
