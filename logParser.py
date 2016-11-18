# -*- coding: utf-8 -*-

import datetime
import time
import re
import json

logformatSquid      = '%ts.%03tu %6tr %>a %Ss/%03>Hs %<st %rm %ru %[un %Sh/%<a %mt'
logformatCommon     = '%>a %[ui %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st %Ss:%Sh'
logformatCombined   = '%>a %[ui %[un [%tl] "%rm %ru HTTP/%rv" %>Hs %<st "%{Referer}>h" "%{User-Agent}>h" %Ss:%Sh'
logformatReferrer   = '%ts.%03tu %>a %{Referer}>h %ru'
logformatUseragent  = '%>a [%tl] "%{User-Agent}>h" %%ssl::>cert_issuer'

logFormatCodeRegex = re.compile(r'%(["\[\'#])?(-)?([0-9\.]+)?({.+?})?([%a-zA-Z]+::)?([><a-zA-Z_]+)')
regexEscapeRegex = re.compile(r'([\\\*\+\.\?\{\}\(\)\[\]\^\$\-\|\/])')
whitespaceEscapeRegex = re.compile(r'([ ])')

f = open('logformat-codemaps/squid-31.json', 'r')
codemap = json.load(f)
f.close()

def translateLogFormatCode(m):
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
    ret['key'] = codemap[ret['fullcode']]
    return ret

def replaceLogFormatCode(m):
    ret = translateLogFormatCode(m)
    pattern = '_____' + ret['key'] + '_____'
    return pattern

# 書式 % ["|[|'|#] [-] [[0]width] [{argument}] formatcode
def parse(logformat):
    regex = logFormatCodeRegex.sub(lambda m: replaceLogFormatCode(m), logformat)
    regex = regexEscapeRegex.sub(lambda m: '\\' + m.group(0), regex)
    regex = whitespaceEscapeRegex.sub('\s+', regex) # スペースは複数でも許容させる
    regex = re.sub(r'_____(.*?)_____', lambda m: '(?P<' + m.group(1) + '>[^\s]*?)', regex)
    iterator = logFormatCodeRegex.finditer(logformat)
    codes = map(lambda x: translateLogFormatCode(x), iterator)
    return { 'codes': list(codes), 'regex': regex }

fmt = parse(logformatSquid)
# print(parse(logformatCommon))
# print(parse(logformatCombined))
# print(parse(logformatReferrer))
# print(parse(logformatUseragent))

regex = re.compile(fmt['regex'])

f = open('sample/access.log', 'r')
n = 0
start = time.time()
for i, row in enumerate(f):
    n += 1
    m = regex.match(row)
    if m:
        for c in fmt['codes']:
            print(c['key'], ':', m.group(c['key']))
        print('-' * 40)
    if i == 10:
        break
elapsed = time.time() - start
print('Elapsed: {0:.3f} s ({1:.0f} ms/record)'.format(elapsed, elapsed * 1000 / n))
f.close()
