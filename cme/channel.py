from .decoding import readPacket
from .bookbuilder import BookBuilder

class SecurityInfo:
    def __init__(self, defnmsg):
        self.volume = 0
        # ticksize = defnmsg.MinPriceIncrement
        # contractsize = defnmsg.UnitofMeasureQty
        _ = ( defnmsg.OpenInterestQty,
              defnmsg.ClearedVolume,
              defnmsg.HighLimitPrice,
              defnmsg.LowLimitPrice )
        for e in defnmsg.MDFeedTypes:
            if e.MDFeedType == b'GBX':
                numlevel = e.MarketDepth
        self.book = BookBuilder(numlevel, defnmsg.DisplayFactor)
        self.tempTrades = []
    
    def process(self, recvtime, transtime, endevent, tempid, msg):
        if tempid == 42:
            self.tempTrades.append( (msg.SecurityID, msg.MDEntryPx * self.book.dispfctr,
                                     msg.MDEntrySize, msg.NumberOfOrders, msg.AggressorSide) )
        elif tempid == 37:
            self.updateVolume(msg.MDEntrySize)
        elif tempid == 32:
            self.updateBook(msg)
        elif tempid == 35:
            self.updateStat(msg)            
        else:
            print(tempid, msg)
        
    def updateSnap(self, snapmsg):
        # tempid = 38
        self.book.refreshFromSnap(snapmsg)
    
    def updateVolume(self, size):
        # tempid = 37
        self.volume = size
        
    def updateBook(self, entry):
        # tempid = 32
        self.book.processBookUpd(entry)
        
    def updateStat(self, entry):
        # tempid = 35
        pass
        
