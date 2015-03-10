import pandas as pd

UnderlyingProduct = {
        2:      'Commodity / Agriculture',
        4:      'Currency',
        5:      'Equity',
        12:     'Other',
        14:     'Interest Rate',
        15:     'FX Cash',
        16:     'Energy',
        17:     'Metal',
        None:   '' }

MatchAlgorithm = {
        'F':    'First In, First Out'
                 }

TickRule = {
        4: ' <-500:25 | -500, 500: 5 | >500: 25 ' }

SecuritySubType = {       
    b'3W' : '3 way',
    b'SP' : 'Calendar spread',
    b'3C' : '3 way straddle vs call',
    b'FX' : 'FX Calendar spread',
    b'3P' : '3 way straddle vs put',
    b'RT' : 'Reduced Tick calendar spread',
    b'BX' : 'Box',
    b'EQ' : 'Equity calendar spread',
    b'BO' : 'Butterfly (options)',
    b'BF' : 'Butterfly (futures)',
    b'XT' : 'Xmas Tree',
    b'CF' : 'Condor',
    b'CC' : 'Conditional Curve',
    b'FS' : 'Strip',
    b'CO' : 'Condor',
    b'IS' : 'Intercommodity spread',
    b'DB' : 'Double',
    b'PK' : 'Pack',
    b'HO' : 'Horizontal',
    b'MP' : 'Month pack',
    b'HS' : 'Horizontal straddle',
    b'PB' : 'Pack butterfly',
    b'IC' : 'Iron Condor',
    b'DF' : 'Double butterfly',
    b'12' : 'Ratio 1X2',
    b'PS' : 'Pack spread',
    b'13' : 'Ratio 1x3',
    b'C1' : 'Crack 1:1',
    b'23' : 'Ratio 2x3',
    b'FB' : 'Bundle',
    b'RR' : 'Risk Reversal',
    b'BS' : 'Bundle spread',
    b'SS' : 'Straddle strip',
    b'IV' : 'Implied Treasury Intercommodity spread',
    b'ST' : 'Straddle',
    b'EC' : 'TAS calendar spread',
    b'SG' : 'Strangle',
    b'SI' : 'Commodities Intercommodity spread',
    b'SR' : 'Sstrip',
    b'MS' : 'BMD futures strip',
    b'VT' : 'Vertical',
    b'SA' : 'Energy Strip',
    b'JR' : 'Jelly roll',
    b'SB' : 'Balanced Strip',
    b'IB' : 'Iron butterfly',
    b'WS' : 'Unbalanced Strip spread',
    b'GT' : 'Guts',
    b'XS' : 'Energy Inter:Commodity Strip',
    b'GN' : 'Generic',
    b'DI' : 'Interest Rate Inter:Commodity Spread',
    b'SA' : 'Energy strip',    
    b'SD' : 'Reduced Tick FX calendar spread',
    b'DG' : 'Calendar diagonal',    
    b'IN' : 'Invoice Swap',
    b'FO' : 'Covered option outright'
    }


def createFutures(futmsgs):
    columns = [ 'UnderlyingProduct', 'SecurityExchange', 'SecurityGroup', 'Asset', 'Symbol',
                'SecurityID', 'SecurityType', 'CFICode', 'Maturity', 'Currency', 'MatchAlgorithm',
                'MinTradeVol', 'MaxTradeVol', 'MinTick', 'UnitOfMeasure', 'ContractSize',
                'ReferencePrice', 'SettlPriceType', 'OpenInterest', 'ClearedVolume', 
                'HighLimitPrice', 'LowLimitPrice', 'MaxPriceVariation', 'UserDefined',
                'Activation', 'LastTradeTime', 'MarketDepth' ]
    futs = []
    for msg in futmsgs:
        dispfctr = msg.DisplayFactor
        activation, lasttrd, depth = None, None, None
        for e in msg.Events:
            if e.EventType == 'Activation':
                activation = e.EventTime
            elif e.EventType == 'LastEligibleTradeDate':
                lasttrd = e.EventTime
            else:
                print(e)
        for e in msg.MDFeedTypes:
            if e.MDFeedType == b'GBX':
                depth = e.MarketDepth
            else:
                print(e)
        
        a = ( UnderlyingProduct[msg.UnderlyingProduct],
              msg.SecurityExchange.decode('utf-8'),
              msg.SecurityGroup.decode('utf-8'),
              msg.Asset.decode('utf-8'),
              msg.Symbol.decode('utf-8'),
              msg.SecurityID,
              msg.SecurityType.decode('utf-8'),
              msg.CFICode.decode('utf-8'),
              msg.MaturityMonthYear,
              msg.Currency.decode('utf-8'),
              msg.MatchAlgorithm.decode('utf-8'),
              msg.MinTradeVol,
              msg.MaxTradeVol,
              msg.MinPriceIncrement * dispfctr,
              msg.UnitOfMeasure.decode('utf-8'),
              msg.UnitofMeasureQty,
              msg.TradingReferencePrice * dispfctr,
              msg.SettlPriceType,  # Explanation
              msg.OpenInterestQty,
              msg.ClearedVolume,
              None if msg.HighLimitPrice is None else msg.HighLimitPrice * dispfctr,
              None if msg.LowLimitPrice is None else msg.LowLimitPrice * dispfctr,
              None if msg.MaxPriceVariation is None else msg.MaxPriceVariation * dispfctr,
              msg.UserDefinedInstrument.decode('utf-8'),
              activation,
              lasttrd,
              depth
              )
        futs.append(a)
    return pd.DataFrame(futs, columns = columns)

