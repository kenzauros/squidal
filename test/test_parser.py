# -*- coding: utf-8 -*-

import time
import re
import unittest
from squidal import SquidLogParser

logformatSquid = '%ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt'
logformatSquidBroken = '%tXs.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt'

# logformatCommon = '%>a %[ui %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st %Ss:%Sh'
# logformatCombined = '%>a %[ui %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st "%{Referer}>h" "%{User-Agent}>h" %Ss:%Sh'
# logformatReferrer = '%ts.%03tu %>a %{Referer}>h %ru'
# logformatUseragent = '%>a [%tl] "%{User-Agent}>h" %%ssl::>cert_issuer'

VERSION_AVAILABLE = 3.1
VERSION_UNAVAILABLE = 3.9
SAMPLE_LOG = 'sample/access.log'

class TestSquidLogParser(unittest.TestCase):
    # Constructor
    def test_constructor(self):
        # Can instantiate with avilable version
        parser = SquidLogParser(VERSION_AVAILABLE)
        # Cannot instantiate with unavilable version
        with self.assertRaises(Exception):
            parser = SquidLogParser(VERSION_UNAVAILABLE)

    # Set Squid's logformat
    def test_setLogFormat(self):
        parser = SquidLogParser(VERSION_AVAILABLE)
        # Valid logformat
        parser.setLogFormat(logformatSquid)
        # Invalid logformat
        with self.assertRaises(Exception):
            parser.setLogFormat(logformatSquidBroken)

    # Parse a row in log
    def test_parse(self):
        parser = SquidLogParser(VERSION_AVAILABLE)
        with open(SAMPLE_LOG, 'r') as f:
            row = f.readline()
            # parse before setLogFormat
            with self.assertRaises(Exception):
                parser.parse(parser.keys[0])
            parser.setLogFormat(logformatSquid)
            # parse after setLogFormat
            self.assertTrue(parser.parse(row))

    # Get values from a single row
    def test_get(self):
        parser = SquidLogParser(VERSION_AVAILABLE)
        parser.setLogFormat(logformatSquid)
        # get before parse
        with self.assertRaises(Exception):
            parser.get(parser.keys[0])
        # get after parse
        with open(SAMPLE_LOG, 'r') as f:
            row = f.readline()
            self.assertTrue(parser.parse(row))
            self.assertIsNotNone(parser.get(parser.keys[0]))

    # Get values from multiple rows
    def test_all(self):
        parser = SquidLogParser(VERSION_AVAILABLE)
        parser.setLogFormat(logformatSquid)
        n = 0
        # start = time.time()
        with open(SAMPLE_LOG, 'r') as f:
            for i, row in enumerate(f):
                self.assertTrue(parser.parse(row))
                for key in parser.keys:
                    self.assertIsNotNone(parser.get(key))
                n += 1
                if n == 100:
                    break
        # elapsed = time.time() - start
        # print('Elapsed: {0:.3f} s / {1} records ({2:.0f} ms/record)'.format(elapsed, n, elapsed * 1000 / n))
