from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from lxml import etree
import datetime
import logging
import IPy


def build_lookup(element, domain):
    """ Build rule IDs, titles, descriptions in memory. """

    # Initialise variables to avoid reference before assignment
    global_id = global_title = global_fixtext = ''

    if element.tag == domain + "Rule":
        global_id = element.get('id')

        # Iterate over children and find title/desc/fixtext
        for child in element:
            if child.tag == domain + "title":
                global_title = child.text

            if child.tag == domain + "fixtext":
                global_fixtext = child.text

    # Return the parsed values as a tuple back to caller (if exists)
    if global_id and global_title and global_fixtext:
        return global_id, global_title, global_fixtext
    else:
        return None


def parse_testresults(xml, test_id, domain):
    """ Parse the given XML file and build mappings """

    global_lookup = {}
    global_testresults = {}

    for event, element in etree.iterparse(xml, events=("start", "end")):

        try:
            global_id, global_title, global_fixtext = \
                build_lookup(element, domain)
            global_lookup.update({global_id: [global_title, global_fixtext]})
        except TypeError:
            pass

        # # Get results

        if element.tag == domain + 'TestResult' and \
                element.get('id') == test_id:
            # Go through TestResult tag and get all associated results only
            for ch in element:
                if ch.tag == domain + "rule-result":
                    for child in ch:
                        if child.tag == domain + "result":
                            global_testresults[ch.get('idref')] = child.text
                if ch.tag == domain + "score":
                    global_maximum_score = ch.get('maximum')
                    global_score = ch.text
                    global_testresults['max_score'] = global_maximum_score
                    global_testresults['score'] = global_score

    logging.debug("Lookup build successful for all results")
    return global_lookup, global_testresults


def parse_test_result_ids(xml, domain):

    global_test_ids = []

    for event, element in etree.iterparse(xml, events=("start", "end")):
        if element.tag == domain + 'TestResult':
            if element.get('id') not in global_test_ids:
                global_test_ids.append(element.get('id'))

    return global_test_ids


def parse_xml_domain(xml):
    # Get reference resolution
    xmldomain = ''
    for event, element in etree.iterparse(xml, events=("start", "end")):
        xmldomain = ''.join(['{', element.nsmap[None], '}'])

    return xmldomain


def create_dictionary(metadata, results):
    """ Create an internalized dictionary structure intermediate """

    # Initialise internal dict
    internal = dict()

    # Add Benchmark data
    # internal['Benchmark'] = unify_lookup(lookup, results)

    # Add metadata
    internal['metadata'] = {}
    internal['metadata'].update(metadata)

    # Add unified results
    internal.update(create_results_tag(results))

    logging.debug("JSON structure creation success")
    return internal


def handle_result(result):
    """ Handles the result string and returns a boolean if possible"""
    if result == 'notapplicable':
        return -1
    if result == 'pass':
        return 1
    return 0


def unify_lookup(lookup, results):
    """ Create a unified serializable list from lookup and results. """

    unified_list = []

    for key in results.keys():
        if key not in ('score', 'max_score'):
            created_testbench = {'title': lookup[key][0],
                                 'rule-id': key,
                                 'x_fixtext': lookup[key][1]}
            unified_list.append(created_testbench)

    return unified_list


def create_results_tag(results):
    """ Create the updated format results dictionary"""
    results_tag_dict = dict()
    results_tag_dict['results'] = []

    for key in results.keys():
        if key not in ('score', 'max_score'):
            intermediate = {'rule-id': key,
                            'result': handle_result(results[key])}
            results_tag_dict['results'].append(intermediate)

    # Add maximum and attained scores to results
    results_tag_dict['score'] = results['score']
    results_tag_dict['max_score'] = results['max_score']

    return results_tag_dict


def find_benchmark_id(domain, xml):
    """ Parse the given XML and find the Benchmark ID"""
    global_benchmark_id = ''

    for event, element in etree.iterparse(xml, events=("start", "end")):
        if element.tag == domain + "Benchmark":
            global_benchmark_id = element.get('id')

    return global_benchmark_id


def parse_timestamp(timestamp):
    """Parses XCCDF timestamp format to human readable timestamp"""

    date_time = ''

    try:
        date_time = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        logging.error("datetime object creation failed")
        logging.debug("Returning NULL datetime object")
    return date_time


def timestamp_dump(timestamp):
    """ Returns the string for the datetime object after parse"""
    date_time = parse_timestamp(timestamp)
    return datetime.datetime.strftime(date_time, "%Y-%m-%d %H:%M:%S")


def parse_ipaddresses(list_ipaddress):
    """Parses XCCDF IP address format"""

    # Ignore localhost addresses (IPv6 support added)
    localhost = ('127.0.0.1', 'localhost', '0:0:0:0:0:0:0:1', '::1')
    final_list = []
    for ip in list_ipaddress:
        try:
            ip_object = IPy.IP(ip)
            if ip not in localhost:
                final_list.append(ip_object.strNormal())
        except ValueError:
            # One or more IPs failed to validate
            logging.error("IP address validation failed : %s", ip)
            logging.debug("Improper IP list returned, check output file.")

    logging.debug("IP Parsing successful : %d values", len(final_list))
    return final_list


def parse_userlogin(user, privilege):
    """Parses XCCDF logged in user and elevation"""
    return {'user': user, 'privileged': parse_boolean(privilege)}


def parse_boolean(boolean):
    """Parses string bools and returns Python booleans"""
    if boolean in ('false', 'False', '0',):
        return False
    return True


# Main Parse
def parse_metadata(xml, test_id, xmldomain):
    global_metadata = {}

    # Initialise result variables to avoid reference before assignment
    global_ipaddresses = []
    global_starttime = global_endtime = ''
    global_system = global_user = global_privilege = ''
    global_scanner_name = global_scanner_version = ''

    # Get metadata attributes
    for event, element in etree.iterparse(xml, events=("start", "end")):

        if_place = element.get('id') == test_id

        if element.tag == xmldomain + "TestResult" and if_place:

            # Get timestamp
            global_starttime = element.get('start-time')
            global_endtime = element.get('end-time')

            global_system = element.find(xmldomain + 'target').text
            global_identity = element.find(xmldomain + 'identity')
            global_privilege = global_identity.get('privileged')
            global_user = global_identity.text

            global_findips = element.findall(xmldomain + 'target-address')
            global_ipaddresses = [ip.text for ip in global_findips]

            global_facts = element.find(xmldomain + "target-facts")
            global_scanner = global_facts.findall(xmldomain + "fact")

            for fact in global_scanner:
                if 'scanner:name' in fact.get('name'):
                    global_scanner_name = fact.text
                if 'scanner:version' in fact.get('name'):
                    global_scanner_version = fact.text

    global_metadata['hostname'] = global_system
    global_metadata['user'] = parse_userlogin(global_user, global_privilege)

    global_metadata.update({'starttime': timestamp_dump(global_starttime),
                            'endtime': timestamp_dump(global_endtime)})
    global_metadata['ip'] = parse_ipaddresses(global_ipaddresses)
    global_metadata['scanner'] = {'name': global_scanner_name,
                                  'version': global_scanner_version}

    logging.debug("Metadata build success : %s", test_id)
    return global_metadata
