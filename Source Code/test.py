'''
Created on Jan 15, 2013

@author: ccnx
'''
import dpkt
import socket
from collections import deque

#socket.inet_ntoa('\x01\x02\x03\x04')

from numpy import *

# If the package has been installed correctly, this should work:
import Gnuplot, Gnuplot.funcutils

import ccn

FL_DF_POS = 1
FL_MF_POS = 2

def bits(i,n):
    return tuple((0,1)[i>>j & 1] for j in xrange(n-1,-1,-1)) 


def processIpPacket(ipPacket):
    CCN_TYPE_INTEREST = '\x01\xd2'
    CCN_TYPE_CONTENT = '\x04\x82'

    flagbits = bits(ipPacket[0].off, 16)
    
    df_flag = flagbits[FL_DF_POS]
    mf_flag = flagbits[FL_MF_POS]

    if df_flag and ipPacket[0].data.data[:2] == CCN_TYPE_INTEREST:
            ccnPacket = ccn.CcnPacket(ipPacket[0].data.data)
            interests.append((ccnPacket, ipPacket[1]))
            print 'added Interest', ccnPacket.chunkNr.encode('hex')
    elif ipPacket[0].data.data[:2] == CCN_TYPE_CONTENT:
        #print 'Content t1', i
        ccnPacket = ccn.CcnPacket(ipPacket[0].data.data)
        if df_flag:
            contentObjects.append((ccnPacket, ipPacket[1]))
            print 'added Content with Ts', ccnPacket.chunkNr.encode('hex')
        else:
            contentObjects.append((ccnPacket, 0))
            print 'added Content', ccnPacket.chunkNr.encode('hex')
    elif (not df_flag and not mf_flag):
        #print 'Content t2', i
        tupleToModify = contentObjects[len(contentObjects) - 1]
        contentObjects[len(contentObjects) - 1] = (tupleToModify[0], ipPacket[1])
        print 'added Ts for Content ', tupleToModify[0].chunkNr.encode('hex')

filename = '../../measurements/small_file_filtered'

f = open(filename)
pcap = dpkt.pcap.Reader(f)

ipPackets = []
for ts, buf in pcap:
    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    ipPackets.append((ip, ts))

ccnPackets = []
interests = deque([])
contentObjects = deque([])
for ipPacket in ipPackets:
    try:
        processIpPacket(ipPacket)
    except Exception as e:
        print e

#
#interests = deque([])
#contentObjects = deque([])
#for i in range(len(ipPackets)):
#    ip = ipPackets[i]
#    flagbits = bits(ip.off, 16)
#    
#    df_flag = flagbits[FL_DF_POS]
#    mf_flag = flagbits[FL_MF_POS]
#    
#    if df_flag and ip.data.data[0] == CCN_INTEREST_TYPE:
#        #print 'Interest', i
#        interests.append(timestamps[i])
#    elif df_flag and ip.data.data[0] == CCN_CONTENT_TYPE:
#        #print 'Content t1', i
#        contentObjects.append(timestamps[i])
#    elif (not df_flag and not mf_flag):
#        #print 'Content t2', i
#        contentObjects.append(timestamps[i])
#    
#
#delays = []
#for i in range(len(contentObjects)):
#    iTs = interests.popleft()
#    cTs = contentObjects.popleft()
#    
#    delay = cTs - iTs
#    delays.append(delay)
#
#
#g = Gnuplot.Gnuplot()
#g.title('A simple example') # (optional)
#g('set data style linespoints') # give gnuplot an arbitrary command
## Plot a list of (x, y) pairs (tuples or a numpy array would
## also be OK):
#g.plot(delays)
#raw_input('Please press return to continue...\n')
#    
#print 'test'