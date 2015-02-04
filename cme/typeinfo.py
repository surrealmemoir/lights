'''
Created on Dec 22, 2014

@author: hluo
'''

from collections import namedtuple

'''
For convenience

structsyntax = {
                'char':     'c',
                'int8':     'b',
                'int16':    'h',
                'int32':    'i',
                'int64':    'q',
                'uint8':    'B',
                'uint16':   'H',
                'uint32':   'I',
                'uint64':   'Q'
                }


# 'Name': 'primitivetype', 'null(num)/length(char)', 'desc' 
typedict = {
            'Asset'             : ('char',      6,         'Asset'),
            'CFICode'           : ('char',      6,         None),
            'CHAR'              : ('char',      None,      None),
            'Currency'          : ('char',      3,         'Currency'),
            'InstAttribType'    : ('int8',      None,      'Eligibility'),
            'Int8'              : ('int8',      None,      'Int8'),
            'Int16'             : ('int16',     None,      'Int16'),
            'Int32'             : ('int32',     None,      'Int32'),
            'Int8NULL'          : ('int8',      127,       'Int8NULL'),
            'Int32NULL'         : ('int32',     2147483647,'Int32NULL'),
            'uInt8'             : ('uint8',     None,      'uInt8'),
            'uInt32'            : ('uint32',    None,      'uInt32'),
            'uInt64'            : ('uint64',    None,      'uInt64'),
            'uInt32NULL'        : ('uint32',    4294967295,'uInt32NULL'),
            'uInt8NULL'         : ('uint64',    255,       'uInt8NULL'),    
            'DecimalQty'        : ('int32',     2147483647,None),
            'FLOAT'             : ('int64',     None,      None ),
            'PRICE'             : ('int64',     None,      None ),
            'PRICENULL'         : ('int64',     9223372036854775807, None),
            'LocalMktDate'      : ('uint16',    65535,    'LocalMktDate'),
            'MDEntryTypeChannelReset': ('char', 1,        'Channel Reset message entry type'),
            'MDEntryTypeLimits' : ('char',      1,        'MDEntryTypeLimits'),
            'MDEntryTypeTrade'  : ('char',      1,        'MDEntryTypeTrade'),
            'MDEntryTypeVol'    : ('char',      1,        'MDEntryTypeVol'),
            'MDFeedType'        : ('char',      3,        None),
            'MDUpdateActionNew' : ('int8',      None,     'MDUpdateActionNew'),
            'MDUpdateTypeNew'   : ('int8',      None,     'MDUpdateTypeNew'),
            'QuoteReqId'        : ('char',      23,       None),
            'SecurityExchange'  : ('char',      4,        None),
            'SecurityGroup'     : ('char',      6,        None),
            'SecurityIDSource'  : ('char',      1,        'SecurityIDSource'),
            'SecuritySubType'   : ('char',      5,        None),
            'SecurityType'      : ('char',      6,        'SecurityType'),
            'Symbol'            : ('char',      20,       'Symbol'),
            'Text'              : ('char',      180,      'Text'),
            'UnderlyingSymbol'  : ('char',      20,       None),
            'UnitOfMeasure'     : ('char',      30,       None),
            'UserDefinedInstrument': ('char',   1,        None)
            }
'''

# Enumerations
MDUpdateAction = { 
                  0: 'New',
                  1: 'Change',
                  2: 'Delete',
                  3: 'DeleteThru',
                  4: 'DeleteFrom',
                  5: 'Overlay'
                  }

MDEntryTypeBook = {
                   b'0': 'Bid',
                   b'1': 'Offer',
                   b'E': 'ImpliedBid',
                   b'F': 'ImpliedOffer',
                   b'J': 'BookReset'
                   }

MDEntryTypeDailyStatistics = {
                b'6': 'SettlementPrice',
                b'B': 'ClearedVolume',
                b'C': 'OpenInterest',
                b'W': 'FixingPrice'
                }

MDEntryTypeStatistics = {
                b'4': 'OpenPrice',
                b'7': 'HighTrade',
                b'8': 'LowTrade',
                b'N': 'HighestBid',
                b'O': 'LowestOffer'
                }

