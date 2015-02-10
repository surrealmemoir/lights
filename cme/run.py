
from .feedprocessor import CleanFeedSyncer
from .settings import recordPath, addrdict

import common.infra.network as cin
import heapq
import datetime as dt
from recorder import recordingReader

def setupLiveSockets(receiver, addrs, client):
    sock1 = cin.prepare_mc_recv(*cin.address_string_to_tuple(addrs['I']))
    sock2 = cin.prepare_mc_recv(*cin.address_string_to_tuple(addrs['S']))
    sock3 = cin.prepare_mc_recv(*cin.address_string_to_tuple(addrs['N']))
    handler = CleanFeedSyncer(client)
    receiver.add_receiver(sock1, handler.processIncrPacket)
    receiver.add_receiver(sock2, handler.processSnapPacket)
    receiver.add_receiver(sock3, handler.processDefnPacket)
    def activate():
        receiver.add_receiver(sock2, handler.processSnapPacket)
        receiver.add_receiver(sock3, handler.processDefnPacket)
    def deactivate():
        receiver.remove_receiver(sock2)
        receiver.remove_receiver(sock3)
    handler.activate_call = activate
    handler.deactivate_call = deactivate
    
def playlive(calldict):
    '''
    Live data.
    sample input: { 'F': print, 'O': print }
    This is to provide a call to the syncer that syncs the defn/snap/incr 
    '''
    recv = cin.asyncio_receiver()
    
    for k, v in calldict.items():
        setupLiveSockets(recv, addrdict[k], v)
    
    print('start event loop')
    try:
        recv.start()
    except KeyboardInterrupt:
        recv.loop.stop()
    print('end event loop')    
    
def replay(date, calldict):
    '''
    Recorded data.
    sample input: { 'F': print, 'O': print }
    This is to provide a call to the syncer that syncs the defn/snap/incr 
    '''
    callbacks = {}
    filepaths = {}
    for k, v in calldict.items():
        handler = CleanFeedSyncer(v)
        callbacks[ k + 'I' ] = handler.processIncrPacket
        callbacks[ k + 'S' ] = handler.processSnapPacket
        callbacks[ k + 'N' ] = handler.processDefnPacket
        for typ in ['I', 'S', 'N']:
            filepaths[ k + typ ] = recordPath(date, k, typ)
    
    f = lambda typ: ( (x, typ) for x in recordingReader(filepaths[typ]) )
    merged = heapq.merge( *[f(a) for a in filepaths] )
    print(dt.datetime.now())
    for (tm, packet), typ in merged:
        callbacks[typ](packet, tm)
    print(dt.datetime.now())    
    
