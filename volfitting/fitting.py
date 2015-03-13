import numpy as np
from scipy.optimize import minimize

from ammr.utils import inspector

from volfitting.volmodel import HVol

hdrval = HVol.hdr(hvolvref = 0.2,
                  hvolkmin = -3,
                  hvolkmax = 2,
                  hvolkp = -2,
                  hvolkc = 1,
                  hvoltp = 0.6,
                  hvoltc = 0.6,
                  hvolfp = 0.6,
                  hvolfc = 0.3)
volmodel = HVol(hdrval)

def quadcriteria(param, xvec, yvec, wvec):
    diff = yvec - volmodel.vol(param, xvec)
    b = np.diff(xvec)
    weights = wvec * (np.append(b,b[-1]) + np.append(b[0],b))/2
    return 0.5 * np.dot(diff, weights*diff)


def quadcriteriaJac(param, xvec, yvec, wvec):
    diff = yvec - volmodel.vol(param, xvec)
    b = np.diff(xvec)
    weights = wvec * (np.append(b,b[-1]) + np.append(b[0],b))/2
    return - np.dot(weights * diff, volmodel.vol_grad(param, xvec))


def fit(strkvec, fwd, tbiz, bidvol, askvol ):
    ''' assume strkvec, bidvol, askvol are numpy arrays '''
    idx = np.logical_and(bidvol > 0, askvol > 0)
    bid = bidvol[idx]
    ask = askvol[idx]
    tgt = 0.5 * (bid + ask)
    p0 = np.array( [0.2, 0, 0, 0, 0] )
    xvec = np.log(strkvec[idx]/fwd) / np.sqrt(tbiz)
    #inspector()
    res = minimize(quadcriteria, p0, args = (xvec,tgt,1),
                   jac = quadcriteriaJac, method = 'SLSQP')
    if res.success:
        return res.x
    else:
        print(res)
        raise Exception('Fitting failed')
        inspector()
