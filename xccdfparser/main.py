from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import sys

from xccdfparser import lib

import json
import argparse
import logging
import os


def xmlparse(xml):
    """ Perform required operations in order. """

    # Get domain reference resolution
    domain = lib.parse_xml_domain(xml)
    logging.debug("Domain reference resoultion success : %s", domain)

    # Get all possible test result ids
    test_result_ids = lib.parse_test_result_ids(xml, domain)
    logging.debug("Test result IDs acquired")

    # Init list of metadata and results
    list_metadata = []
    list_results = []
    dict_writecontent = {}
    lookup = results = None

    for test_id in test_result_ids:
        # Get metadata from file
        metadata = lib.parse_metadata(xml, test_id, domain)
        # Parse for test results
        lookup, results = lib.parse_testresults(xml, test_id, domain)
        # Create serialized JSON Object
        write_content = lib.create_dictionary(metadata, results)

        logging.debug("Parsing TestResult id : %s", test_id)

        list_metadata.append(metadata)
        list_results.append(results)
        dict_writecontent[test_id] = write_content

    # Write Benchmark data universal for all tests
    dict_writecontent['Benchmark'] = dict()
    global_benchmark_id = lib.find_benchmark_id(domain, xml)
    global_rules = lib.unify_lookup(lookup, results)

    dict_writecontent['Benchmark'].update({'id': global_benchmark_id,
                                           'rules': global_rules})

    # Return the results for writing to JSON file
    return json.dumps(dict_writecontent, sort_keys=True, indent=4)


def write_to_json(obj, filename):
    """ Utility function to write to file """
    try:
        with open(filename, str("w")) as file_obj:
            file_obj.write(obj)
    except IOError:
        logging.warning("Write permissions not verified")
        logging.error("File write error : %s", filename)


def augment_filename(filename):
    """ Automatically name output JSON file, if not given in arguments """
    new_file = filename.rstrip('.xml') + '.json'

    if '.xml' in new_file:
        sys.stderr.write("Given file is not in XML format. ")
    else:
        return new_file


def main():
    """ Run the required functions and write output. """

    help_text = "-vvv=DEBUG, -vv=INFO, -v=WARN, nothing - ERROR(default)"
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='count', default=0,
                        help=help_text)
    parser.add_argument('-o', '--out', help="to specify an output JSON file")
    parser.add_argument('file', help="XML file to be parsed")
    args = parser.parse_args()

    verbose_level = {0: logging.ERROR,
                     1: logging.WARNING,
                     2: logging.INFO,
                     3: logging.DEBUG}

    # Set logger to verbose level given in arguments
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=verbose_level[args.verbose])

    # Check if file exists
    if not os.path.isfile(args.file):
        logging.error("Given file does not exist : %s", args.file)
        sys.exit(1)

    # Open the file and run the program
    if not args.out:
        file_to_write = augment_filename(args.file)
        logging.debug("Output filename : %s", file_to_write)
    else:
        file_to_write = args.out

    logging.info("Opening file : %s", args.file)
    write_content = xmlparse(args.file)
    logging.info("File opening successful : %s", args.file)

    logging.info("Writing JSON to file : %s", file_to_write)
    write_to_json(write_content, file_to_write)
    logging.info("File write successful : %s", file_to_write)


if __name__ == '__main__':
    main()
