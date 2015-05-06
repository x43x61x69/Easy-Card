#!/usr/bin/env python
#-*- coding:utf-8 -*-

#
# Name: 悠遊卡餘額明細查詢
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Zhi-Wei Cai.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys
import datetime
import hashlib
import urllib
import urllib2
import json

from Crypto.Cipher import DES3
import pytz

version = '0.3'
copyright = 'Copyright (C) 2015 Zhi-Wei Cai.'

# lol
key = 'EasyCardToKingay23456789'
iv = '01234567'
salt = 'L0CalKing'
const = 0x2160


def getID(data, isEncrypt, key, iv, encode):
    size = len(data)
    if size % 16 != 0:
        data += '\x06' * (16 - size % 16)
    des3 = DES3.new(key, DES3.MODE_CBC, iv)
    if isEncrypt:
        result = des3.encrypt(data).encode(encode).rstrip()
    else:
        result = des3.decrypt(data.decode(encode))
    return result


def getVerify(const, seed, salt):
    hash = hashlib.md5()
    hash.update(str(seed * const) + salt)
    return hash.hexdigest().upper()


def proc(data):
    e = getID(data, 1, key, iv, 'base64')
    #print e
    cardID = urllib.quote_plus(e)
    date = datetime.datetime.now(pytz.timezone('Asia/Taipei'))
    seed = date.month + date.day + date.hour
    begin = '{:%Y-%m-%d}'.format(date - datetime.timedelta(days=30))
    end = '{:%Y-%m-%d}'.format(date)
    verify = getVerify(const, seed, salt)
    url = 'https://wallet.easycard.com.tw/EasyWallet/QueryManager/V3/GetTXNThinDataInfo?verify={}&cardID={}&begin={}&end={}&ev=1'.format(verify, cardID, begin, end)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    content = response.read()
    dict = json.loads(content)
    try:
        if dict[-1]['B'] != '--':
            print('{: ^90}'.format('卡號 "{} {} {}"，餘額：{} 元'.format(data[0:3], data[3:9], data[-1], dict[-1]['B'])))
            print(url)
            if len(dict) > 1:
                if dict[0]['T'].encode('utf-8') != '查無交易資料':
                    print('\n{:=^90}\n'.format('[ 交易明細 ]'))
                i = 1
                for item in dict:
                    try:
                        if item['T']:
                            if item['T'] == 'D':
                                action = '扣款'
                            else:
                                action = '儲值'
                            print('#{:>4} [{}] {} {:>5} 元，餘額 {:>5} 元，地點：{}'.format(i, item['D'], action, item['Q'], item['A'], item['L'].encode('utf-8').replace('<BR>', '-')))
                            i += 1
                    except KeyError as err:
                        pass
    except KeyError as err:
        print('卡號 "{}" 不存在！'.format(data))
    except ValueError as err:
        print('卡號 "{}" 不存在！'.format(data))
    print('\n{:=^90}\n\n'.format('[ 查詢結束 ]'))


if __name__ == '__main__':
    print('\n悠遊卡餘額明細查詢 v{}'.format(version))
    print('{}\n'.format(copyright))
    
    if len(sys.argv) > 1:
        try:
            print '\n{:=^90}\n'.format('[ 查詢開始 ]')
            proc(str(sys.argv[1]))
        except ValueError as err:
            pass
    else:
        while 1:
            try:
                data = raw_input("請輸入卡片號碼：").replace(' ', '')
                if len(data):
                    print '\n{:=^90}\n'.format('[ 查詢開始 ]')
                    proc(data)
                else:
                    break
            except ValueError as err:
                pass
