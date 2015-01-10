'''
Created on Dec 23, 2014

@author: hluo
'''

from collections import namedtuple
from numpy import nan

class BookBuilder:
    ''' class to build a book from interpreted exchange FIX messages '''
    
    leveldata = namedtuple("booklvl", ["price", "size", "numord"])
    nonetuple = leveldata(nan, nan, nan)
    
    def __init__(self, instrumentid, numlevels):
        self.instrumentid = instrumentid
        self.numlevels = numlevels
        self.bid = [self.nonetuple] * numlevels
        self.ask = [self.nonetuple] * numlevels
        
        self.tradecount = 0
        
    def printBook(self):
        print(' '*9 + 'bid   ask' + ' '*9)        
        for i in range(self.maxlevel):
            linestr = (' '*13 if self.bid[i] == self.nonetuple else 
                       '{0:>4d} {1:>7.2f} '.format(self.bid[i].size, self.bid[i].price))
            linestr += (('@'+' '*13) if self.ask[i] == self.nonetuple else 
                        '@ {0:>7.2f} {1:>4d}'.format(self.ask[i].price, self.ask[i].size))
            print(linestr)
        
    def process(self, tempid, incoming):
        if tempid == 32:
            self.processBookUpd(incoming)
        elif tempid == 42:
            self.processTrade(incoming)
        elif tempid == 38:
            self.refreshFromSnap(incoming)
        else:
            return
            print('passing tempid {}'.format(tempid))
        
    def processBookUpd(self, entry):
        
        if entry.MDEntryType == 'Bid':
            side = self.bid            
        elif entry.MDEntryType == 'Offer':
            side = self.ask        
        else:
            raise Exception('Unknown entry type {}'.format(entry.EntryType))
        # update book
        if entry.MDUpdateAction == 'Change':
            side[entry.MDPriceLevel-1] = self.leveldata(entry.MDEntryPx, entry.MDEntrySize, entry.NumberOfOrders)
        elif entry.MDUpdateAction == 'New':
            side.insert(entry.MDPriceLevel-1, self.leveldata(entry.MDEntryPx, entry.MDEntrySize, entry.NumberOfOrders))
            if len(side) > self.numlevels:
                side.pop()
        elif entry.MDUpdateAction == 'Delete':
            side.pop(entry.MDPriceLevel-1)
            side.append(self.nonetuple)
        else:
            raise Exception('Dont know what to do! {}'.format(entry))
        
    def processTrade(self, entry):
        self.tradecount += 1
        if self.tradecount < 20:        
            print(entry.MDEntryPx, entry.MDEntrySize, entry.AggressorSide, entry.NumberOfOrders)
    
    def refreshFromSnap(self, msg):
        ''' from snap messages, make this the current book '''
        self.bid = [self.nonetuple] * self.numlevels
        self.ask = [self.nonetuple] * self.numlevels
        #self.time = msg.TransactTime
        #self.seq = msg.LastMsgSeqNumProcessed
        for e in msg.MDEntries:
            if e.MDEntryType == 'Bid':
                side = self.bid
            elif e.MDEntryType == 'Offer':
                side = self.ask
            elif e.MDEntryType in [ 'ImpliedBid', 'ImpliedOffer', 'EmptyBook' ]:
                print("NEWENTRY!!!!",e)
            else:
                continue
            side[e.MDPriceLevel-1] = self.leveldata(e.MDEntryPx, e.MDEntrySize, e.NumberOfOrders)