MDEntryType = {
               b'0': 'Bid',
               b'1': 'Offer',
               b'2': 'Trade',
               b'4': 'OpeningPrice',
               b'6': 'SettlementPrice',
               b'7': 'TradingSessionHighPrice',
               b'8': 'TradingSessionLowPrice',
               b'B': 'TradeVolume',
               b'C': 'OpenInterest',
               b'E': 'ImpliedBid',
               b'F': 'ImpliedOffer',
               b'J': 'EmptyBook',
               b'N': 'SessionHighBid',
               b'O': 'SessionLowOffer',
               b'W': 'FixingPrice',
               b'e': 'ElectronicVolume',
               b'g': 'ThresholdLimitsandPriceBandVariation'               
               }

AggressorSide = {
                 0: 'NoAggressor',
                 1: 'Buy',
                 2: 'Sell',
                 255: None
                 }

SecurityUpdateAction = { 
                  b'A': 'Add',
                  b'D': 'Delete',
                  b'M': 'Modify'
                  }

SecurityTradingStatus = { 
                  2  : 'Halt',
                  4  : 'Close',
                  15 : 'NewPriceIndication',
                  17 : 'ReadyToTrade',
                  18 : 'NotAvailableForTrading',
                  20 : 'UnknownorInvalid',
                  21 : 'Preopen',
                  24 : 'PreCross',
                  25 : 'Cross',
                  26 : 'PostClose',
                  103: 'NoChange',
                  255: None
                  }

SecurityTradingEvent = {
                  0 : 'NoEvent',
                  1 : 'NoCancel',
                  4 : 'ResetStatistics',
                  5 : 'ImpliedMatchingON',
                  6 : 'ImpliedMatchingOFF'
                  }

EventType = {
             5: 'Activation',
             7: 'LastEligibleTradeDate'
             }

HaltReason = {
              0: 'GroupSchedule',
              1: 'SurveillanceIntervention',
              2: 'MarketEvent',
              3: 'InstrumentActivation',
              4: 'InstrumentExpiration',
              5: 'Unknown',
              6: 'RecoveryInProcess'
              }

PutOrCall = {
             0: 'Put',
             1: 'Call'
             }

OpenCloseSettlFlag = {
                      0: 'DailyOpenPrice',
                      5: 'IndicativeOpeningPrice',
                      255: None
                      }

LegSide = {
           1: 'BuySide',
           2: 'SellSide'
           }

class MsgNames:
    # Incremental
    StatusMsg  = "SecurityStatus30"
    RefreshMsg = "MDIncrementalRefreshBook32"
    DailyStatMsg = "MDIncrementalRefreshDailyStatistics33"
    LimitMsg   = "MDIncrementalRefreshLimitsBanding34"
    StatMsg    = "MDIncrementalRefreshSessionStatistics35"
    VolumeMsg  = "MDIncrementalRefreshVolume37"
    QuoteRequestMsg  = "QuoteRequest39"
    TradeMsg   = "MDIncrementalRefreshTradeSummary42"
    # Definitions
    FutDefMsg  = "MDInstrumentDefinitionFuture27"
    SprdDefMsg = "MDInstrumentDefinitionSpread29"
    OptDefMsg  = "MDInstrumentDefinitionOption41"
    # Snapshot
    SnapMsg    = "SnapshotFullRefresh38"
    
