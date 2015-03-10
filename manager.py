from mytime import printI64
from cme.instrument import Future, OptMat, Option
from cme.channel import ChannelManager


class GrandManager:
    def __init__(self, names):
        self.channels = { k: ChannelManager(k, self) for k in names }
        self.ready = { k : False for k in names } 
        self.time = 0
        
        self.futures = {}
        self.optmats = {}
        self.options = {}
        
        self.process = self._processInit
        
    def _processInit(self, channelName, trades, hasChanged, time):
        self.time = time
        if False in self.ready.values():
            return
        
        for iid, (tempid, msg) in self.channels['F'].secDefinitions.items():
            if tempid == 27:
                self.futures[iid] = Future(tempid, msg, self.channels['F'].secProcessors[iid].book)
        
        for iid, (tempid, msg) in self.channels['O'].secDefinitions.items():
            if tempid == 41:
                grp, asset, mat = (msg.SecurityGroup.decode('utf-8'), 
                                   msg.Asset.decode('utf-8'), 
                                   msg.MaturityMonthYear)
                uid = msg.Underlyings[0].UnderlyingSecurityID 
                if (grp, asset, mat) not in self.optmats:
                    self.optmats[(grp,asset,mat)] = (OptMat(grp, asset, mat, 
                                                            self.futures[uid], msg))

        for iid, (tempid, msg) in self.channels['O'].secDefinitions.items():
            if tempid == 41:
                self.options[iid] = Option(tempid, msg, self.channels['O'].secProcessors[iid].book)
                grp, asset, mat = (msg.SecurityGroup.decode('utf-8'), 
                                   msg.Asset.decode('utf-8'), 
                                   msg.MaturityMonthYear)
                self.options[iid].updateOptMat(self.optmats[(grp,asset,mat)])                
            else:
                continue
            
        for _, v in self.optmats.items():
            v.organizeOpts()
        #inspector()
        self.process = self._processNormal
        
    def _processNormal(self, channelName, trades, hasChanged, time):
        if time < self.time + 30000000000:
            return
        self.time = time        
        print(printI64(time))
        idx = ('EZ', 'ES', (2015, 3, None, None))
        self.optmats[idx].updateTime(time)
        self.optmats[idx].printImplyVols()
        #inspector()
    