def createSpreads(sprdmsgs):
    columns = [ 'UnderlyingProduct', 'SecurityExchange', 'SecurityGroup', 'Asset', 'Symbol',
                'SecurityID', 'SecurityType', 'CFICode', 'Maturity', 'SecuritySubType', 'Currency', 
                'MatchAlgorithm',
                'MinTradeVol', 'MaxTradeVol', 'MinTick', 'TickRule', 'UnitOfMeasure',
                'ReferencePrice', 'SettlPriceType', 'OpenInterest', 'ClearedVolume', 
                'HighLimitPrice', 'LowLimitPrice', 'MaxPriceVariation', 'UserDefined',
                'Activation', 'LastTradeTime', 'MarketDepth', 'Legs' ]
    sprds = []
    for msg in sprdmsgs:
        dispfctr = msg.DisplayFactor
        activation, lasttrd, depth = None, None, None
        for e in msg.Events:
            if e.EventType == 'Activation':
                activation = e.EventTime
            elif e.EventType == 'LastEligibleTradeDate':
                lasttrd = e.EventTime
            else:
                print(e)
        for e in msg.MDFeedTypes:
            if e.MDFeedType == b'GBX':
                depth = e.MarketDepth
            else:
                print(e)
        legs = '|'.join( [ str(e.LegSecurityID) + '=' + 
                           str(e.LegRatioQty * ( 1 if e.LegSide == 'BuySide' else -1 )) 
                           for e in msg.Legs ] )
        a = ( UnderlyingProduct[msg.UnderlyingProduct],
              msg.SecurityExchange.decode('utf-8'),
              msg.SecurityGroup.decode('utf-8'),
              msg.Asset.decode('utf-8'),
              msg.Symbol.decode('utf-8'),
              msg.SecurityID,
              msg.SecurityType.decode('utf-8'),
              msg.CFICode.decode('utf-8'),
              msg.MaturityMonthYear,
              SecuritySubType[msg.SecuritySubType] if msg.SecuritySubType in SecuritySubType else msg.SecuritySubType.decode('utf-8'),
              msg.Currency.decode('utf-8'),
              msg.MatchAlgorithm.decode('utf-8'),
              msg.MinTradeVol,
              msg.MaxTradeVol,
              msg.MinPriceIncrement * dispfctr,
              msg.TickRule,
              msg.UnitOfMeasure.decode('utf-8'),
              msg.TradingReferencePrice * dispfctr,
              msg.SettlPriceType,  # Explanation
              msg.OpenInterestQty,
              msg.ClearedVolume,
              None if msg.HighLimitPrice is None else msg.HighLimitPrice * dispfctr,
              None if msg.LowLimitPrice is None else msg.LowLimitPrice * dispfctr,
              None if msg.MaxPriceVariation is None else msg.MaxPriceVariation * dispfctr,
              msg.UserDefinedInstrument.decode('utf-8'),
              activation,
              lasttrd,
              depth,
              legs
              )
        sprds.append(a)
    return pd.DataFrame(sprds, columns = columns)

