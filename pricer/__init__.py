import numpy as np
import scipy.stats
from scipy.optimize import brentq

#from ammr.utils import inspector

'''
General option pricer, if we forget different decay schedule and tcal vs tbiz, then the inputs are
ULprice; Strike; Volatility; TimeToMaturity; OptionFundingRate r_opt; ULFundingRate (r_ul - q_ul)

For Stock options: r_opt = r_ul usually
For Future options: r_ul = q_ul = 0
'''

N = scipy.stats.norm.cdf
phi = scipy.stats.norm.pdf
TINYPRICE = 1e-8

def EuropeanBasePrice(std, k, call):
    d1 = (-np.log(k)+0.5*(std**2)) / (std)
    d2 = d1 - std
    return ( N(d1) - k * N(d2) ) if call else ( k * N(-d2) - N(-d1) )

def EuropeanBasePriceDiff(std, k, call, price):    
    d1 = (-np.log(k)+0.5*(std**2)) / (std)
    d2 = d1 - std
    return ( N(d1) - k * N(d2) - price) if call else ( k * N(-d2) - N(-d1)- price )

def EuropeanBaseVega(std, k, call, price = 0):
    d2 = (-np.log(k)-0.5*(std**2)) / (std)
    return phi(d2)

def EuropeanBaseImply(price, k, tbiz, call):
    if np.isnan(price) or price < TINYPRICE:
        return np.nan
    vol_floor = 0.01
    vol_ceil = 3
    sqrttbiz = np.sqrt( tbiz )
    if EuropeanBasePriceDiff( vol_floor * sqrttbiz, k, call, price ) > -TINYPRICE:
        return vol_floor
    elif EuropeanBasePriceDiff( vol_ceil * sqrttbiz, k, call, price ) < TINYPRICE:
        return vol_ceil
    else:
        std = brentq(EuropeanBasePriceDiff, vol_floor * sqrttbiz, vol_ceil * sqrttbiz, 
                     args = (k, call, price), rtol = 0.000001 * sqrttbiz)
    return std / sqrttbiz

def testImply(N):
    #N = 10000
    fwdratio = np.exp(np.random.normal(0, 1, N))
    vol = 0.01 * ( 5 + 200 * np.random.rand(N))
    tbiz = np.random.rand(N)
    px = np.zeros(N)
    implyvol = np.zeros(N)
    for i in range(N):
        px[i] = EuropeanBasePrice(vol[i] * np.sqrt(tbiz[i]), fwdratio[i], True)
        implyvol[i] = EuropeanBaseImply(px[i], fwdratio[i], tbiz[i], True)
    print('Sample size: ', N)
    maxerr = max(abs((vol - implyvol)[implyvol > 0.01]))
    print('MaxError', maxerr)
    # low premium
    giveup = (np.log(fwdratio) / (vol * np.sqrt(tbiz)))[implyvol == 0.01]
    print('Lowest Moneyness when give up', min(abs(giveup)))
    #return fwdratio, vol, tbiz, px, implyvol

def BSEuropeanPrice(vol, spot, strike, tbiz, r_opt, r_ul, q_ul, call):
    """Generic input. Except no tbiz/tcal schedule and discrete dividend"""
    fwd = spot * np.exp(tbiz * (r_ul - q_ul))
    df = np.exp(-tbiz * r_opt)
    return df * fwd * EuropeanBasePrice(vol*np.sqrt(tbiz), strike/fwd, call)

def BSEuropeanImplyVol(price, spot, strike, tbiz, r_opt, r_ul, q_ul, call):
    fwd = spot * np.exp(tbiz * (r_ul - q_ul))
    df = np.exp(-tbiz * r_opt)
    return EuropeanBaseImply(price / (df * fwd), strike / fwd, tbiz, call)
