from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import sys


if sys.version_info > (2, 7):
    # Python 2.7.x and 3.x
    import unittest
else:
    # Pre Python 2.7.x
    import unittest2 as unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)
