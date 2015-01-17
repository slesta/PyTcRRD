#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime
import time
import os
import subprocess
import re
from tcvars import *
from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT
from pyrrd.graph import ColorAttributes, Graph

step = 2

min = 60
hour = 60 * 60
day = 24 * 60 * 60
week = 7 * day
month = day * 30
quarter = month * 3
half = 365 * day / 2
year = 365 * day

now = int(time.time())


def unitsconvert(value, unit):
    if unit == 'bit':
        return int(value)
    if unit == 'Kbit':
        return int(value) * 1000
    if unit == 'Mbit':
        return int(value) * 1000000
    if unit == 'Gbit':
        return int(value) * 1000000000


def hextodecipmask(ipmask):
    ipmask = ipmask.split('/')
    ip = str(ipmask[0])
    mask = ipmask[1]
    ip1 = int(ip[0:2], 16)
    ip2 = int(ip[2:4], 16)
    ip3 = int(ip[4:6], 16)
    ip4 = int(ip[6:8], 16)
    mask1 = int(mask[0:2], 16)
    mask2 = int(mask[2:4], 16)
    mask3 = int(mask[4:6], 16)
    mask4 = int(mask[6:8], 16)
    ip = str(ip1) + '.' + str(ip2) + '.' + str(ip3) + '.' + str(ip4)
    mask = str(mask1) + '.' + str(mask2) + '.' + str(mask3) + '.' + str(mask4)
    return (ip, mask)


