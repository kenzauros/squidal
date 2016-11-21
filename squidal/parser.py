# -*- coding: utf-8 -*-

import re
import json
import os.path

class SquidLogParser:
    '''Read values from Squid log file.'''

    # Constants
    FORMATCODES_DIR = 'formatcodes'
    KEY_ESCAPE = '_____'

    # Class variables
    __logFormatCodeRegex = re.compile(r'%(["\[\'#])?(-)?([0-9\.]+)?({.+?})?([%a-zA-Z]+::)?([><a-zA-Z_]+)')
    __regexEscapeRegex = re.compile(r'([\\\*\+\.\?\{\}\(\)\[\]\^\$\-\|\/])')
    __whitespaceEscapeRegex = re.compile(r'([ ])')
    __keyReplaceRegex = re.compile(KEY_ESCAPE + r'(.*?)' + KEY_ESCAPE)

    def __init__(self, version):
        self.success = False
        self.codes = []
        self.keys = []
        self.__match = None
        self.__codemap = None
        self.__setVersion(version)

    def __setVersion(self, version):
        filename = '%s/squid-%s.json' % (self.FORMATCODES_DIR, version)
        if not os.path.exists(filename):
            raise Exception('Version %s is not supported.' % version)
        with open(filename, 'r') as f:
            self.__codemap = json.load(f)
        self.version = version

    def __translateLogFormatCode(self, m):
        ret = {}
        ret['match'] = m.group(0)
        ret['format'] = m.group(1)
        ret['left_aligned'] = True if m.group(2) else False
        ret['width'] = m.group(3) and int(m.group(3))
        ret['zero_padded'] = True if m.group(3) and m.group(3)[0] == '0' else False
        ret['argument'] = m.group(4) and m.group(4)[1:-1]
        ret['code'] = m.group(6)
        ret['fullcode'] = (m.group(5) or '') + ret['code']
        ret['section'] = m.group(5) and m.group(5)[0:-2]
        ret['key'] = self.__codemap[ret['fullcode']]
        return ret

    def __replaceLogFormatCode(self, m):
        ret = self.__translateLogFormatCode(m)
        pattern = self.KEY_ESCAPE + ret['key'] + self.KEY_ESCAPE
        return pattern

    def setLogFormat(self, logformat):
        '''
        Set the logformat.
        This method must be called before parse.
        Logformat must contains available formatcodes.
        '''
        # format for Squid's formatcode: % ["|[|'|#] [-] [[0]width] [{argument}] formatcode
        self.logformat = logformat
        pattern = self.__logFormatCodeRegex.sub(lambda m: self.__replaceLogFormatCode(m), logformat)
        pattern = self.__regexEscapeRegex.sub(lambda m: '\\' + m.group(0), pattern)
        pattern = self.__whitespaceEscapeRegex.sub('\s+', pattern) # accepts multiple spaces
        pattern = self.__keyReplaceRegex.sub(lambda m: '(?P<' + m.group(1) + '>[^\s]*?)', pattern)
        iterator = self.__logFormatCodeRegex.finditer(logformat)
        codes = list(map(lambda x: self.__translateLogFormatCode(x), iterator))
        self.keys = list(map(lambda x: x['key'], codes))
        self.codes = codes
        self.logformatRegexPattern = pattern
        self.__regex = re.compile(pattern)

    def parse(self, log):
        '''
        Parse a log line.
        Call "get" method to get an extracted value after call this method.
        '''
        if not self.logformatRegexPattern:
            raise Exception('"logformat" is not avilable. Call "setLogFormat" method to set it.')
        m = self.__regex.match(log)
        self.success = bool(m)
        self.__match = m
        return self.success

    def get(self, key):
        '''Get any extracted value by "parse" method.'''
        if not self.success:
            raise Exception('"parse" method has not been succeeded. Call parse method and make sure if it returns True.')
        return self.__match.group(key)
