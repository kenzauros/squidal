# -*- coding: utf-8 -*-

import datetime
import time
import re

from peewee import *

db = SqliteDatabase('squid-log.db')

# access.log のモデル
class Access(Model):
    time = DateTimeField()
    duration = IntegerField()
    client = CharField()
    result = CharField()
    status = IntegerField()
    bytes = IntegerField()
    method = CharField()
    url = CharField()
    rfc931 = CharField()
    peerstatus = CharField()
    peerhost = CharField()
    type = CharField()
    scheme = CharField()
    host = CharField()
    ssl = BooleanField()

    class Meta:
        database = db  # This model uses the "people.db" database.


f = open('sample/access.log', 'r')
start = time.time()
n = 0
db.create_tables([Access], True)
with db.transaction():
    # スキーマ (http など) を取得する正規表現
    schemeRegex = re.compile(r'([^:/]*):\/{2}')
    # ホスト名を取得する正規表現
    hostRegex = re.compile(r'([^:/]*:\/{2})?([^:/]*)')
    # SSL かどうかを判別する正規表現
    sslRegex = re.compile(r'([^:/]*:\/{2})?([^:/]*):443')
    for i, row in enumerate(f):
        print(row.strip())
        words = row.split()
        dt = datetime.datetime.fromtimestamp(float(words[0]))
        resultCodes = words[3].split('/')
        peerStatus = words[8].split('/')
        url = words[6]
        # SSL かどうか
        isSSL = True if sslRegex.match(url) else False
        # スキーマ (http など)
        scheme = schemeRegex.match(url)
        scheme = '' if scheme is None else scheme.group(1)
        # スキーマが取得できず、443 ポートの場合は https にしておく
        if not scheme and isSSL:
            scheme = 'https'
        # ホスト名
        host = hostRegex.match(url)
        host = '' if host is None else host.group(2)
        # レコード生成
        record = Access(time=dt, duration=words[1], client=words[2], result=resultCodes[0], \
            status=resultCodes[1], bytes=words[4], method=words[5], url=url, \
            rfc931=words[7], peerstatus=peerStatus[0], peerhost=peerStatus[1], type=words[9], \
            scheme=scheme, host=host, ssl=isSSL)
        record.save()
        n += 1
        # if i == 5:
        #     break

elapsed = time.time() - start
print('Elapsed: {0:.3f} s ({1:.0f} ms/record)'.format(elapsed, elapsed * 1000 / n))
f.close()