# Field Names
class FN:    
    TransTime  = "TransactTime"             # 60
    EventIndi  = "MatchEventIndicator"      # 5799
    MDEntries  = "MDEntries"                # 268     group
    Price      = "MDEntryPx"                # 270
    Size       = "MDEntrySize"              # 271
    SecID      = "SecurityID"               # 48
    SecSeq     = "RptSeq"                   # 83
    NumOrders  = "NumberOfOrders"           # 346
    BookLevel  = "MDPriceLevel"             # 1023
    UpdAction  = "MDUpdateAction"           # 279
    EntryType  = "MDEntryType"              # 269
    AggSide    = "AggressorSide"            # 5797
    OrderID    = "OrderID"                  # 37
    LastQty    = "LastQty"                  # 32
    OrderEntries = "OrderIDEntries"         # 37705    group 
    # Below is for definitions
    TotNumReports = "TotNumReports"         # 911
    SecUpdAct  = "SecurityUpdateAction"     # 980
    LastUpdTm  = "LastUpdateTime"           # 779
    TradingStatus = "MDSecurityTradingStatus"    # 1682
    TrdStatus  = "SecurityTradingStatus"    # 326
    HaltReason = "HaltReason"               # 327
    TradingEvent  = "SecurityTradingEvent"  # 1174
    ApplID     = "ApplID"                   # 1180
    MktSegID   = "MarketSegmentID"          # 1300
    UlProduct  = "UnderlyingProduct"        # 462
    SecExch    = "SecurityExchange"         # 207
    SecGroup   = "SecurityGroup"            # 1151
    Asset      = "Asset"                    # 6937
    Symbol     = "Symbol"                   # 55
    IDSource   = "SecurityIDSource"         # 22
    SecType    = "SecurityType"             # 167
    CFICode    = "CFICode"                  # 461
    MatMMYYYY  = "MaturityMonthYear"        # 200
    Currency   = "Currency"                 # 15
    SettlCur   = "SettlCurrency"            # 120
    MatchAlgo  = "MatchAlgorithm"           # 1142
    MinTradeVol = "MinTradeVol"             # 562
    MaxTradeVol = "MaxTradeVol"             # 1140
    MinPxIncr  = "MinPriceIncrement"        # 969
    DispFctr   = "DisplayFactor"            # 9787
    MainFrac   = "MainFraction"             # 37702
    SubFrac    = "SubFraction"              # 37703
    PxDispFmt  = "PriceDisplayFormat"       # 9800
    UnitMeasure= "UnitOfMeasure"            # 996
    ContractSz = "UnitofMeasureQty"         # 1147
    TrdRefPx   = "TradingReferencePrice"    # 1150
    SettlPxType= "SettlPriceType"           # 731
    OpenInt    = "OpenInterestQty"          # 5792
    ClearVol   = "ClearedVolume"            # 5791
    HighLimPx  = "HighLimitPrice"           # 1149
    LowLimPx   = "LowLimitPrice"            # 1148
    MaxPxChng  = "MaxPriceVariation"        # 1143
    DecayQty   = "DecayQuantity"            # 5818
    DecayDate  = "DecayStartDate"           # 5819
    OrigCtrctSize = "OriginalContractSize"  # 5849
    CtrctMult  = "ContractMultiplier"       # 231
    CtrctMultUnit = "ContractMultiplierUnit"    # 1435
    FlowSchedType = "FlowScheduleType"      # 1439
    MinPxIncrAmt  = "MinPriceIncrementAmount"   # 1146
    UserDefInstr  = "UserDefinedInstrument" # 9779
    PutOrCall  = "PutOrCall"                # 201
    StrikePx   = "StrikePrice"              # 202
    StrikeCcy  = "StrikeCurrency"           # 947
    MinCabPx   = "MinCabPrice"              # 9850    
    Events     = "Events"                   # 864     group
    MDFeedTypes= "MDFeedTypes"              # 1141    group
    InstAttrib = "InstAttrib"               # 870     group
    LotTypeRules  = "LotTypeRules"          # 1234    group
    Legs       = "Legs"                     # 555     group
    Underlyings= "Underlyings"              # 711     group
    SecSubType = "SecuritySubType"          # 762
    PxRatio    = "PriceRatio"               # 5770
    TickRule   = "TickRule"                 # 6350
    EventType  = "EventType"                # 865
    EventTime  = "EventTime"                # 1145
    MDFeedType = "MDFeedType"               # 1022
    MktDepth   = "MarketDepth"              # 264
    UnderlyingID = "UnderlyingSecurityID"   # 309
    UnderlyingSym = "UnderlyingSymbol"      # 311
    LastMsgSeq = "LastMsgSeqNumProcessed"   # 369
    TradeDate  = "TradeDate"                # 75
    TrdRefDate = "TradingReferenceDate"     # 5796
    OpenCloseSettlFlag = "OpenCloseSettlFlag"   # 286
    InstAttribVal = "InstAttribValue"       # 872
    LotType    = "LotType"                  # 1093
    MinLotSz   = "MinLotSize"               # 1231
    LegSecID   = "LegSecurityID"            # 602
    LegSide    = "LegSide"                  # 624
    LegRatio   = "LegRatioQty"              # 623
    LegPx      = "LegPrice"                 # 566
    LegOptDelta= "LegOptionDelta"           # 1017
    QuoteReqID = "QuoteReqID"               # 131
    OrderQty   = "OrderQty"                 # 38
    QuoteType  = "QuoteType"                # 537
    QuoteSide  = "Side"                     # 54
    
#Names of messages and fields

# id = 32
RefreshMessage = namedtuple(MsgNames.RefreshMsg, [FN.TransTime, FN.EventIndi, FN.MDEntries])
RefreshMDEntry = namedtuple(FN.MDEntries, [FN.SecID, FN.SecSeq, FN.Price, FN.Size, 
                                           FN.NumOrders, FN.BookLevel, FN.UpdAction, FN.EntryType])

