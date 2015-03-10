'''
Created on Dec 23, 2014

@author: hluo
'''

from collections import namedtuple
from numpy import nan

class BookBuilder:
    ''' class to build a book from interpreted exchange FIX messages '''
    
    leveldata = namedtuple("booklvl", ["price", "size", "numord"])
    nonetuple = leveldata(nan, 0, 0)
    
    def __init__(self, numlevels, displayFctr):
        #self.instrumentid = instrumentid
        self.numlevels = numlevels
        self.bid = [self.nonetuple] * numlevels
        self.ask = [self.nonetuple] * numlevels
        self.dispfctr = displayFctr
        
    def printBook(self):
        print(' '*9 + 'bid   ask' + ' '*9)        
        for i in range(self.numlevels):
            linestr = (' '*13 if self.bid[i] == self.nonetuple else 
                       '{0:>4d} {1:>7.2f} '.format(self.bid[i].size, self.bid[i].price))
            linestr += (('@'+' '*13) if self.ask[i] == self.nonetuple else 
                        '@ {0:>7.2f} {1:>4d}'.format(self.ask[i].price, self.ask[i].size))
            print(linestr)

    def processBookUpd(self, entry):
        if entry.MDEntryType == 'Bid':
            side = self.bid            
        elif entry.MDEntryType == 'Offer':
            side = self.ask        
        elif entry.MDEntryType in [ 'ImpliedBid', 'ImpliedOffer' ]:
            return
        else:
            raise Exception('Unknown entry type {}'.format(entry.EntryType))
        # update book
        if entry.MDUpdateAction == 'Change':
            side[entry.MDPriceLevel-1] = self.leveldata(entry.MDEntryPx * self.dispfctr, 
                                                        entry.MDEntrySize, entry.NumberOfOrders)
        elif entry.MDUpdateAction == 'New':
            side.insert(entry.MDPriceLevel-1, self.leveldata(entry.MDEntryPx * self.dispfctr, 
                                                             entry.MDEntrySize, entry.NumberOfOrders))
            if len(side) > self.numlevels:
                side.pop()
        elif entry.MDUpdateAction == 'Delete':
            side.pop(entry.MDPriceLevel-1)
            side.append(self.nonetuple)
        else:
            raise Exception('Dont know what to do! {}'.format(entry))

    def refreshFromSnap(self, msg):
        ''' from snap messages (tempid 38), make this the current book '''
        for i in range(self.numlevels):
            self.bid[i] = self.nonetuple
            self.ask[i] = self.nonetuple
        for e in msg.MDEntries:
            if e.MDEntryType == 'Bid':
                side = self.bid
            elif e.MDEntryType == 'Offer':
                side = self.ask
            elif e.MDEntryType in [ 'ImpliedBid', 'ImpliedOffer' ]:
                continue                
            elif e.MDEntryType in [ 'SessionHighBid', 'SessionLowOffer', 'SettlementPrice',
                                    'OpenInterest', 'TradeVolume', 'ElectronicVolume',
                                    'OpeningPrice', 'Trade', 'TradingSessionHighPrice',
                                    'TradingSessionLowPrice',
                                    'FixingPrice' ]:
                continue
            else:
                # [ 'EmptyBook' ]
                print("NEWENTRY!!!!",e)
                continue
            side[e.MDPriceLevel-1] = self.leveldata(e.MDEntryPx * self.dispfctr, 
                                                    e.MDEntrySize, e.NumberOfOrders)