class ChannelManager:
    def __init__(self, name, manager):
        self.inRecovery = True
        self.secProcessorCreator = SecurityInfo
        
        self.secProcessors = {}
        self.secDefinitions = {}
        
        self.tempTrades = []
        self.secChanged = set()
        
        self.stop = False
        
        self.name = name
        self.manager = manager
        self.recovery = MarketRecovery(self)        
    
    def createInstrument(self, tempid, msg):
        self.secProcessors[msg.SecurityID] = self.secProcessorCreator(msg)
        self.secDefinitions[msg.SecurityID] = (tempid, msg)
        '''
        for x in msg.Events:
            if x.EventType == 'LastEligibleTradeDate':
                mat = x.EventTime
        ctrctsz = msg.UnitofMeasureQty if tempid == 27 else 1 
        (
             (msg.SecurityID, msg.UnderlyingProduct, msg.SecurityGroup.decode('utf-8'), 
              msg.Asset.decode('utf-8'), msg.Symbol.decode('utf-8'), msg.CFICode.decode('utf-8'), 
              mat, ctrctsz, msg.DisplayFactor) )
        '''
        
    def onRecovery(self, defnmsgs, snapmsgs, incrpackets, minincrseq):
        #inspector()
        lastseqdict = {}
        for _, tempid, msg in defnmsgs:
            self.createInstrument(tempid, msg)            
        for _, _, e in snapmsgs:
            self.secProcessors[e.SecurityID].updateSnap(e)
            lastseqdict[e.SecurityID] = e.RptSeq      
        #print(lastseqdict)
        #inspector()  
        for recvtime, packetseq, msgs in incrpackets:
            if packetseq <= minincrseq:
                continue
            if packetseq != minincrseq + 1:
                print('Packet Gaps when procesing incremental')
                self.recovery.resetSnap()
                #if self.activate_call:
                #    self.activate_call()
                return
            minincrseq += 1
            for tempid, msg in msgs:
                for e in getattr(msg, 'MDEntries' + str(tempid)):
                    if e.RptSeq <= lastseqdict[e.SecurityID]:
                        continue
                    if tempid == 32:
                        self.secProcessors[e.SecurityID].updateBook(e)
                    elif tempid == 37:
                        self.secProcessors[e.SecurityID].updateVolume(e.MDEntrySize)
                    else:
                        print(e)
        #inspector()
        self.manager.ready[self.name] = True
        '''
        fut, opt, sprd = createDefinitionFile(defnmsgs)
        if fut is not None:
            fut.to_csv('/home/hluo/tempF.csv', index=False)
            asd = 'F'
        if opt is not None:
            opt.to_csv('/home/hluo/tempO.csv', index=False)
            asd = 'O'
        if sprd is not None:
            sprd.to_csv('/home/hluo/tempS' + asd + '.csv', index=False)
        '''
        #inspector()
        self.inRecovery = False
    
    def processIncrFeed(self, buf, recvtime = 0):
        if self.stop:
            return
        if self.inRecovery:
            self.recovery.processIncrFeed(buf, recvtime)
            return
        _, _, msgs = readPacket(buf, None)
        for tempid, msg in msgs:
            self.processMsg(tempid, msg)
            #print('Indicator', msg.MatchEventIndicator)
            if tempid not in [4, 12, 15, 16] and msg.MatchEventIndicator & 128:
                self.processEventEnd(recvtime, msg.TransactTime)
        #self.processPacketEnd()
    
    def processSnapFeed(self, buf, recvtime = 0):
        if self.inRecovery:
            self.recovery.processSnapFeed(buf, recvtime)
    
    def processDefnFeed(self, buf, recvtime = 0):
        if self.inRecovery:
            self.recovery.processDefnFeed(buf, recvtime)
    
    def processMsg(self, tempid, msg):        
        if tempid == 42:
            for e in msg.MDEntries42:
                self.tempTrades.append( (e.SecurityID, e.MDEntryPx * self.secProcessors[e.SecurityID].book.dispfctr,
                                         e.MDEntrySize, e.NumberOfOrders, e.AggressorSide) )
                self.secChanged.add(e.SecurityID)
        elif tempid == 37:
            for e in msg.MDEntries37:
                self.secProcessors[e.SecurityID].updateVolume(e.MDEntrySize)
                self.secChanged.add(e.SecurityID)
        elif tempid == 32:
            for e in msg.MDEntries32:
                self.secProcessors[e.SecurityID].updateBook(e)
                self.secChanged.add(e.SecurityID)            
        elif tempid in [27, 29, 41]:
            self.createInstrument(tempid, msg)
        else:
            return
            print(tempid, msg)
            #inspector()
    
    def processEventEnd(self, recvtime, eventTime):
        #real work
        self.manager.process(self.name, self.tempTrades, self.secChanged, eventTime)
        '''
        if self.tempTrades:
            print('End of Event')
            for e in self.tempTrades:
                print(e)            
            for iid in self.secChanged:
                print(self.secDefinitions[iid])
                self.secProcessors[iid].book.printBook()
        '''    
        #inspector()
        
        #clear
        self.secChanged.clear()        
        self.tempTrades.clear()
        
