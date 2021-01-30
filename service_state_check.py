#!/usr/bin/env python2
#-*- coding: utf-8 -*-

from flask import Flask, request
import os
import json
from pprint import pprint
import subprocess, socket
import httplib
from time import sleep

os.environ['FLASK_APP']='service_state_check.py'
app = Flask(__name__)

RetryInterval=int(os.environ.get('RetryInterval', 5))
RetryTimes=int(os.environ.get('RetryTimes', 40))
ConnectionTimeOut=int(os.environ.get('ConnectionTimeOut', 10))

def checkPortState(host='127.0.0.1',port=9200):
### 检查对应服务器上面的port 是否处于TCP监听状态 ##

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(ConnectionTimeOut)
    try:
       s.connect((host,port))
       return {'ret_code':0,
               'result':str(host)+':'+str(port)+' is listening'}
    except:
       return {'ret_code':1,
               'result':'can not access '+str(host)+':'+str(port)}


@app.route('/checkservice', methods=['POST', ])
def checkServiceState():
    RawData=request.get_data()
    RawHeader=request.headers
    RawJson=request.json
    RawDict=json.loads(RawData)

    TmpAvailableServiceList  = []
    TmpFailedServiceList = []

    for endpoint in RawDict['endpoints']:
        endpoint = endpoint.strip()
        if not endpoint:
            continue

        TmpList =  endpoint.split(':')
        if len(TmpList) == 1:
            TmpHost = TmpList[0].strip()
            TmpPort = 80
        elif len(TmpList) == 2:
            TmpHost = TmpList[0].strip()
            TmpPort = int(TmpList[1].strip())
        else:
            print ('invalid endpont: %s'%(endpoint, ))
            TmpFailedServiceList.append(endpoint)

        for _ in range(RetryTimes):
            TmpCheckResult = checkPortState(host=TmpHost, port= TmpPort)
            print (str(TmpCheckResult))
            if TmpCheckResult['ret_code'] == 0:
                TmpAvailableServiceList.append(endpoint)
                break
            print ('#%s %s current is not ok, retry...'%(str(_), endpoint))
            sleep (RetryInterval)
        else:
            TmpFailedServiceList.append(endpoint)


    TmpDict = {
        'ret_code': 0,
        'result': {
            'AvailableServcies': TmpAvailableServiceList,
            'FailedServices': TmpFailedServiceList,
        }
    }

    TmpResponse = json.dumps(TmpDict)
    return TmpResponse

