from datetime import datetime, date, time
from pytz import timezone

gTZ  = timezone( 'US/Eastern' )

def printI64( u64 ):
    utc, nanos = divmod( u64, 10**9 )
    dt = datetime.fromtimestamp( utc, gTZ )
    return '{0}.{1} {2}'.format( dt.strftime( '%Y-%m-%d@%H:%M:%S' ), format( nanos, '09d' ), dt.strftime( '%Z' ) )

def toI64( date = date.today(), hrs = 0, mins = 0, secs = 0, nsecs = 0 ):
    return int( gTZ.localize( 
                        datetime.combine( date, 
                               time( 
                                        hour        = hrs, 
                                        minute      = mins, 
                                        second      = secs, 
                                ) 
                        ),
                is_dst = None
           ).timestamp() ) * 10**9 + nsecs