# id = 42
TradeMessage = namedtuple(MsgNames.TradeMsg,[FN.TransTime, FN.EventIndi, FN.MDEntries, FN.OrderEntries])
TradeEntry = namedtuple(FN.MDEntries, [FN.SecID, FN.SecSeq, FN.Price, FN.Size, 
                                       FN.NumOrders, FN.AggSide, FN.UpdAction])
OrderEntry = namedtuple(FN.OrderEntries, [FN.OrderID, FN.LastQty])

# id = 37
VolumeMessage = namedtuple(MsgNames.VolumeMsg, [FN.TransTime, FN.EventIndi, FN.MDEntries])
VolumeMDEntry = namedtuple(FN.MDEntries, [FN.SecID, FN.SecSeq, FN.Size, FN.UpdAction])

# id = 35
StatMessage = namedtuple(MsgNames.StatMsg, [FN.TransTime, FN.EventIndi, FN.MDEntries])
StatMDEntry = namedtuple(FN.MDEntries, [FN.Price, FN.SecID, FN.SecSeq, FN.OpenCloseSettlFlag,
                                        FN.UpdAction, FN.EntryType])

# id = 33
DailyStatMessage = namedtuple(MsgNames.DailyStatMsg, [FN.TransTime, FN.EventIndi, FN.MDEntries])
DailyStatMDEntry = namedtuple(FN.MDEntries, [FN.Price, FN.Size, FN.SecID, FN.SecSeq, FN.TrdRefDate,
                                             FN.SettlPxType, FN.UpdAction, FN.EntryType])

# id = 30
SecurityStatusMessage = namedtuple(MsgNames.StatusMsg, [FN.TransTime, FN.SecGroup, FN.Asset,
                                                        FN.SecID, FN.TradeDate, FN.EventIndi,
                                                        FN.TradingStatus, FN.HaltReason, FN.TradingEvent])

# id = 34
LimitMessage = namedtuple(MsgNames.LimitMsg, [FN.TransTime, FN.EventIndi, FN.MDEntries])
LimitMDEntry = namedtuple(FN.MDEntries, [FN.HighLimPx, FN.LowLimPx, FN.MaxPxChng, 
                                         FN.SecID, FN.SecSeq])

# id = 39
QuoteRequestMessage = namedtuple(MsgNames.QuoteRequestMsg, [FN.TransTime, FN.QuoteReqID, FN.EventIndi, FN.MDEntries])
QuoteRequestMDEntry = namedtuple(FN.MDEntries, [FN.Symbol, FN.SecID, FN.OrderQty, FN.QuoteType, FN.QuoteSide])


# id = 27
FutureDefnMessage = namedtuple(
                               MsgNames.FutDefMsg,
                               [
                                FN.EventIndi,
                                FN.TotNumReports,
                                FN.SecUpdAct,
                                FN.LastUpdTm,
                                FN.TradingStatus,
                                FN.ApplID,
                                FN.MktSegID,
                                FN.UlProduct,
                                FN.SecExch,
                                FN.SecGroup,
                                FN.Asset,
                                FN.Symbol,
                                FN.SecID,
                                FN.SecType,
                                FN.CFICode,
                                FN.MatMMYYYY,
                                FN.Currency,
                                FN.SettlCur,
                                FN.MatchAlgo,
                                FN.MinTradeVol,
                                FN.MaxTradeVol,
                                FN.MinPxIncr,
                                FN.DispFctr,
                                FN.MainFrac,
                                FN.SubFrac,
                                FN.PxDispFmt,
                                FN.UnitMeasure,
                                FN.ContractSz,
                                FN.TrdRefPx,
                                FN.SettlPxType,
                                FN.OpenInt,
                                FN.ClearVol,
                                FN.HighLimPx,
                                FN.LowLimPx,
                                FN.MaxPxChng,
                                FN.DecayQty,
                                FN.DecayDate,
                                FN.OrigCtrctSize,
                                FN.CtrctMult,
                                FN.CtrctMultUnit,
                                FN.FlowSchedType,
                                FN.MinPxIncrAmt,
                                FN.UserDefInstr,
                                FN.Events,
                                FN.MDFeedTypes,
                                FN.InstAttrib,
                                FN.LotTypeRules])