def feedfile():
    arrlan = []
    arrlanf = []
    arrwan = []
    arrwanf = []




    #time.sleep(20)
    ####################################### nacitani TC FILTER LAN

    rawstr = r"""(?:flowid )(?P<flowid>[0-9:a-f]+)(?:[\t\n\r ]+)(?:match )(?P<hexip>[0-9a-fA-F/]+)"""
    filteroutput = \
        subprocess.Popen(['tc -s filter show dev ' + str(lan)], shell=True, stdout=subprocess.PIPE).communicate()[0]
    filteroutput = filteroutput[0:-1].split('filter')
    for line in filteroutput:
        # print line
        match_obj = re.search(rawstr, line, re.MULTILINE)
        if match_obj != None:
            line = []
            flowid = match_obj.group('flowid')
            hexip = match_obj.group('hexip')
            # print flowid
            # print hexip
            ip, mask = hextodecipmask(hexip)
            arrlanf.append({'flowid': flowid, 'ip': ip, 'mask': mask})

    ####################################### nacitani TC FILTER WAN

    rawstr = r"""(?:flowid )(?P<flowid>[0-9:a-f]+)(?:[\t\n\r ]+)(?:match )(?P<hexip>[0-9a-fA-F/]+)"""
    filteroutput = \
        subprocess.Popen(['tc -s filter show dev ' + str(wan)], shell=True, stdout=subprocess.PIPE).communicate()[0]
    filteroutput = filteroutput[0:-1].split('filter')
    for line in filteroutput:
        # print line
        match_obj = re.search(rawstr, line, re.MULTILINE)
        if match_obj != None:
            line = []
            flowid = match_obj.group('flowid')
            hexip = match_obj.group('hexip')
            ip, mask = hextodecipmask(hexip)
            arrwanf.append({'flowid': flowid, 'ip': ip, 'mask': mask})
    # print arrlan
    # print arrwan

    ####################################### nacitani TC CLASS LAN

    rawstr = r"""(?:class htb )(?P<classid>[0-9a-fA-F:]+)(?: parent )(?P<parentid>[0-9a-fA-F:]+)(?:(?:(?: prio )(?P<prio>[0-9]+))|(?:))(?: rate )(?P<rate>[0-9]+)(?P<rateunit>[MmKkbit]+)(?: ceil )(?P<ceil>[0-9]+)(?P<ceilunit>[MmKkbit]+)(?: burst )(?P<burst>[0-9]+)(?P<burstunit>[MmKkbit]+)(?: cburst )(?P<cburst>[0-9]+)(?P<cburstunit>[MmKkbit]+)(?:[\t \n\r]+)(?:Sent )(?P<sent>[0-9]+)(?: bytes )(?P<pckt>[0-9]+)(?:[ pkt(]+)(?:[a-zA-Z0-9, ]+)(?:[)])(?:[\n \t\r]+)(?:rate )(?P<rateps>[0-9]+)(?:[MmKkbit]+ )(?P<pps>[0-9]+)(?:[a-zA-Z0-9 ]+)(?:[\t \n\r])(?: lended: )(?P<lended>[0-9]+)(?: borrowed: )(?P<borrowed>[0-9]+)"""
    classoutput = \
        subprocess.Popen([' tc -s class show dev ' + str(lan)], shell=True, stdout=subprocess.PIPE).communicate()[0]
    classoutput = classoutput[0:-1].split('\n\n')
    for line in classoutput:
        # print line
        match_obj = re.search(rawstr, line, re.MULTILINE)
        if match_obj != None:
            line = []
            classid = match_obj.group('classid')
            parentid = match_obj.group('parentid')
            prio = match_obj.group('prio')
            rate = match_obj.group('rate')
            rateunit = match_obj.group('rateunit')
            ceil = match_obj.group('ceil')
            ceilunit = match_obj.group('ceilunit')
            burst = match_obj.group('burst')
            burstunit = match_obj.group('burstunit')
            cburst = match_obj.group('cburst')
            cburstunit = match_obj.group('cburstunit')
            sent = match_obj.group('sent')
            pckt = match_obj.group('pckt')
            rateps = match_obj.group('rateps')
            pps = match_obj.group('pps')
            lended = match_obj.group('lended')
            borrowed = match_obj.group('borrowed')
            # for itemlan in arrlan:
            # if itemlan['flowid'] == classid:
            arrlan.append(
                {'classid': classid, 'sent': sent, 'pckt': pckt, 'prio': prio, 'rate': rate, 'rateunit': rateunit,
                 'ceil': ceil,
                 'ceilunit': ceilunit, 'lended': lended, 'borrowed': borrowed, 'interface': 'lan'})



    ####################################### nacitani TC CLASS WAN

    classoutput = \
        subprocess.Popen([' tc -s class show dev ' + str(wan)], shell=True, stdout=subprocess.PIPE).communicate()[0]
    classoutput = classoutput[0:-1].split('\n\n')
    for line in classoutput:
        # print line
        match_obj = re.search(rawstr, line, re.MULTILINE)
        if match_obj != None:
            line = []
            classid = match_obj.group('classid')
            parentid = match_obj.group('parentid')
            prio = match_obj.group('prio')
            rate = match_obj.group('rate')
            rateunit = match_obj.group('rateunit')
            ceil = match_obj.group('ceil')
            ceilunit = match_obj.group('ceilunit')
            burst = match_obj.group('burst')
            burstunit = match_obj.group('burstunit')
            cburst = match_obj.group('cburst')
            cburstunit = match_obj.group('cburstunit')
            sent = match_obj.group('sent')
            pckt = match_obj.group('pckt')
            rateps = match_obj.group('rateps')
            pps = match_obj.group('pps')
            lended = match_obj.group('lended')
            borrowed = match_obj.group('borrowed')
            # for itemwan in arrwan:
            # if itemwan['flowid'] == classid:
            arrwan.append(
                {'classid': classid, 'sent': sent, 'pckt': pckt, 'prio': prio, 'rate': rate, 'rateunit': rateunit,
                 'ceil': ceil,
                 'ceilunit': ceilunit, 'lended': lended, 'borrowed': borrowed, 'interface': 'wan'})

    # print arrlan
    # print arrwan

    #############################################################################################
    ############################################  LAN  ##########################################
    #############################################################################################

    for bitsvalue in arrlan:
        filename = 'rrd/lan%s.rrd' % str(bitsvalue['classid']).replace(':', '-')
        #print filename
        #print bitsvalue
        if not os.path.isfile(filename):
            # if ip == '10-253-1-3':
            # print str(bitsvalue)
            # print datetime.datetime.today()
            dss = []
            rras = []
            rezerva = 25
            ds1 = DS(dsName='rate', dsType='GAUGE', heartbeat=step + rezerva, minval=0)
            ds2 = DS(dsName='ceil', dsType='GAUGE', heartbeat=step + rezerva, minval=0)
            ds3 = DS(dsName='sent', dsType='DERIVE', heartbeat=step + rezerva, minval=0)

            dss.append(ds1)
            dss.append(ds2)
            dss.append(ds3)

            rramin = RRA(cf='AVERAGE', xff=0.9, steps=1, rows=20*60)
            # rra1 = RRA(cf='AVERAGE', xff=0.9, steps=1, rows=hour / (step * 1))
            # # 1 days-worth of one-minute samples --> 60/1 * 24
            # rra2 = RRA(cf='AVERAGE', xff=0.9, steps=12, rows=day / (step * 12))
            # # 7 days-worth of five-minute samples --> 60/5 * 24 * 7
            # rra3 = RRA(cf='AVERAGE', xff=0.9, steps=(5 * min) / step, rows=week / (step * (5 * min) / step))
            # # 30 days-worth of five-minute samples --> 60/60 * 24 * 30
            # rra4 = RRA(cf='AVERAGE', xff=0.9, steps=(10 * min) / step, rows=month / (step * (10 * min) / step))
            # rra5 = RRA(cf='AVERAGE', xff=0.9, steps=(hour * 6) / step, rows=year / (step * (hour * 6) / step))
            # #rras.extend([rra1, rra2, rra3, rra4, rra5])
            # rras.append(rra1)
            # rras.append(rra2)
            # rras.append(rra3)
            # rras.append(rra4)
            # rras.append(rra5)
            rras.append(rramin)


            #print step
            myRRD = RRD(filename, ds=dss, rra=rras, start=now, step=step)
            myRRD.create()



        # print filename
        myRRD = RRD(filename)
        # now=int(time.time())
        i = 0
        # for item in bitsvalue['values']:
        #print item
        try:
            myRRD.bufferValue(int(time.time()), unitsconvert(bitsvalue['rate'], bitsvalue['rateunit']),
                              unitsconvert(bitsvalue['ceil'], bitsvalue['ceilunit']), int(bitsvalue['sent']))
        except:
            print 'neulozila se data do rrd'
            print item
        myRRD.update()

    #############################################################################################
    ############################################  WAN  ##########################################
    #############################################################################################

    for bitsvalue in arrwan:
        filename = 'rrd/wan%s.rrd' % str(bitsvalue['classid']).replace(':', '-')
        #print filename
        #print bitsvalue
        if not os.path.isfile(filename):
            # if ip == '10-253-1-3':
            # print str(bitsvalue)
            # print datetime.datetime.today()
            dss = []
            rras = []
            rezerva = 25
            ds1 = DS(dsName='rate', dsType='GAUGE', heartbeat=step + rezerva, minval=0)
            ds2 = DS(dsName='ceil', dsType='GAUGE', heartbeat=step + rezerva, minval=0)
            ds3 = DS(dsName='sent', dsType='DERIVE', heartbeat=step + rezerva, minval=0)

            dss.append(ds1)
            dss.append(ds2)
            dss.append(ds3)

            rramin = RRA(cf='AVERAGE', xff=0.9, steps=1, rows=20*60)
            # rra1 = RRA(cf='AVERAGE', xff=0.9, steps=1, rows=hour / (step * 1))
            # # 1 days-worth of one-minute samples --> 60/1 * 24
            # rra2 = RRA(cf='AVERAGE', xff=0.9, steps=12, rows=day / (step * 12))
            # # 7 days-worth of five-minute samples --> 60/5 * 24 * 7
            # rra3 = RRA(cf='AVERAGE', xff=0.9, steps=(5 * min) / step, rows=week / (step * (5 * min) / step))
            # # 30 days-worth of five-minute samples --> 60/60 * 24 * 30
            # rra4 = RRA(cf='AVERAGE', xff=0.9, steps=(10 * min) / step, rows=month / (step * (10 * min) / step))
            # rra5 = RRA(cf='AVERAGE', xff=0.9, steps=(hour * 6) / step, rows=year / (step * (hour * 6) / step))
            # #rras.extend([rra1, rra2, rra3, rra4, rra5])
            # rras.append(rra1)
            # rras.append(rra2)
            # rras.append(rra3)
            # rras.append(rra4)
            # rras.append(rra5)
            rras.append(rramin)


            #print step
            myRRD = RRD(filename, ds=dss, rra=rras, start=now, step=step)
            myRRD.create()



        # print filename
        myRRD = RRD(filename)
        # now=int(time.time())
        i = 0
        # for item in bitsvalue['values']:
        #print item
        try:
            myRRD.bufferValue(int(time.time()), unitsconvert(bitsvalue['rate'], bitsvalue['rateunit']),
                              unitsconvert(bitsvalue['ceil'], bitsvalue['ceilunit']), int(bitsvalue['sent']))
        except:
            print 'neulozila se data do rrd'
            print item
        myRRD.update()


if trafic:
    filenam = 'readtcclasspid'
    soubor = file(filenam, 'w')
    soubor.write(str(os.getpid()))
    soubor.close()

    # print os.getpid()

    zabralo = step
    if not os.path.isdir('rrd'):
        subprocess.Popen(['mkdir rrd'], shell=True, stdout=subprocess.PIPE).communicate()[0]
    subprocess.Popen(['rm rrd/*'], shell=True, stdout=subprocess.PIPE).communicate()[0]
    while True:
        time.sleep(zabralo)
        start = datetime.datetime.today()
        feedfile()
        zabralo = datetime.datetime.today() - start
        zabralo = (float(zabralo.microseconds) / 1000000)
        print str (zabralo) + ' sec.'
        zabralo=step-zabralo
        # if zabralo < step:
        #     zabralo = step

