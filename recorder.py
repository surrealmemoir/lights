
import common.infra.network as cin
import struct
from datetime import datetime

import mytime

def mcRecorder(mc_address_string, filename):
    mcast_a, mcast_p, if_n = cin.address_string_to_tuple(mc_address_string)
    sock = cin.prepare_mc_recv(mcast_a, mcast_p, if_n)
    
    f = open(filename, 'wb')
    msgcnt = 0
    print('Recording begins at {}'.format( datetime.now() ) )
    try :
        while True:            
            buf = sock.recv(16000)
            curtm = datetime.now()
            tmI64 = int(curtm.timestamp())*(10**9) + curtm.microsecond*1000
            f.write(struct.pack('H', 8 + len(buf)))
            f.write(struct.pack('Q', tmI64))
            f.write(buf)
            msgcnt += 1
            #print(readPacket(buf, None))
            if (msgcnt % 1000) == 1:
                print('Packets Recorded: ', msgcnt)
                f.flush()            
    except KeyboardInterrupt:
        print('Recording finished at {}, Packet Count: {}'.format( datetime.now(), msgcnt) )
        f.close()
        
def recordingReader(filename):
    ''' returns a generator that yields (receivetime, binarypacket) tuple '''
    f = open(filename, 'rb')
    msgcnt = 0
    while True:
        head = f.read(2)
        if not head:
            break
        sz, = struct.unpack('H', head)
        tmI64, = struct.unpack('Q', f.read(8))
        buf = f.read(sz - 8)
        msgcnt += 1
        if msgcnt == 1:
            print('Begin time', mytime.printI64(tmI64))
        yield (tmI64, buf)
    f.close()
    print('End time', mytime.printI64(tmI64))
    print('Packet count ', msgcnt)