def createOptions(optmsgs):
    columns = [ 'UnderlyingProduct', 'SecurityExchange', 'SecurityGroup', 'Asset', 'Symbol',
                'SecurityID', 'SecurityType', 'CFICode', 'Maturity', 'StrikePrice', 'Currency', 
                'MatchAlgorithm', 'MinTradeVol', 'MaxTradeVol', 'MinTick', 
                'TickRule', 'PutOrCall', 'MinCabPrice', 'UnitOfMeasure', 'ContractSize',
                'ReferencePrice', 'SettlPriceType', 'OpenInterest', 'ClearedVolume', 
                'HighLimitPrice', 'LowLimitPrice', 'UserDefined',
                'Activation', 'LastTradeTime', 'MarketDepth', 'Underlying' ]
    opts = []
    for msg in optmsgs:
        dispfctr = msg.DisplayFactor
        activation, lasttrd, depth = None, None, None
        for e in msg.Events:
            if e.EventType == 'Activation':
                activation = e.EventTime
            elif e.EventType == 'LastEligibleTradeDate':
                lasttrd = e.EventTime
            else:
                print(e)
        for e in msg.MDFeedTypes:
            if e.MDFeedType == b'GBX':
                depth = e.MarketDepth
            else:
                print(e)
        underlying = msg.Underlyings[0].UnderlyingSecurityID
        a = ( UnderlyingProduct[msg.UnderlyingProduct],
              msg.SecurityExchange.decode('utf-8'),
              msg.SecurityGroup.decode('utf-8'),
              msg.Asset.decode('utf-8'),
              msg.Symbol.decode('utf-8'),
              msg.SecurityID,
              msg.SecurityType.decode('utf-8'),
              msg.CFICode.decode('utf-8'),
              msg.MaturityMonthYear,
              msg.StrikePrice * dispfctr,
              msg.Currency.decode('utf-8'),
              msg.MatchAlgorithm.decode('utf-8'),
              msg.MinTradeVol,
              msg.MaxTradeVol,
              None if msg.MinPriceIncrement is None else msg.MinPriceIncrement * dispfctr,              
              msg.TickRule,
              msg.PutOrCall,
              msg.MinCabPrice * dispfctr,
              msg.UnitOfMeasure.decode('utf-8'),
              msg.UnitofMeasureQty,
              msg.TradingReferencePrice * dispfctr,
              msg.SettlPriceType,  # Explanation
              msg.OpenInterestQty,
              msg.ClearedVolume,
              None if msg.HighLimitPrice is None else msg.HighLimitPrice * dispfctr,
              None if msg.LowLimitPrice is None else msg.LowLimitPrice * dispfctr,
              msg.UserDefinedInstrument.decode('utf-8'),
              activation,
              lasttrd,
              depth,
              underlying
              )
        opts.append(a)
    return pd.DataFrame(opts, columns = columns)


def createDefinitionFile(defnmsgs):
    futmsgs = [e[2] for e in defnmsgs if e[1] == 27]
    optmsgs = [e[2] for e in defnmsgs if e[1] == 41]
    sprdmsgs = [e[2] for e in defnmsgs if e[1] == 29]
    #inspector()
    
    fut = createFutures(futmsgs) if futmsgs else None
    opt = createOptions(optmsgs) if optmsgs else None
    sprd = createSpreads(sprdmsgs) if sprdmsgs else None
    
    return fut, opt, sprd
    if futmsgs:
        createFutures(futmsgs).to_csv('/home/hluo/temp.csv', index=False)
    if optmsgs:
        createOptions(optmsgs).to_csv('/home/hluo/temp.csv', index=False)
    if sprdmsgs:
        createSpreads(sprdmsgs).to_csv('/home/hluo/temp1.csv', index=False)
        
class Instrument:
    def __init__(self, defn, book):
        self.iid = defn.SecurityID
        self.group = defn.SecurityGroup.decode('utf-8')
        self.asset = defn.Asset.decode('utf-8')
        self.symbol = defn.Symbol.decode('utf-8')
        self.book = book
    
    def __str__(self):
        return 'Group: {}, Asset: {}, Symbol: {}, ID: {}'.format(self.group, self.asset,
                                                                 self.symbol, self.iid)
    
    def getBidPrice(self):
        return self.book.bid[0].price
    
    def getAskPrice(self):
        return self.book.ask[0].price
    
    def getMidPrice(self):
        return 0.5 * (self.book.bid[0].price + self.book.ask[0].price)
    

