#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import os
from tcvars import *
import datetime

from pyrrd.rrd import RRD, RRA, DS
from pyrrd.graph import DEF, CDEF, VDEF
from pyrrd.graph import LINE, AREA, GPRINT, PRINT, COMMENT
from pyrrd.graph import ColorAttributes, Graph


def Tcgraph():
    exampleNum = 1

    min = 60
    hour = 60 * 60
    day = 24 * 60 * 60
    week = 7 * day
    month = day * 30
    quarter = month * 3
    half = 365 * day / 2
    year = 365 * day
    now = int(time.time())

    endTime = now
    startTime = str(now - 600)
    zacalo = datetime.datetime.today()


    #### index pro web
    filenam = wwwpath + 'index.html'
    soubor = file(filenam, 'w')
    soubor.write(wwwhead)

    adr_list = os.listdir('rrd/')
    for adr in adr_list:


        filename = 'rrd/%s' % adr
        print filename
        graphfile = wwwpath + '%s.png' % adr.replace('.rrd', '')
        graphfile_lg = 'graphs/%s.png' % adr.replace('.rrd', '')
        hgraphfile_lg = wwwpath + '%sh.png' % adr.replace('.rrd', '')
        dgraphfile_lg = 'graphs/%sd.png' % adr.replace('.rrd', '')
        wgraphfile_lg = 'graphs/%sw.png' % adr.replace('.rrd', '')
        mgraphfile_lg = 'graphs/%sm.png' % adr.replace('.rrd', '')
        ygraphfile_lg = 'graphs/%sy.png' % adr.replace('.rrd', '')
        now = int(time.time())
        endTime = now
        startTime = str(now - 600)
        myRRD = RRD(filename)

        def1 = DEF(rrdfile=myRRD.filename, vname='dsrate', dsName='rate')
        def2 = DEF(rrdfile=myRRD.filename, vname='dsceil', dsName='ceil')
        def3 = DEF(rrdfile=myRRD.filename, vname='dssent', dsName='sent')

        cdef1 = CDEF(vname='sdsrate', rpn='%s,1,*,FLOOR' % def1.vname)
        cdef2 = CDEF(vname='sdsceil', rpn='%s,1,*,FLOOR' % def2.vname)
        cdef3 = CDEF(vname='sdssent', rpn='%s,8,*,FLOOR' % def3.vname)

        area1 = LINE(defObj=cdef1, color='#468A41', legend='rate', width='2')
        area2 = LINE(defObj=cdef2, color='#d91161', legend='ceil', width='2')
        area3 = AREA(defObj=cdef3, color='#8399f770', legend='sent', width='1')
        # area4 = LINE(defObj=cdef2, color='#468A41', legend='', width='1')

        # vdef1 = VDEF(vname='rate', rpn='%s,TOTAL' % def1.vname)
        # vdef2 = VDEF(vname='ceil', rpn='%s,TOTAL' % def2.vname)

        vdef1 = VDEF(vname='rate', rpn='%s,MAXIMUM' % def1.vname)
        vdef2 = VDEF(vname='ceil', rpn='%s,MAXIMUM' % def2.vname)

        # vdef1 = VDEF(vname='RATE_last', rpn='%s,LAST' % def1.vname)
        # vdef2 = VDEF(vname='RSSI_last', rpn='%s,LAST' % def2.vname)
        # vdef3 = VDEF(vname='CHANN_last', rpn='%s,LAST' % def3.vname)
        # vdef2 = VDEF(vname='myavgtx', rpn='%s,TOTAL' % def1.vname)
        #            gprint1 = GPRINT(vdef1, 'rate %lg%SMbps')
        #            gprint2 = GPRINT(vdef2, 'rssi %lg%SdBm')
        #            gprint3 = GPRINT(vdef3, 'kanal %lg%S')

        gprint1 = GPRINT(vdef1, 'rate %lg %Sbits')
        gprint2 = GPRINT(vdef2, 'ceil %lg %Sbits')
        #gprint3 = GPRINT('2588888', 'ceil %lg %Sbits')

        comment1 = COMMENT('textik')

        ca = ColorAttributes()
        ca.back = '#333333'

        ca.canvas = '#333333'

        ca.shadea = '#000000'
        ca.shadeb = '#111111'
        ca.mgrid = '#CCCCCC'
        ca.axis = '#FFFFFF'
        ca.frame = '#AAAAAA'
        ca.font = '#FFFFFF'
        ca.arrow = '#FFFFFF'

        nadpis = adr + ' - ' + str(datetime.datetime.today())
        graphwidth = 800
        graphheight = 400

        print hgraphfile_lg

        gh = Graph(hgraphfile_lg, start=int(time.time()) - min*20, end=endTime, vertical_label='bits/s', color=ca)
        gh.width = graphwidth

        gh.height = graphheight
        text = nadpis
        text = text.replace(' ', '_')
        gh.title = text
        gh.data.extend([
            def1, def2, def3,
            cdef1, cdef2, cdef3,
            area1, area2, area3,  #area4,
            # area6, area10, area7, area8, area9,
            vdef1, gprint1, vdef2, gprint2, comment1,
        ])

        gh.write()

        if 'lan' in hgraphfile_lg:
            soubor.write('<td><img src="' + str(hgraphfile_lg).replace(wwwpath, '') + '"></td><td><img src="' + str(
                hgraphfile_lg).replace(wwwpath, '').replace('lan', 'wan') + '"></td></tr>')

    soubor.write(wwwfooter)
    soubor.close()

    dobabehu = datetime.datetime.today() - zacalo
    dobabehu = dobabehu.seconds
    print 'Doba zpracování grafů: ' + str(dobabehu) + ' sec.'


Tcgraph()