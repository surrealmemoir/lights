from collections import namedtuple
import numpy as np


class QuadraticVol:
    def vol( self, param, x ):
        return param[0] + param[1] * x + param[2] * (x ** 2)

class TanhVol:
    ''' Quadratic, but replace x with alpha * tanh(x/alpha), two different smiles depending on call/put wing '''
    pass

class GVol:
    '''x = log(K/F) / sqrt(t)'''
    def vol( self, param, x ):
        z = ( param[2] * np.exp( -param[3] * x / param[0] )
              + ( 1 - param[2] ) * np.exp( -param[4] * x / param[0] ) )
        return param[0] * np.sqrt( 1 + param[1] * np.log( z ) )
    
    def dvoldx( self, param, x ):
        pass
    
    def d2voldx2( self, param, x ):
        pass
    
    def vol_grad( self, param, x ):
        return 0
    
    def dvoldx_grad( self, param, x ):
        return 0
    
    def d2voldx2_grad( self, param, x ):
        return 0
    

class HVol:
    '''
    x = log(K/F) / sqrt(t)
    in the member functions below, we assume param to be a numpy array, not namedtuple
    '''
    param = namedtuple( 'hvolparams', [ 'hvolvatm', 'hvolskew', 'hvolsmile', 'hvolputshift', 'hvolcallshift' ] )
    hdr   = namedtuple( 'hvolhdr', [ 'hvolvref', 'hvolkmin', 'hvolkmax', 'hvolkp', 'hvolkc',
                                     'hvoltp', 'hvoltc', 'hvolfp', 'hvolfc' ] )
    def __init__( self, hdrval ):   
        self.hdrval = hdrval     
        if hdrval != None:
            self.setupinf( hdrval )
    
    def update( self, hdrval ):
        self.hdrval = hdrval
        self.setupinf( hdrval )
    
    def vol( self, param, x ):
        '''dim: len(x)'''
        return np.dot( self.vol_grad( param, x ), np.array( param ) )
    
    def dvoldx( self, param, x ):
        return np.dot( self.dvoldx_grad( param, x ), np.array( param ) )
    
    def d2voldx2( self, param, x ):
        return np.dot( self.d2voldx2_grad( param, x ), np.array( param ) )
    
    def vol_grad( self, param, x ):
        '''dim: len(x) * len(param)'''
        hdrval = self.hdrval
        kb = np.where( x < 0, hdrval.hvolkmin, hdrval.hvolkmax ) * hdrval.hvolvref
        ks = np.where( x < 0, hdrval.hvolkp, hdrval.hvolkc ) * hdrval.hvolvref
        tt = np.where( x < 0, hdrval.hvoltp, hdrval.hvoltc )
        ff = np.where( x < 0, hdrval.hvolfp, hdrval.hvolfc )
    
        a0 = np.where( x * (x-kb) > 0, 1 - 1 / ( 1 + tt*(x/kb - 1) ), 0 )
        a1 = np.where( x * (x-kb) > 0, a0 * (1 + a0) / tt, 0 )
        a2 = np.where( x * (x-kb) > 0, 0.5 * ( (a0/tt) ** 2 ), 0 )
    
        dskew  = np.where( x * (x-kb) > 0, 5 * kb * (1 + a1), 5 * x )
        dsmile = np.where( x * (x-kb) > 0, 25 * kb * kb * (0.5 + a1 + a2), 12.5 * x * x )
        dshift = np.where( x * (x-kb) > 0, (((ff + kb/ks) / (1 + ff)) ** 4) * (1 + 4*a1/(1+ff) + a2*((12-8*ff) / ((1+ff)**2)) ),
                           (x * (kb+ff*ks) / (ks * (kb+ff*x))) ** 4 )
        dpshift = np.where( x < 0, dshift, 0 )
        dcshift = np.where( x > 0, dshift, 0 )
        return np.array( [ np.ones(np.shape(x)), dskew , dsmile, dpshift, dcshift ] ).T
        
    def dvoldx_grad( self, param, x ):
        hdrval = self.hdrval
        kb = np.where( x < 0, hdrval.hvolkmin, hdrval.hvolkmax ) * hdrval.hvolvref
        ks = np.where( x < 0, hdrval.hvolkp, hdrval.hvolkc ) * hdrval.hvolvref
        tt = np.where( x < 0, hdrval.hvoltp, hdrval.hvoltc )
        ff = np.where( x < 0, hdrval.hvolfp, hdrval.hvolfc )
    
        a0 = np.where( x * (x-kb) > 0, 1 - 1 / ( 1 + tt*(x/kb - 1) ), 0 )
        a1 = np.where( x * (x-kb) > 0, (1 + 2 * a0) / kb * ((1 - a0) ** 2), 0 )
        a2 = np.where( x * (x-kb) > 0, a0 / (tt*kb) * ((1 - a0) ** 2), 0 )
    
        dskew  = np.where( x * (x-kb) > 0, 5 * kb * a1, 5 )
        dsmile = np.where( x * (x-kb) > 0, 25 * kb * kb * (a1 + a2), 25 * x )
        dshift = np.where( x * (x-kb) > 0, ( ((ff + kb/ks) / (1 + ff)) ** 4 ) * ( 4*a1/(1+ff) + a2*((12-8*ff) / ((1+ff)**2)) ),
                           ( (kb+ff*ks) / (ks * (kb+ff*x)) ) ** 4 * (4 * kb * x * x * x/(kb+ff*x)) )
        dpshift = np.where( x < 0, dshift, 0 )
        dcshift = np.where( x > 0, dshift, 0 )
        return np.array( [ np.zeros(np.shape(x)), dskew , dsmile ,dpshift, dcshift ] ).T
    
    def d2voldx2_grad(self, param, x):
        """ x = logkf / sqrt t, so far only works if x is a number"""
        hdrval = self.hdrval
        kb = np.where( x < 0, hdrval.hvolkmin, hdrval.hvolkmax ) * hdrval.hvolvref
        ks = np.where( x < 0, hdrval.hvolkp, hdrval.hvolkc ) * hdrval.hvolvref
        tt = np.where( x < 0, hdrval.hvoltp, hdrval.hvoltc )
        ff = np.where( x < 0, hdrval.hvolfp, hdrval.hvolfc )
    
        a0 = np.where(x * (x-kb) > 0, 1 - 1 / (1 + tt*(x/kb - 1)), 0)
        a1 = np.where(x * (x-kb) > 0, -6 * a0 * tt / (kb*kb) * ((1 - a0) ** 3), 0)
        a2 = np.where(x * (x-kb) > 0, (1-3*a0) / (kb*kb) * ((1 - a0) ** 3), 0)
    
        dskew  = np.where( x * (x-kb) > 0, 5 * kb * a1, 0 )
        dsmile = np.where( x * (x-kb) > 0, 25 * kb * kb * (a1 + a2), 25 )
        dshift = np.where( x * (x-kb) > 0, (((ff + kb/ks) / (1 + ff)) ** 4) * (4*a1/(1+ff) + a2*((12-8*ff) / ((1+ff)**2))),
                            ((kb+ff*ks) / (ks * (kb+ff*x))) ** 4 * (4 * kb * x * x * (3*kb-2*ff*x)/((kb+ff*x)**2)) )
        dpshift = np.where( x < 0, dshift, 0 )
        dcshift = np.where( x > 0, dshift, 0 )
        return np.array( [ np.zeros(np.shape(x)), dskew , dsmile ,dpshift, dcshift ] ).T
    
    def setupinf( self, hdr ):
        ''' on the wings, vols go upward at extreme strikes '''
        kb5 = np.array( [ hdr.hvolkmin, hdr.hvolkmax ] ) * hdr.hvolvref * 5
        ff1 = 1 + np.array( [ hdr.hvolfp, hdr.hvolfc ] )
        fk4 = ( np.array( [ hdr.hvolfp + hdr.hvolkmin / hdr.hvolkp, 
                            hdr.hvolfc + hdr.hvolkmax / hdr.hvolkc ] ) / ff1 ) ** 4 * 4
        
        s1coeff = np.array( [ 0, kb5[0], kb5[0] ** 2, 
                              fk4[0] / ff1[0], 0 ] ) / hdr.hvoltp
        s2coeff = np.array( [ 0, kb5[1], kb5[1] ** 2, 
                              0, fk4[1] / ff1[1] ] ) / hdr.hvoltc
        c1coeff = np.array( [ 0, 0, kb5[0] ** 2,
                              fk4[0] * (3 - 2 * hdr.hvolfp) / (ff1[0] ** 2),
                              0 ] ) / ( hdr.hvoltp ** 2 ) + 3 * s1coeff  
        c2coeff = np.array( [ 0, 0, kb5[1] ** 2, 0,
                              fk4[1] * (3 - 2 * hdr.hvolfc) / (ff1[1] ** 2) ]
                            ) / ( hdr.hvoltc ** 2 ) + 3 * s2coeff
        
        self.infcons = np.array( [ c1coeff, c2coeff ] )
    
    def addcons( self, param ):
        return np.dot( self.infcons, param )
    
    def addcons_grad( self, param ):
        return self.infcons