# id = 29
SpreadDefnMessage = namedtuple(MsgNames.SprdDefMsg, 
                               [
                                FN.EventIndi,
                                FN.TotNumReports,
                                FN.SecUpdAct,
                                FN.LastUpdTm,
                                FN.TradingStatus,
                                FN.ApplID,
                                FN.MktSegID,
                                FN.UlProduct,
                                FN.SecExch,
                                FN.SecGroup,
                                FN.Asset,
                                FN.Symbol,
                                FN.SecID,
                                FN.SecType,
                                FN.CFICode,
                                FN.MatMMYYYY,
                                FN.Currency,
                                FN.SecSubType,
                                FN.UserDefInstr,
                                FN.MatchAlgo,
                                FN.MinTradeVol,
                                FN.MaxTradeVol,
                                FN.MinPxIncr,
                                FN.DispFctr,
                                FN.PxDispFmt,
                                FN.PxRatio,
                                FN.TickRule,
                                FN.UnitMeasure,
                                FN.TrdRefPx,
                                FN.SettlPxType,
                                FN.OpenInt,
                                FN.ClearVol,
                                FN.HighLimPx,
                                FN.LowLimPx,
                                FN.MaxPxChng,
                                FN.MainFrac,
                                FN.SubFrac,
                                FN.Events,
                                FN.MDFeedTypes,
                                FN.InstAttrib,
                                FN.LotTypeRules,
                                FN.Legs
                                ])

OptionDefnMessage = namedtuple(MsgNames.OptDefMsg,
                               [
                                FN.EventIndi,
                                FN.TotNumReports,
                                FN.SecUpdAct,
                                FN.LastUpdTm,
                                FN.TradingStatus,
                                FN.ApplID,
                                FN.MktSegID,
                                FN.UlProduct,
                                FN.SecExch,
                                FN.SecGroup,
                                FN.Asset,
                                FN.Symbol,
                                FN.SecID,
                                FN.SecType,
                                FN.CFICode,
                                FN.PutOrCall,
                                FN.MatMMYYYY,
                                FN.Currency,
                                FN.StrikePx,
                                FN.StrikeCcy,
                                FN.SettlCur,
                                FN.MinCabPx,
                                FN.MatchAlgo,
                                FN.MinTradeVol,
                                FN.MaxTradeVol,
                                FN.MinPxIncr,
                                FN.MinPxIncrAmt,
                                FN.DispFctr,
                                FN.TickRule,
                                FN.MainFrac,
                                FN.SubFrac,
                                FN.PxDispFmt,
                                FN.UnitMeasure,
                                FN.ContractSz,
                                FN.TrdRefPx,
                                FN.SettlPxType,
                                FN.ClearVol,
                                FN.OpenInt,
                                FN.LowLimPx,
                                FN.HighLimPx,
                                FN.UserDefInstr,
                                FN.Events,
                                FN.MDFeedTypes,
                                FN.InstAttrib,
                                FN.LotTypeRules,
                                FN.Underlyings
                                ])

InstrumentEventEntry = namedtuple(FN.Events,[FN.EventType, FN.EventTime])
MDFeedTypeEntry = namedtuple(FN.MDFeedTypes,[FN.MDFeedType, FN.MktDepth])
UnderlyingEntry = namedtuple(FN.Underlyings,[FN.UnderlyingID, FN.UnderlyingSym])
InstEligibilityEntry = namedtuple(FN.InstAttrib, [FN.InstAttribVal])
LotTypeRulesEntry = namedtuple(FN.LotTypeRules, [FN.LotType, FN.MinLotSz])
LegEntry = namedtuple(FN.Legs, [FN.LegSecID, FN.LegSide, FN.LegRatio, FN.LegPx, FN.LegOptDelta])

# id = 38
SnapFullMessage =  namedtuple(MsgNames.SnapMsg,
                              [FN.LastMsgSeq, FN.TotNumReports, FN.SecID, FN.SecSeq,
                               FN.TransTime, FN.LastUpdTm, FN.TradeDate, FN.TradingStatus,
                               FN.HighLimPx, FN.LowLimPx, FN.MaxPxChng, FN.MDEntries])

SnapMDEntry = namedtuple(FN.MDEntries, [FN.Price, FN.Size, FN.NumOrders, FN.BookLevel, FN.TrdRefDate,
                                        FN.OpenCloseSettlFlag, FN.SettlPxType, FN.EntryType])