class Future(Instrument):
    def __init__(self, tempid, defn, book):
        assert tempid == 27, 'Not a Future'
        Instrument.__init__(self, defn, book)
        self.maturity = defn.MaturityMonthYear
        for e in defn.Events:
            if e.EventType == 'LastEligibleTradeDate':
                expiry = e.EventTime        
        self.matTime = expiry
    
    def __str__(self):
        mat = (self.maturity[0], self.maturity[1])
        return ( Instrument.__str__(self) + '\n' + 
                 'Future, Mat: {}, Time: {}'.format(mat, printI64(self.matTime)) ) 
        
    def getExpiration(self, curtm):
        return max(0, (self.matTime - curtm) / (365 * 24 * 60 * 60 * (10 ** 9)))
    
    def getQuoteImbalance(self):
        return 0

class VolSurface:
    pass

class OptMat:
    def __init__(self, grp, asset, mat, ul, repDefn):
        self.group = grp
        self.asset = asset
        self.maturity = mat
        self.underlying = ul
        for e in repDefn.Events:
            if e.EventType == 'LastEligibleTradeDate':
                expiry = e.EventTime        
        self.matTime = expiry
        
        self.call_options = []
        self.put_options = []
        self.strikes = []
        
        self.fwd = 1
        self.tbiz = 0
        self.volmodel = 0
        self.volparam = 0
    
    def organizeOpts(self):
        self.call_options.sort(key=lambda x: x.strike)
        self.put_options.sort(key=lambda x: x.strike)
        cstrk = [ x.strike for x in self.call_options ]
        pstrk = [ x.strike for x in self.put_options ]
        if cstrk != pstrk:
            raise Exception('Call strike and put strike not the same')
        else:
            self.strikes = cstrk
        
    def getStrikeVol(self, strike):
        return 0
    
    def updateFwd(self, fwd):
        if isinstance(self.underlying, Future):
            self.fwd = self.underlying.getMidPrice()
        else:
            raise NotImplementedError('Unknown Underlying Type')
    
    def updateTime(self, curtm):
        self.tbiz = (self.matTime - curtm) / (365 * 24 * 60 * 60 * (10 ** 9))
        print(self.tbiz)
        
    def printImplyVols(self):
        for i, k in enumerate(self.strikes):
            cbid, cask = self.call_options[i].calcImplyVols()
            pbid, pask = self.put_options[i].calcImplyVols()
            print('{0:>6.4f} @ {1:>6.4f} c {2:>7.2f} p {3:>6.4f} @ {4:>6.4f}'.format(cbid, cask, k, pbid, pask))
        
from pricer import BSEuropeanImplyVol

class Option(Instrument):
    def __init__(self, tempid, defn, book):
        assert tempid == 41, 'Not an Option'
        Instrument.__init__(self, defn, book)
        #self.optmat = 0
        self.cfi = defn.CFICode.decode('utf-8')
        self.strike = defn.StrikePrice * defn.DisplayFactor
        
        self.impbid = 0
        self.impask = 0
        self.fitvol = 0
        self.theo = 0
    
    def __str__(self):
        mat = (self.optmat.maturity[0], self.optmat.maturity[1])
        return ( Instrument.__str__(self) + '\n' + 
                 'Option, Mat: {}, Strk: {}, Time: {}'.format(mat, self.strike, 
                                                              printI64(self.optmat.matTime)) )
        
    def updateOptMat(self, optmat):
        self.optmat = optmat
        optlist = optmat.call_options if self.isCall() else optmat.put_options
        optlist.append(self)
        
    def getUnderlying(self):
        return self.optmat.underlying
    
    def isCall(self):
        return self.cfi[1] == 'C'
    
    def isEuropean(self):
        return self.cfi[2] == 'E'
    
    def calcImplyVols(self):
        bid = self.getBidPrice()
        ask = self.getAskPrice()
        ul = self.optmat.underlying.getMidPrice()
        bidvol = BSEuropeanImplyVol(bid, ul, 
                                    self.strike, self.optmat.tbiz, 0, 0, 0, self.isCall())
        askvol = BSEuropeanImplyVol(ask, ul, 
                                    self.strike, self.optmat.tbiz, 0, 0, 0, self.isCall())
        #print(bid, ask, ul, self.strike, self.optmat.tbiz, bidvol, askvol)
        #inspector()
        #bidvol = implyVol(self.optmat.fwd, self.strike, bid,
        #                  self.optmat.tbiz, self.isCall())
        return bidvol, askvol
