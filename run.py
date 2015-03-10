
#from cme.feedprocessor import CleanFeedSyncer
from cme.settings import recordPath, addrdict
from manager import GrandManager

import common.infra.network as cin
import heapq
import datetime as dt
from recorder import recordingReader

def setupLiveSockets(receiver, addrs, client):
    sock1 = cin.prepare_mc_recv(*cin.address_string_to_tuple(addrs['I']))
    sock2 = cin.prepare_mc_recv(*cin.address_string_to_tuple(addrs['S']))
    sock3 = cin.prepare_mc_recv(*cin.address_string_to_tuple(addrs['N']))
    
    receiver.add_receiver(sock1, client.processIncrFeed)
    receiver.add_receiver(sock2, client.processSnapFeed)
    receiver.add_receiver(sock3, client.processDefnFeed)
    #def activate():
    #    receiver.add_receiver(sock2, handler.processSnapPacket)
    #    receiver.add_receiver(sock3, handler.processDefnPacket)
    #def deactivate():
    #    receiver.remove_receiver(sock2)
    #    receiver.remove_receiver(sock3)
    #handler.activate_call = activate
    #handler.deactivate_call = deactivate

def playlive():
    '''
    Live data.
    Grand Manager should have the proper calls and procchng etc.
    '''
    recv = cin.asyncio_receiver()
    
    channels = ['F', 'O']
    mgr = GrandManager(channels)
    
    for a in channels:
        setupLiveSockets(recv, addrdict[a], mgr.channels[a])
    
    print('start event loop')
    try:
        recv.start()
    except KeyboardInterrupt:
        recv.loop.stop()
    print('end event loop')    

def replay(date):
    '''
    Recorded data.
    Grand Manager should have the proper calls and procchng etc.
    '''
    callbacks = {}
    filepaths = {}
    
    channels = ['F', 'O']
    mgr = GrandManager(channels)
    for a in channels:
        callbacks[ a + 'I' ] = mgr.channels[a].processIncrFeed
        callbacks[ a + 'S' ] = mgr.channels[a].processSnapFeed
        callbacks[ a + 'N' ] = mgr.channels[a].processDefnFeed
        for typ in ['I', 'S', 'N']:
            filepaths[ a + typ ] = recordPath(date, a, typ)
    
    f = lambda typ: ( (x, typ) for x in recordingReader(filepaths[typ]) )
    merged = heapq.merge( *[f(a) for a in filepaths] )
    print(dt.datetime.now())
    for (tm, packet), typ in merged:
        callbacks[typ](packet, tm)
    print(dt.datetime.now())
