'''
Decoding CME.
For message formats, see ftp://ftp.cmegroup.com/SBEFix/Production/Templates/templates_FixBinary.xml
and http://www.cmegroup.com/confluence/display/EPICSANDBOX/MDP3+Message+Specification

To figure out:
Matching Algorithm
http://www.cmegroup.com/confluence/display/EPICSANDBOX/Matching+Algorithms

Tick Rule / Cabinet Price / Settlement / Opening
http://www.cmegroup.com/confluence/display/EPICSANDBOX/Pricing
http://www.cmegroup.com/confluence/display/EPICSANDBOX/MDP3+Variable+Tick+Table

Definition:
http://www.cmegroup.com/confluence/display/EPICSANDBOX/Market+Data+-+Security+Definition

For FLOAT/INTPRICE distinctions, check:
http://www.cmegroup.com/confluence/display/EPICSANDBOX/MDP3+-+Security+Definition

MDP3 Message Specification
http://www.cmegroup.com/confluence/display/EPICSANDBOX/MDP3+-+Market+Data+Snapshot+Full+Refresh
'''

import struct

from .typeinfo import *

PRICEEXP = 10000000

pxmult = 0.01


def readPacket(packet, id_to_process):
    ''' In the future, break down into readPacketHdr and readPacketBody, for now always read whole '''
    #Packet header, sequence and sending time
    packetmsg = []
    packetseq, packettm = struct.unpack("<IQ",packet[0:12])
    curlen = 12
    while curlen < len(packet):
        msgsz, blocklen, tempid, schemaid, ver = struct.unpack("<HHHHH",packet[curlen:curlen+10])
        if (id_to_process is None) or (tempid in id_to_process):
            packetmsg.append(( tempid, readMessage[tempid](packet[curlen+10 : curlen+msgsz]) ))
        curlen += msgsz
    assert curlen == len(packet), 'Bad Packet Reading'         
    return packetseq, packettm, packetmsg