class MarketRecovery:
    def __init__(self, manager):
        self.manager = manager
        
        self.resetDefn()
        self.resetSnap()
        
    def resetDefn(self):
        '''
        syncstatus: 0 -- defn ready
                    1 -- defn starts(after finding packet 1)
                    2 -- defn ends, snap ready
                    3 -- snap starts(after finding packet 1)
                    4 -- snap ends, incr ready
        '''
        self.syncstatus = 0
        self.defn_packet_seq = 0
        self.numreport_defn = None
        self.defnmsg_queue = []
    
    def resetSnap(self):
        if self.syncstatus > 2:
            self.syncstatus = 2
        
        self.min_incr_packet_seq = 0
        self.max_incr_packet_seq = 0
        self.snap_packet_seq = 0
        self.numreport_snap = None
        self.snapmsg_queue = []
        self.incrpacket_queue = []
    
    def processIncrFeed(self, buf, recvtime = 0):
        packetseq, packettm, msgs = readPacket(buf, None)
        if self.syncstatus < 4:
            self.incrpacket_queue.append( (recvtime, packetseq, msgs) )            
        
    def processSnapFeed(self, buf, recvtime = 0):
        if (not self.syncstatus in [2,3]) or (not self.incrpacket_queue):
            return
        
        packetseq, packettm, msgs = readPacket(buf, [38])
                
        lastincr = min( [msg.LastMsgSeqNumProcessed for tempid, msg in msgs] )
        if (self.syncstatus == 2 and packetseq != 1) or lastincr < self.incrpacket_queue[0][1]:
            return
        
        if packetseq != self.snap_packet_seq + 1:
            print('Gap or looped around while trying to sync snap. {} to {}'.format(self.snap_packet_seq, packetseq))
            self.resetSnap()
            return
        
        self.syncstatus = 3
        self.snap_packet_seq = packetseq
        
        for (tempid, msg) in msgs:
            self.snapmsg_queue.append( (recvtime, tempid, msg) )
        
        totset = {msg.TotNumReports for tempid, msg in msgs}
        assert len(totset) == 1, 'TotNumReports inconsistent within packet.{}'.format(totset)
        numreport = totset.pop()
        if self.numreport_snap and self.numreport_snap != numreport:
            raise Exception('inconsistent snap loop in numreport_snap')
        self.numreport_snap = numreport
        
        assert lastincr >= self.max_incr_packet_seq, 'LastMsgSeqProcessed going backwards in snap syncing'
        if packetseq == 1:
            self.min_incr_packet_seq = lastincr
        self.max_incr_packet_seq = lastincr
        
        if len(self.snapmsg_queue) == self.numreport_snap:            
            print('Done collection snaps')
            self.snap_consistent = (self.min_incr_packet_seq == self.max_incr_packet_seq)
            self.flushDefnSnap()
    
    def processDefnFeed(self, buf, recvtime = 0):
        if self.syncstatus > 1:
            return
        packetseq, packettm, msgs = readPacket(buf, [27, 29, 41])
        
        if self.syncstatus == 0 and (packetseq != 1):
            return
        if packetseq != self.defn_packet_seq + 1:
            self.resetDefn()
            print('Gapped/Looped around without finishing prev {} cur{}'.format(self.defn_packet_seq, packetseq))
        self.syncstatus = 1
        self.defn_packet_seq = packetseq
        
        for tempid, msg in msgs:
            self.defnmsg_queue.append( (recvtime, tempid, msg) )            
            if self.numreport_defn is None:
                self.numreport_defn = msg.TotNumReports                
            elif self.numreport_defn != msg.TotNumReports:
                raise Exception('Conflicting numreport_snap prev {} cur {}'.format(self.numreport_defn, msg.TotNumReports))
                
        if len(self.defnmsg_queue) == self.numreport_defn:
            print('Done collecting definition')
            self.syncstatus = 2
    
    def flushDefnSnap(self):
        lastdefntime1 = max([msg.LastUpdateTime for recvtime, tempid, msg in self.defnmsg_queue]) 
        lastdefntime2 = max([ msg.LastUpdateTime for recvtime, tempid, msg in self.snapmsg_queue ])
        if lastdefntime1 != lastdefntime2:
            print('Missing definitions. Reset')
            self.resetDefn()
            self.resetSnap()
            return
        assert len( { msg.SecurityID for recvtime, tempid, msg 
                      in self.defnmsg_queue} ) == self.numreport_defn, 'Defn Num Bad match'
        assert len( { msg.SecurityID for recvtime, tempid, msg 
                      in self.snapmsg_queue} ) == self.numreport_snap, 'Snap Num Bad match'
        
        print('All Definition Reports: ', self.numreport_defn)
        print('All Snap Reports: ', self.numreport_snap)
        self.syncstatus = 4
        self.manager.onRecovery(self.defnmsg_queue, self.snapmsg_queue, self.incrpacket_queue,
                                self.min_incr_packet_seq)
