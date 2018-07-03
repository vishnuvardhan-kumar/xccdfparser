from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import sys
from xccdfparser import main, lib
import json
import datetime

if sys.version_info > (2, 7):
    # Python 2.7.x and 3.x
    import unittest
else:
    # Pre Python 2.7.x
    import unittest2 as unittest


class TestParser(unittest.TestCase):

    testfile = ''
    testfilerelative = ''
    sample = ''
    samplerelative = ''
    json_data = ''
    results = ''
    expected1 = expected2 = ''
    testlist = testtarget = testuser = ''
    sample_file = sample_file_relative = ''
    metadata = domain = ''
    testcase = lookup = ''
    test_id = case = ''
    user = user_results = privilege = ''
    time1 = time2 = ''
    testcase_1 = testcase_2 = ''

    def test_create_dictionary(self):
        self.testfile = 'xccdfparser/tests/test/sample.json'
        self.testfilerelative = 'tests/sample.json'
        self.sample = 'xccdfparser/tests/test/sample.xml'
        self.samplerelative = 'test/sample.xml'

        try:
            with open(self.testfile) as file_obj:
                self.json_data = json.loads(file_obj.read())
                self.json_data = json.dumps(self.json_data,
                                            sort_keys=True, indent=4)
        except IOError:
            with open(self.testfilerelative) as file_obj:
                self.json_data = json.loads(file_obj.read())
                self.json_data = json.dumps(self.json_data,
                                            sort_keys=True, indent=4)

        try:
            self.results = main.xmlparse(self.sample)
        except IOError:
            self.results = main.xmlparse(self.samplerelative)

        self.assertTrue('"endtime": "2016-05-31 14:53:55"' in self.results)

    def test_unify_lookup(self):
        self.expected1 = [{'rule-id': 'a', 'x_fixtext': '2', 'title': '1'}]
        self.testcase_1 = {'a': ['1', '2']}, \
                          {'a': 'b', 'score': '5', 'max_score': '100'}
        self.assertEqual(lib.unify_lookup(*self.testcase_1),
                         self.expected1)

    def test_parse_timestamp(self):
        self.time1 = isinstance(lib.parse_timestamp('2018-05-31T14:53:52'),
                                datetime.datetime)
        self.time2 = isinstance(lib.parse_timestamp('2018-05-31T14:53:52'),
                                datetime.datetime)

        self.assertTrue(self.time1)
        self.assertTrue(self.time2)

    def test_parse_ipaddresses_ipv4(self):
        self.testlist = ['127.0.0.1', '31.21.18.100']
        self.assertEqual(lib.parse_ipaddresses(self.testlist),
                         ['31.21.18.100'])

    def test_parse_ipaddresses_ipv6(self):
        self.testlist = ['0:0:0:0:0:0:0:1',
                         '3ffe:1900:4545:3:200:f8ff:fe21:67cf']
        self.assertEqual(lib.parse_ipaddresses(self.testlist),
                         ['3ffe:1900:4545:3:200:f8ff:fe21:67cf'])

    def test_parse_userlogin(self):
        self.user, self.privilege = 'dheeraj', 'false'
        self.user_results = lib.parse_userlogin(self.user, self.privilege)
        self.assertEqual(self.user_results['user'], 'dheeraj')
        self.assertEqual(self.user_results['privileged'], False)

    def test_parse_metadata(self):
        self.sample_file = "xccdfparser/tests/test/sample.xml"
        self.sample_file_relative = "test/sample.xml"
        self.test_id = "xccdf_org.open-scap_testresult_default-profile"
        self.domain = '{http://checklists.nist.gov/xccdf/1.2}'

        try:
            self.metadata = lib.parse_metadata(self.sample_file,
                                               self.test_id, self.domain)
        except IOError:
            self.metadata = lib.parse_metadata(self.sample_file_relative,
                                               self.test_id, self.domain)

        self.assertEqual(self.metadata['ip'],
                         ["31.21.18.100",
                          "3ffe:1900:4545:3:200:f8ff:fe21:67cf"])
        self.assertEqual(self.metadata['starttime'], '2016-05-31 14:53:52')
        self.assertEqual(self.metadata['endtime'], '2016-05-31 14:53:55')
        self.assertEqual(self.domain,
                         '{http://checklists.nist.gov/xccdf/1.2}')

    def test_parse_testresults(self):

        self.domain = "{http://checklists.nist.gov/xccdf/1.2}"
        self.testfile = "xccdfparser/tests/test/sample.xml"
        self.testfilerelative = "test/sample.xml"
        self.testcase = "xccdf_mil.disa.stig_rule_SV-50237r1_rule"
        self.test_id = "xccdf_org.open-scap_testresult_default-profile"

        try:
            self.lookup, self.results = lib.parse_testresults(self.testfile,
                                                              self.test_id,
                                                              self.domain)
        except IOError:
            # Running individual test from this level
            self.case = lib.parse_testresults(self.testfilerelative,
                                              self.test_id, self.domain)
            self.lookup, self.results = self.case

        self.assertEqual(self.results[self.testcase], "WellPlayed")


if __name__ == '__main__':
    unittest.main()