def readBookUpdate(fixmsg):
    ''' tempid = 32 '''
    transact_tm, matcheventindicator_bm = struct.unpack("<QBxx", fixmsg[0:11])
    grplen, numgrp = struct.unpack("<HB",fixmsg[11:14])
    msglist = []
    assert len(fixmsg) == 14+grplen*numgrp, 'Bad Message Reading'
    for i in range(14, 14+grplen*numgrp, grplen):
        px, sz, iid, mktdata_seq, numord, booklvl, act, entrytype = \
            struct.unpack("<qiiIiBBcxxxxx", fixmsg[i : i + grplen])
        px = (px // PRICEEXP if px != 9223372036854775807 else None)
        sz = (sz if sz != 2147483647 else None)
        numord = (numord if numord != 2147483647 else None)
        msglist.append(MDEntries32(iid, mktdata_seq, px, sz, numord, booklvl, 
                                         MDUpdateAction[act], MDEntryTypeBook[entrytype]))
    return MDIncrementalRefreshBook32(transact_tm, matcheventindicator_bm, msglist)

def readVolumeUpdate(fixmsg):
    ''' tempid = 37 '''
    transact_tm, matcheventindicator_bm = struct.unpack("<QBxx", fixmsg[0:11])
    grplen, numgrp = struct.unpack("<HB",fixmsg[11:14])
    msglist = []
    assert len(fixmsg) == 14+grplen*numgrp, 'Bad Message Reading'
    for i in range(14, 14+grplen*numgrp, grplen):
        volume, iid, mktdata_seq, act = struct.unpack("<iiIBxxx", fixmsg[i : i + grplen])
        msglist.append(MDEntries37(iid, mktdata_seq, volume, MDUpdateAction[act]))
    return MDIncrementalRefreshVolume37(transact_tm, matcheventindicator_bm, msglist)

def readTradeSummary(fixmsg):
    ''' tempid = 42 '''
    transact_tm, matcheventindicator_bm = struct.unpack("<QBxx", fixmsg[0:11])
    grplen, numgrp = struct.unpack("<HB",fixmsg[11:14])
    grplen2, numgrp2 = struct.unpack("<HxxxxxB",fixmsg[14 + grplen*numgrp : 14 + grplen*numgrp+8])
    tradelist, orderlist = [], []
    assert len(fixmsg) == 14 + grplen*numgrp + 8 + grplen2* numgrp2, 'Bad Message Reading'
    for i in range(14, 14+grplen*numgrp, grplen):
        px, qty, iid, mktdata_seq, numord, AggSide, act = struct.unpack(
                            "<qiiIiBBxxxxxx", fixmsg[i : i + grplen])        
        tradelist.append(MDEntries42(iid, mktdata_seq, px // PRICEEXP, qty, numord, 
                                       AggressorSide[AggSide], MDUpdateAction[act]))
    for i in range(14+grplen*numgrp+8, 14+grplen*numgrp+8+grplen2*numgrp2, grplen2):
        ordid, sz = struct.unpack("<Qixxxx", fixmsg[i : i + grplen2])
        orderlist.append(OrderIDEntries(ordid, sz))
    return MDIncrementalRefreshTradeSummary42(transact_tm, matcheventindicator_bm, tradelist, orderlist)


def readSnapshotMsg(fixmsg):
    ''' tempid = 38 '''
    lastseq, numinstr, secid, secseq, transact_tm, lastupdtm, trddate \
         = struct.unpack("<IIiIQQH", fixmsg[0:34])
    secstatus, highlimpx, lowlimpx, maxpxvar = struct.unpack("<Bqqq",fixmsg[34:59])
    highlimpx = (None if highlimpx == 9223372036854775807 else highlimpx // PRICEEXP)
    lowlimpx = (None if lowlimpx == 9223372036854775807 else lowlimpx // PRICEEXP)
    maxpxvar = (None if maxpxvar == 9223372036854775807 else maxpxvar // PRICEEXP)
    trddate = (None if trddate == 65535 else trddate)
    
    msglist = []
    grplen, numgrp = struct.unpack("<HB",fixmsg[59:62])
    assert len(fixmsg) == 62 + grplen*numgrp, 'Bad Message Reading'
    for i in range(62, 62+grplen*numgrp, grplen):        
        px, sz, numord, booklvl, trdrefdate, openclosesettle, settlpxtype, entrytype = \
            struct.unpack("<qiibHBBc", fixmsg[i : i + grplen])
        px = (None if px == 9223372036854775807 else px // PRICEEXP)
        sz = (None if sz == 2147483647 else sz)
        numord = (None if numord == 2147483647 else numord)
        booklvl = (None if booklvl == 127 else booklvl)
        trdrefdate = (None if trdrefdate == 65535 else trdrefdate)
        openclosesettle = (None if openclosesettle == 255 else OpenCloseSettlFlag[openclosesettle])
        msglist.append(MDEntries38(px, sz, numord, booklvl, trdrefdate, openclosesettle,
                                      settlpxtype, MDEntryType[entrytype]))
    
    return SnapshotFullRefresh38(lastseq, numinstr, secid, secseq, transact_tm, lastupdtm, trddate,
                              SecurityTradingStatus[secstatus], highlimpx, lowlimpx, maxpxvar, msglist)

def readFutureMsg(fixmsg):
    ''' Future Definition, tempid 27 '''    
    # struct.unpack("<cIcQBhBB36ci12cHBBB6ccIIqq", fixmsg[0:107])
    matcheventindicator_bm, numinstr, updact, lasttm, curstate, channelid, mktsegID, prodcomplex \
        = struct.unpack("<BIcQBhBB", fixmsg[0:19])
    exch = fixmsg[19:23].strip(b'\x00')
    secgroup = fixmsg[23:29].strip(b'\x00')
    sec = fixmsg[29:35].strip(b'\x00')
    instrument = fixmsg[35:55].strip(b'\x00')
    iid, = struct.unpack("<i", fixmsg[55:59])
    sectype = fixmsg[59:65].strip(b'\x00')
    cficode = fixmsg[65:71].strip(b'\x00')
    matyyyy, matmm, matdd, matwk = struct.unpack("<HBBB", fixmsg[71:76])
    matyyyy = (None if matyyyy == 65535 else matyyyy)
    matmm = (None if matmm == 255 else matmm)
    matdd = (None if matdd == 255 else matdd)
    matwk = (None if matwk == 255 else matwk)
    mat = (matyyyy, matmm, matdd, matwk)
    curccy = fixmsg[76:79].strip(b'\x00')
    curccy_settle = fixmsg[79:82].strip(b'\x00')
    matchalgo, minvol, maxvol, mintick, dispfctr = struct.unpack("<cIIqq", fixmsg[82:107])
    mintick *= 1e-7
    dispfctr *= 1e-7
    #mintick *= dispfctr 
    mainfrac, subfrac, numdecidisp = struct.unpack("<BBB", fixmsg[107:110])
    mainfrac = (None if mainfrac == 255 else mainfrac)
    subfrac = (None if subfrac == 255 else subfrac)
    numdecidisp = (None if numdecidisp == 255 else numdecidisp)   
    unitofmeasure = fixmsg[110:140].strip(b'\x00')
    contractsz, refpx, settlpricetype, openint, clearvol, highlimpx, lowlimpx, maxpxchng = \
        struct.unpack("<qqBiiqqq", fixmsg[140:189])
    contractsz = (None if contractsz == 9223372036854775807 else contractsz * 1e-7)
    refpx = (None if refpx == 9223372036854775807 else refpx // PRICEEXP)
    openint = (None if openint == 2147483647 else openint)
    clearvol = (None if clearvol == 2147483647 else openint)
    highlimpx = (None if highlimpx == 9223372036854775807 else highlimpx // PRICEEXP)
    lowlimpx = (None if lowlimpx == 9223372036854775807 else lowlimpx // PRICEEXP)
    maxpxchng = (None if maxpxchng == 9223372036854775807 else maxpxchng // PRICEEXP)
    decayqty, decaydate = struct.unpack("<iH", fixmsg[189:195])
    decayqty = (None if decayqty == 2147483647 else decayqty)
    decaydate = (None if decaydate == 65535 else decaydate)
    origctrctsz, ctrctmult, multunit, flowschedtype, minpxincr, userdefinstr = \
         struct.unpack("<iibbqc", fixmsg[195:214])
    origctrctsz = (None if origctrctsz == 2147483647 else origctrctsz)
    ctrctmult = (None if ctrctmult == 2147483647 else ctrctmult)
    multunit = (None if multunit == 127 else multunit)
    flowschedtype = (None if flowschedtype == 127 else flowschedtype)
    minpxincr = (None if minpxincr == 9223372036854775807 else minpxincr * 1e-7)
    
    cur = 214
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    eventlist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        evtype, evtime = struct.unpack("<BQ", fixmsg[i : i+grplen])
        eventlist.append(Events(EventType[evtype], evtime))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    feedtypelist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        mdfeedtype = fixmsg[i : i+3]
        mktdepth, = struct.unpack("<b", fixmsg[i+3 : i+grplen])
        feedtypelist.append(MDFeedTypes(mdfeedtype,mktdepth))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    attribvallist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        attribval, = struct.unpack("<I", fixmsg[i : i+grplen])
        attribvallist.append(InstAttrib(attribval))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    lottypelist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        lottype, minlotsz = struct.unpack("<bi", fixmsg[i : i+grplen])
        minlotsz = (None if minlotsz == 2147483647 else minlotsz // PRICEEXP)
        lottypelist.append(LotTypeRules(lottype, minlotsz))
    cur += grplen*numgrp
    assert cur == len(fixmsg), 'Bad Message Reading'
    return MDInstrumentDefinitionFuture27(matcheventindicator_bm, numinstr, SecurityUpdateAction[updact], lasttm, 
                             SecurityTradingStatus[curstate], 
                             channelid, mktsegID, prodcomplex, exch, secgroup, sec, instrument,
                             iid, sectype, cficode, mat, curccy, curccy_settle, matchalgo, minvol, maxvol, 
                             mintick, dispfctr, mainfrac, subfrac, numdecidisp, unitofmeasure,
                             contractsz, refpx, settlpricetype, openint, clearvol, highlimpx, lowlimpx, 
                             maxpxchng, decayqty, decaydate, origctrctsz, ctrctmult, multunit, flowschedtype, 
                             minpxincr, userdefinstr, tuple(eventlist), tuple(feedtypelist), 
                             tuple(attribvallist), tuple(lottypelist))

def readSpreadMsg(fixmsg):
    ''' Spread Definition, tempid 29 '''
    matcheventindicator_bm, numinstr, updact, lasttm, curstate, channelid, mktsegID, prodcomplex \
        = struct.unpack("<BIcQBhBB", fixmsg[0:19])
    prodcomplex = (None if prodcomplex == 255 else prodcomplex)
    exch = fixmsg[19:23].strip(b'\x00')
    secgroup = fixmsg[23:29].strip(b'\x00')
    sec = fixmsg[29:35].strip(b'\x00')
    instrument = fixmsg[35:55].strip(b'\x00')
    iid, = struct.unpack("<i", fixmsg[55:59])
    sectype = fixmsg[59:65].strip(b'\x00')
    cficode = fixmsg[65:71].strip(b'\x00')
    matyyyy, matmm, matdd, matwk = struct.unpack("<HBBB", fixmsg[71:76])
    matyyyy = (None if matyyyy == 65535 else matyyyy)
    matmm = (None if matmm == 255 else matmm)
    matdd = (None if matdd == 255 else matdd)
    matwk = (None if matwk == 255 else matwk)
    mat = (matyyyy, matmm, matdd, matwk)
    curccy = fixmsg[76:79].strip(b'\x00')
    secsubtype = fixmsg[79:84].strip(b'\x00')
    userdefinstr, matchalgo, minvol, maxvol, mintick, dispfctr = struct.unpack("<ccIIqq", fixmsg[84:110])
    mintick *= 1e-7
    dispfctr *= 1e-7
    pxdispfmt, pxratio, tickrule = struct.unpack("<Bqb", fixmsg[110:120])
    pxdispfmt = (None if pxdispfmt == 255 else pxdispfmt)
    pxratio = (None if pxratio == 9223372036854775807 else pxratio * 1e-7)
    tickrule = (None if tickrule == 127 else tickrule)
    unitofmeasure = fixmsg[120:150].strip(b'\x00')
    refpx, settlpricetype, openint, clearvol, highlimpx, lowlimpx, maxpxchng = \
        struct.unpack("<qBiiqqq", fixmsg[150:191])
    refpx = (None if refpx == 9223372036854775807 else refpx // PRICEEXP)
    openint = (None if openint == 2147483647 else openint)
    clearvol = (None if clearvol == 2147483647 else openint)
    highlimpx = (None if highlimpx == 9223372036854775807 else highlimpx // PRICEEXP)
    lowlimpx = (None if lowlimpx == 9223372036854775807 else lowlimpx // PRICEEXP)
    maxpxchng = (None if maxpxchng == 9223372036854775807 else maxpxchng // PRICEEXP)
    mainfrac, subfrac = struct.unpack("<BB", fixmsg[191:193]) #255 NULL
    mainfrac = (None if mainfrac == 255 else mainfrac)
    subfrac = (None if subfrac == 255 else subfrac)
    
    cur = 193
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur  += 3
    eventlist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        evtype, evtime = struct.unpack("<BQ", fixmsg[i : i+grplen])
        eventlist.append(Events(EventType[evtype], evtime))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    feedtypelist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        mdfeedtype = fixmsg[i : i+3]
        mktdepth, = struct.unpack("<b", fixmsg[i+3 : i+grplen])
        feedtypelist.append(MDFeedTypes(mdfeedtype,mktdepth))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    attribvallist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        attribval, = struct.unpack("<I", fixmsg[i : i+grplen])
        attribvallist.append(InstAttrib(attribval))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    lottypelist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        lottype, minlotsz = struct.unpack("<bi", fixmsg[i : i+grplen])
        minlotsz = (None if minlotsz == 2147483647 else minlotsz // PRICEEXP)
        lottypelist.append(LotTypeRules(lottype, minlotsz))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    leglist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        legid, legside, legratio, legpx, legdelta = struct.unpack("<iBbqi", fixmsg[i : i+grplen])
        legpx = (None if legpx == 9223372036854775807 else legpx // PRICEEXP)
        legdelta = (None if legdelta == 2147483647 else legdelta * 1e-7)
        leglist.append(Legs(legid, LegSide[legside], legratio, legpx, legdelta))
    cur += grplen*numgrp
    assert cur == len(fixmsg), 'Bad Message Reading'
    return MDInstrumentDefinitionSpread29(matcheventindicator_bm, numinstr, SecurityUpdateAction[updact], lasttm, 
                             SecurityTradingStatus[curstate], channelid, mktsegID, prodcomplex, 
                             exch, secgroup, sec, instrument, iid, sectype, cficode, mat, curccy, 
                             secsubtype, userdefinstr, matchalgo, minvol, maxvol, mintick, dispfctr, 
                             pxdispfmt, pxratio, tickrule, unitofmeasure, refpx, settlpricetype, 
                             openint, clearvol, highlimpx, lowlimpx, maxpxchng, mainfrac, subfrac, 
                             tuple(eventlist), tuple(feedtypelist), 
                             tuple(attribvallist), tuple(lottypelist), tuple(leglist))

def readOptionMsg(fixmsg):
    ''' Option Definition, tempid 41 '''
    matcheventindicator_bm, numinstr, updact, lasttm, curstate, channelid, mktsegID, prodcomplex \
        = struct.unpack("<BIcQBhBB", fixmsg[0:19])
    exch = fixmsg[19:23].strip(b'\x00')
    secgroup = fixmsg[23:29].strip(b'\x00')
    sec = fixmsg[29:35].strip(b'\x00')
    instrument = fixmsg[35:55].strip(b'\x00')
    iid, = struct.unpack("<i", fixmsg[55:59])
    sectype = fixmsg[59:65].strip(b'\x00')
    cficode = fixmsg[65:71].strip(b'\x00')
    putcall, matyyyy, matmm, matdd, matwk = struct.unpack("<BHBBB", fixmsg[71:77])
    matyyyy = (None if matyyyy == 65535 else matyyyy)
    matmm = (None if matmm == 255 else matmm)
    matdd = (None if matdd == 255 else matdd)
    matwk = (None if matwk == 255 else matwk)
    mat = (matyyyy, matmm, matdd, matwk)
    curccy = fixmsg[77:80].strip(b'\x00')
    strk, = struct.unpack("<q", fixmsg[80:88])
    strk = (None if strk == 9223372036854775807 else strk // PRICEEXP)
    strkcurccy = fixmsg[88:91].strip(b'\x00') 
    settlcurccy = fixmsg[91:94].strip(b'\x00')
    mincabpx, matchalgo, minvol, maxvol, mintick, minpxincr, dispfctr \
        = struct.unpack("<qcIIqqq", fixmsg[94:135])
    mincabpx = (None if mincabpx == 9223372036854775807 else mincabpx // PRICEEXP)
    mintick = (None if mintick == 9223372036854775807 else mintick * 1e-7)
    minpxincr = (None if minpxincr == 9223372036854775807 else minpxincr * 1e-7)
    dispfctr *= 1e-7
    tickrule, mainfrac, subfrac, pxdispfmt = struct.unpack("<bBBB", fixmsg[135:139])
    tickrule = (None if tickrule == 127 else tickrule)
    mainfrac = (None if mainfrac == 255 else mainfrac)
    subfrac = (None if subfrac == 255 else subfrac)
    pxdispfmt = (None if pxdispfmt == 255 else pxdispfmt)
    unitofmeasure = fixmsg[139:169].strip(b'\x00')
    contractsz, refpx, settlpricetype, clearvol, openint, lowlimpx, highlimpx, userdefinstr = \
        struct.unpack("<qqBiiqqc", fixmsg[169:211])
    contractsz = (None if contractsz == 9223372036854775807 else contractsz * 1e-7)
    refpx = (None if refpx == 9223372036854775807 else refpx // PRICEEXP)
    openint = (None if openint == 2147483647 else openint)
    clearvol = (None if clearvol == 2147483647 else openint)
    highlimpx = (None if highlimpx == 9223372036854775807 else highlimpx // PRICEEXP)
    lowlimpx = (None if lowlimpx == 9223372036854775807 else lowlimpx // PRICEEXP)
    
    cur = 211
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur  += 3
    eventlist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        evtype, evtime = struct.unpack("<BQ", fixmsg[i : i+grplen])
        eventlist.append(Events(EventType[evtype], evtime))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    feedtypelist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        mdfeedtype = fixmsg[i : i+3]
        mktdepth, = struct.unpack("<b", fixmsg[i+3 : i+grplen])
        feedtypelist.append(MDFeedTypes(mdfeedtype,mktdepth))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    attribvallist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        attribval, = struct.unpack("<I", fixmsg[i : i+grplen])
        attribvallist.append(InstAttrib(attribval))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    lottypelist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        lottype, minlotsz = struct.unpack("<bi", fixmsg[i : i+grplen])
        minlotsz = (None if minlotsz == 2147483647 else minlotsz // PRICEEXP)
        lottypelist.append(LotTypeRules(lottype, minlotsz))
    cur += grplen*numgrp
    grplen, numgrp = struct.unpack("<HB",fixmsg[cur : cur+3])
    cur += 3
    ULlist = []
    for i in range(cur, cur+grplen*numgrp, grplen): 
        ULID, = struct.unpack('<i', fixmsg[i : i+4])
        ULsym = fixmsg[i+4 : i+grplen].strip(b'\x00')
        ULlist.append(Underlyings(ULID, ULsym))
    cur += grplen*numgrp
    assert cur == len(fixmsg), 'Bad Message Reading'
    
    return MDInstrumentDefinitionOption41(matcheventindicator_bm, numinstr, SecurityUpdateAction[updact], lasttm, 
                             SecurityTradingStatus[curstate], channelid, mktsegID, prodcomplex, 
                             exch, secgroup, sec, instrument, iid, sectype, cficode, PutOrCall[putcall], mat, 
                             curccy, strk, strkcurccy, settlcurccy, mincabpx,  
                             matchalgo, minvol, maxvol, mintick, minpxincr, dispfctr, tickrule, 
                             mainfrac, subfrac, pxdispfmt, unitofmeasure, contractsz, refpx, 
                             settlpricetype, clearvol, openint, lowlimpx, highlimpx, userdefinstr, 
                             tuple(eventlist), tuple(feedtypelist), 
                             tuple(attribvallist), tuple(lottypelist), tuple(ULlist))

def readStatUpdate(fixmsg):
    ''' tempid = 35 '''
    transact_tm, matcheventindicator_bm = struct.unpack("<QBxx", fixmsg[0:11])
    grplen, numgrp = struct.unpack("<HB",fixmsg[11:14])
    msglist = []
    assert len(fixmsg) == 14+grplen*numgrp, 'Bad Message Reading'
    for i in range(14, 14+grplen*numgrp, grplen):
        px, iid, mktdata_seq, opencloseflag, act, entrytype = \
            struct.unpack("<qiIBBcxxxxx", fixmsg[i : i + grplen])
        msglist.append(MDEntries35(px // PRICEEXP, iid, mktdata_seq, opencloseflag,
                                   MDUpdateAction[act], MDEntryTypeStatistics[entrytype]))
    return MDIncrementalRefreshSessionStatistics35(transact_tm, matcheventindicator_bm, msglist)

def readDailyStatUpdate(fixmsg):
    ''' tempid = 33 '''
    transact_tm, matcheventindicator_bm = struct.unpack("<QBxx", fixmsg[0:11])
    grplen, numgrp = struct.unpack("<HB",fixmsg[11:14])
    msglist = []
    assert len(fixmsg) == 14+grplen*numgrp, 'Bad Message Reading'
    for i in range(14, 14+grplen*numgrp, grplen):
        px, sz, iid, mktdata_seq, trdrefdate, settlpxtype, act, entrytype = \
            struct.unpack("<qiiIHBBcxxxxxxx", fixmsg[i : i + grplen])
        px = (px // PRICEEXP if px != 9223372036854775807 else None)
        sz = (sz if sz != 2147483647 else None)
        trdrefdate = (None if trdrefdate == 65535 else trdrefdate)
        msglist.append(MDEntries33(px, sz, iid, mktdata_seq, trdrefdate, settlpxtype,
                                        MDUpdateAction[act], MDEntryTypeDailyStatistics[entrytype]))
    return MDIncrementalRefreshDailyStatistics33(transact_tm, matcheventindicator_bm, msglist)

def readSecurityStatus(fixmsg):
    ''' tempid = 30 '''
    transact_tm, = struct.unpack('<Q', fixmsg[0:8])
    secgroup = fixmsg[8:14].strip(b'\x00')
    asset = fixmsg[14:20].strip(b'\x00')
    iid, trddate, matcheventindicator_bm, secstatus, haltreason, event2 = \
        struct.unpack("<iHBBBB", fixmsg[20:])
    iid = (None if iid == 2147483647 else iid)
    trddate = (None if trddate == 65535 else trddate)
    
    return SecurityStatus30(transact_tm, secgroup, asset, iid, trddate, 
                                 matcheventindicator_bm, SecurityTradingStatus[secstatus], 
                                 HaltReason[haltreason], SecurityTradingEvent[event2])

def readLimitUpdate(fixmsg):
    ''' tempid = 34 '''
    transact_tm, matcheventindicator_bm = struct.unpack("<QBxx", fixmsg[0:11])
    grplen, numgrp = struct.unpack("<HB",fixmsg[11:14])
    msglist = []
    assert len(fixmsg) == 14+grplen*numgrp, 'Bad Message Reading'
    for i in range(14, 14+grplen*numgrp, grplen):        
        hi, lo, diff, iid, mktdata_seq = struct.unpack("<qqqiI", fixmsg[i : i + grplen])
        hi = (hi // PRICEEXP if hi != 9223372036854775807 else None)
        lo = (lo // PRICEEXP if lo != 9223372036854775807 else None)
        diff = (diff // PRICEEXP if diff != 9223372036854775807 else None)
        msglist.append(MDEntries34(hi, lo, diff, iid, mktdata_seq))
    return MDIncrementalRefreshLimitsBanding34(transact_tm, matcheventindicator_bm, msglist)

def readQuoteRequest(fixmsg):
    ''' tempid = 39 '''
    transact_tm, = struct.unpack("<Q", fixmsg[0:8])
    quotereqID = fixmsg[8:31].strip(b'\x00')
    matcheventindicator_bm, =  struct.unpack("<Bxxx", fixmsg[31:35])
    grplen, numgrp = struct.unpack("<HB",fixmsg[35:38])
    msglist = []
    assert len(fixmsg) == 38+grplen*numgrp, 'Bad Message Reading'
    for i in range(38, 38+grplen*numgrp, grplen):
        sym = fixmsg[i : i+20].strip(b'\x00')
        iid, qty, quotetype, side = struct.unpack('<iibbxx', fixmsg[i+20 : i+grplen])
        qty = (None if qty == 2147483647 else qty)
        side = (None if side == 127 else side)
        msglist.append(RelatedSym(sym, iid, qty, quotetype, side))
    return QuoteRequest39(transact_tm, quotereqID, matcheventindicator_bm, msglist)

def readNull(fixmsg):
    return None

readMessage = {
               4:  readNull,
               12: readNull,
               15: readNull,
               16: readNull,
               27: readFutureMsg,
               29: readSpreadMsg,
               30: readSecurityStatus,
               32: readBookUpdate,
               33: readDailyStatUpdate,
               34: readLimitUpdate,
               35: readStatUpdate,
               36: readNull,
               37: readVolumeUpdate,
               38: readSnapshotMsg,
               39: readQuoteRequest,
               41: readOptionMsg,
               42: readTradeSummary
               }
