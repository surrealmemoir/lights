from .decoding import readPacket

class CleanFeedSyncer:
    ''' 
        Provides three callbacks on Incr/Defn/Snap feed update. 
        Callbacks will call with (timestamp, buffer) as received by socket/file
        
        Sends out a clean, synced message stream to the client. 
        In the order of definition --> snap --> incremental.
        
        What goes out is 
        (recvtime, transact_time, tempid, msg)
        
        msg is typically per entry in an incremental message update.
        This is for convenience of future demultiplexing
    '''
    def __init__(self, clientcall):
        self.incrmsg_queue = []
        self.lastseqdict = {}
        
        self.client = clientcall

        self.resetDefn()
        self.resetSnap()
        
        self.activate_call = None
        self.deactivate_call = None
        
    def processIncrPacket(self, packet, recvtime = 0):
        packetseq, packettm, msgs = readPacket(packet, None)
        
        if self.syncstatus < 4:
            self.incrmsg_queue.append( (recvtime, packetseq, msgs) )            
            return
        self._processIncrPacket(recvtime, packetseq, msgs)
    
    def processSnapPacket(self, packet, recvtime = 0):
        ''' should only pick up tempid = 38 '''
        if (not self.syncstatus in [2,3]) or (not self.incrmsg_queue):
            return
        
        packetseq, packettm, msgs = readPacket(packet, [38])
                
        lastincr = min( [msg.LastMsgSeqNumProcessed for tempid, msg in msgs] )
        if (self.syncstatus == 2 and packetseq != 1) or lastincr < self.incrmsg_queue[0][1]:
            return
        
        if packetseq != self.snap_packet_seq + 1:
            print('Gap or looped around while trying to sync snap. {} to {}'.format(self.snap_packet_seq, packetseq))
            self.resetSnap()
            return
        
        self.syncstatus = 3
        self.snap_packet_seq = packetseq        
        
        for (tempid, msg) in msgs:
            self.snaptuple.append( (recvtime, tempid, msg) )
        
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
        
        if len(self.snaptuple) == self.numreport_snap:            
            print('Done collection snaps')
            self.snap_consistent = (self.min_incr_packet_seq == self.max_incr_packet_seq)
            self.flushDefnSnap()
    
    def processDefnPacket(self, packet, recvtime = 0):
        if self.syncstatus > 1:
            return
        packetseq, packettm, msgs = readPacket(packet, [27, 29, 41])
        
        if self.syncstatus == 0 and (packetseq != 1):
            return
        if packetseq != self.defn_packet_seq + 1:
            self.resetDefn()
            print('Gapped/Looped around without finishing prev {} cur{}'.format(self.defn_packet_seq, packetseq))
        self.syncstatus = 1
        self.defn_packet_seq = packetseq
        
        for tempid, msg in msgs:
            self.rawtuple.append( (recvtime, tempid, msg) )            
            if self.numreport_defn is None:
                self.numreport_defn = msg.TotNumReports                
            elif self.numreport_defn != msg.TotNumReports:
                raise Exception('Conflicting numreport_snap prev {} cur {}'.format(self.numreport_defn, msg.TotNumReports))
                
        if len(self.rawtuple) == self.numreport_defn:
            print('Done collecting definition')
            self.syncstatus = 2
    
    def flushDefnSnap(self):
        lastdefntime1 = max([msg.LastUpdateTime for recvtime, tempid, msg in self.rawtuple]) 
        lastdefntime2 = max([ msg.LastUpdateTime for recvtime, tempid, msg in self.snaptuple ])
        if lastdefntime1 != lastdefntime2:
            print('Missing definitions. Reset')
            self.resetDefn()
            self.resetSnap()
            return
        assert len( { msg.SecurityID for recvtime, tempid, msg 
                      in self.rawtuple} ) == self.numreport_defn, 'Defn Num Bad match'
        assert len( { msg.SecurityID for recvtime, tempid, msg 
                      in self.snaptuple} ) == self.numreport_snap, 'Snap Num Bad match'
        
        print('All Definition Reports: ', self.numreport_defn)
        print('All Snap Reports: ', self.numreport_snap)
        
        for recvtime, tempid, msg in self.rawtuple:
            self.client(recvtime, msg.LastUpdateTime, tempid, msg)            
            self.lastseqdict[msg.SecurityID] = 0
        
        for recvtime, tempid, msg in self.snaptuple:
            self.client(recvtime, msg.TransactTime, tempid, msg)
            self.lastseqdict[msg.SecurityID] = msg.RptSeq  
        
        while self.incrmsg_queue:
            recvtime, pseq, msgs = self.incrmsg_queue.pop(0)
            if pseq <= self.min_incr_packet_seq:
                continue
            self._processIncrPacket(recvtime, pseq, msgs)
                
        if self.deactivate_call:
            print('deactivating')
            self.deactivate_call()        
        self.syncstatus = 4
        self.snap_consistent = True
        
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
        self.rawtuple = []
        
    def resetSnap(self):
        if self.syncstatus > 2:
            self.syncstatus = 2
        
        self.min_incr_packet_seq = 0
        self.max_incr_packet_seq = 0
        self.snap_packet_seq = 0
        self.numreport_snap = None
        self.snaptuple = []        
    
    def _processIncrPacket(self, recvtime, packetseq, msgs):
        if packetseq != self.min_incr_packet_seq + 1:
            print('Packet Gaps when procesing incremental')
            self.resetSnap()
            if self.activate_call:
                self.activate_call()
            return
        self.min_incr_packet_seq += 1
        if self.snap_consistent:
            for tempid, msg in msgs:
                self._processIncrMsgFast(recvtime, tempid, msg)                
        else:
            for tempid, msg in msgs:
                self._processIncrMsgSlow(recvtime, tempid, msg)
        
    def _processIncrMsgFast(self, recvtime, tempid, msg):        
        if tempid in [32, 33, 34, 35, 37, 42]:            
            for e in getattr(msg, 'MDEntries' + str(tempid)):
                self.lastseqdict[e.SecurityID] = e.RptSeq                    
                self.client(recvtime, msg.TransactTime, tempid, e)            
        elif tempid in [27, 29, 41]:
            self.lastseqdict[msg.SecurityID] = 0            
            self.client(recvtime, msg.LastUpdateTime, tempid, msg)
        elif tempid == 30:            
            self.client(recvtime, msg.TransactTime, tempid, msg)
        elif tempid == 39:
            for e in msg.RelatedSym:
                self.client(recvtime, msg.TransactTime, tempid, e)   
        else:
            ''' unimportant messages '''
            print(msg)
            self.client(recvtime, 0, tempid, msg)            
    
    def _processIncrMsgSlow(self, recvtime, tempid, msg):
        ''' Checks per ID sequence number and reports gaps per ID '''
        if tempid in [32, 33, 34, 35, 37, 42]:
            for e in getattr(msg, 'MDEntries' + str(tempid)):
                if e.RptSeq < self.lastseqdict[e.SecurityID] + 1:
                    continue
                assert e.RptSeq == self.lastseqdict[e.SecurityID] + 1, \
                       'Gap at ID level! id {} prev {} seq {}'.format( e.SecurityID, self.lastseqdict[e.SecurityID], 
                                                                       e.RptSeq )
                self.client(recvtime, msg.TransactTime, tempid, e)
                self.lastseqdict[e.SecurityID] += 1                
        elif tempid in [27, 29, 41]:
            self.lastseqdict[msg.SecurityID] = 0                 
            self.client(recvtime, msg.LastUpdateTime, tempid, msg)
        elif tempid == 30:
            self.client(recvtime, msg.TransactTime, tempid, msg)
        elif tempid == 39:
            for e in msg.RelatedSym:
                self.client(recvtime, msg.TransactTime, tempid, e)
        else:
            ''' unimportant messages '''
            print(msg)
            self.client(recvtime, 0, tempid, msg)
          
class DeMultiplexer:
    def __init__(self, client_creator, **kwargs):
        self.clients = {}
        self.client_creator = client_creator
        self.kwargs = kwargs
        self.instrumentManager = 0 
        
    def __call__(self, recvtime, transtime, tempid, msg):
        if tempid in [27, 29, 41]:
            #self.instrumentManager.update(msg)
            if msg.SecurityID not in self.clients:
                self.clients[msg.SecurityID] = self.client_creator(tempid, msg, **self.kwargs)
            else:
                raise Exception('Need to have definition first')
        elif tempid == 30:
            #impactids = self.instrumentManager.lookup(msg)
            impactids = []
            for i in impactids:
                self.clients[i](recvtime, transtime, tempid, msg)
        else:
            self.clients[msg.SecurityID](recvtime, transtime,tempid, msg)

