'''
Created on Dec 23, 2014

@author: hluo

ftp://ftp.cmegroup.com/SBEFix/Production/Configuration/config.xml

CME feeds:
CME, Equity Futures: ES, E-Mini
CME, Interest Rate,  GE(ED on bbg),  3 month EURODOLLARs. 
                     GLB(EM): 1 month, BU2(BUA) 2 year,  BU3(BUB), and BU5(BUD), these don't trade
CBOT, Interest Rate, ZT(TU)   2 year T-Note Futures
                     ZF(FV)   5 year T-Note Futures
                     ZN(TY)   10 year T-Note Futures
                     ZB(US)   15-25 year T-Bond Futures
                     UB(WN)   > 25 year T-Bond Futures
                     ZQ(FF)   Federal Funds Rate Futures
                     T1U(CTP) 2 year IRS
                     F1U(CFP) 5 year IRS
                     N1U(CNP) 10 year IRS
                     B1U(CBP) 30 year IRS                     
'''


cme_equity_futures = {
                      'I': "224.0.31.1:14310:eth3.453",
                      'N': "224.0.31.43:14310:eth3.453",
                      'S': "224.0.31.22:14310:eth3.453"
                      }

cme_equity_options = {
                      'I': "224.0.31.2:14311:eth3.453",
                      'N': "224.0.31.44:14311:eth3.453",
                      'S': "224.0.31.23:14311:eth3.453"
                      }

cme_rate_futures = {
                      'I': "224.0.31.3:14312:eth3.453",
                      'N': "224.0.31.45:14312:eth3.453",
                      'S': "224.0.31.24:14312:eth3.453"
                      }

cme_rate_options = {
                      'I': "224.0.31.4:14313:eth3.453",
                      'N': "224.0.31.46:14313:eth3.453",
                      'S': "224.0.31.25:14313:eth3.453"
                      }

nymex_crude_futures = {
                      'I': "224.0.31.130:14382:eth3.453",
                      'N': "224.0.31.172:14382:eth3.453",
                      'S': "224.0.31.151:14382:eth3.453"
                      }

nymex_crude_options = {
                      'I': "224.0.31.131:14383:eth3.453",
                      'N': "224.0.31.173:14383:eth3.453",
                      'S': "224.0.31.152:14383:eth3.453"
                      }

addrdict = {'F': cme_equity_futures,
            'O': cme_equity_options}

filepre  = {'F': 'ES',
            'O': 'ESopt'}

filepost = {'I': 'incr',
            'S': 'snap',
            'N': 'defn'}

folder = '/gfs/qsa/userdata/hluo/'

def recordPath(date, feed, typ):
    ''' 
    returns path of recording
    Feed: F / O;  typ: I / S / N
    '''
    return '_'.join( [folder + filepre[feed],
                      str(date),
                      filepost[typ] ] )
