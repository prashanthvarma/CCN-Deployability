'''
Created on Jan 15, 2013

@author: ccnx
'''
import os
import dpkt
import matplotlib.mlab as mlab
import numpy as np
import matplotlib.pyplot as plt


import ccn
GAUSS = False
REMOVE_MAX = False

FL_DF_POS = 1
FL_MF_POS = 2

catalogPath = '../../measurements/mtu/'
#fName = '1_file_delay_0ms_jit_0ms_cache_default'

class MeasurementObject:
    def __init__(self, filename, file_number, delay, jitter, cacheSize):
        self.filename = filename
        self.FILE_NUMBER = file_number
        self.DELAY = delay
        self.JITTER = jitter
        self.CACHE_SIZE = cacheSize
        
        self.meanDelay = 0
        self.stdDev = 0
        self.downloadTime = 0
        self.minDelay = 0
        self.maxDelay = 0
        self.numberOfContentObjects = 0
        self.maxNumberOfPackets = 0
        self.delayOfMaxNumOfPacketsMin = 0
        self.delayOfMaxNumOfPacketsMax = 0
        
    def processMeasurements(self,
                            meanDelay,
                            stdDev,
                            downloadTime,
                            minDelay, 
                            maxDelay,
                            numberOfContentObjects,
                            maxNumberOfPackets,
                            delayOfMaxNumOfPacketsMin,
                            delayOfMaxNumOfPacketsMax
                            ):
        self.meanDelay = meanDelay
        self.stdDev = stdDev
        self.downloadTime = downloadTime
        self.minDelay = minDelay
        self.maxDelay = maxDelay
        self.numberOfContentObjects = numberOfContentObjects
        self.maxNumberOfPackets = maxNumberOfPackets
        self.delayOfMaxNumOfPacketsMin = delayOfMaxNumOfPacketsMin
        self.delayOfMaxNumOfPacketsMax = delayOfMaxNumOfPacketsMax
    
    def produceString(self):
        rs = ''
        
        rs = rs + str(self.filename) + '\t'
        rs = rs + str(self.FILE_NUMBER) + '\t'
        rs = rs + str(self.DELAY) + '\t'
        rs = rs + str(self.JITTER) + '\t'
        rs = rs + str(self.CACHE_SIZE) + '\t'
        
        rs = rs + str(self.meanDelay) + '\t'
        rs = rs + str(self.stdDev) + '\t'
        rs = rs + str(self.downloadTime) + '\t'
        rs = rs + str(self.minDelay) + '\t'
        rs = rs + str(self.maxDelay) + '\t'
        rs = rs + str(self.numberOfContentObjects) + '\t'
        rs = rs + str(self.maxNumberOfPackets) + '\t'
        rs = rs + str(self.delayOfMaxNumOfPacketsMin) + '\t'
        rs = rs + str(self.delayOfMaxNumOfPacketsMax) + '\t'
        rs = rs + '\n'
        
        return rs
    
    def produceFirstLine(self):
        rs = ''
        
        rs = rs + 'filename' + '\t'
        rs = rs + 'FILE_NUMBER' + '\t'
        rs = rs + 'DELAY' + '\t'
        rs = rs + 'JITTER' + '\t'
        rs = rs + 'CACHE_SIZE' + '\t'
        
        rs = rs + 'meanDelay' + '\t'
        rs = rs + 'stdDev' + '\t'
        rs = rs + 'downloadTime' + '\t'
        rs = rs + 'minDelay' + '\t'
        rs = rs + 'maxDelay' + '\t'
        rs = rs + 'numberOfContentObjects' + '\t'
        rs = rs + 'maxNumberOfPackets' + '\t'
        rs = rs + 'delayOfMaxNumOfPacketsMin' + '\t'
        rs = rs + 'delayOfMaxNumOfPacketsMax' + '\t'
        rs = rs + '\n'
        
        return rs
        
#        for attr, value in self.__dict__.iteritems():
#            returnString = returnString + str(attr)
#            returnString = returnString + ' '
#            returnString = returnString + str(value)
#            returnString = returnString + '    '
#        returnString = returnString + '\n'
    
def save(path, ext='png', close=True, verbose=True):
    """Save a figure from pyplot.
     
    Parameters
    ----------
    path : string
    The path (and filename, without the extension) to save the
    figure to.
     
    ext : string (default='png')
    The file extension. This must be supported by the active
    matplotlib backend (see matplotlib.backends module). Most
    backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.
     
    close : boolean (default=True)
    Whether to close the figure after saving. If you want to save
    the figure multiple times (e.g., to multiple formats), you
    should NOT close it in between saves or you will have to
    re-plot it.
     
    verbose : boolean (default=True)
    Whether to print information about when and where the image
    has been saved.
     
    """
     
    # Extract the directory and filename from the given path
    directory = os.path.split(path)[0]
    filename = "%s.%s" % (os.path.split(path)[1], ext)
    if directory == '':
        directory = '.'
     
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
     
    # The final path to save to
    savepath = os.path.join(directory, filename)
     
    if verbose:
        print("Saving figure to '%s'..." % savepath),
     
    # Actually save the figure
    plt.savefig(savepath)
     
    # Close it
    if close:
        plt.close()
 
    if verbose:
        print("Done")
    
def bits(i,n):
    return tuple((0,1)[i>>j & 1] for j in xrange(n-1,-1,-1)) 

global interestsAndContents
global keyDuplication
global duplicationNr

def processIpPacket(ipPacket):
    global lastContentAdded
    global keyDuplication
    global duplicationNr
    
    CCN_TYPE_INTEREST = '\x01\xd2'
    CCN_TYPE_CONTENT = '\x04\x82'

    flagbits = bits(ipPacket[0].off, 16)
    
    df_flag = flagbits[FL_DF_POS]
    mf_flag = flagbits[FL_MF_POS]

    if df_flag and ipPacket[0].data.data[:2] == CCN_TYPE_INTEREST:
            ccnPacket = ccn.CcnPacket(ipPacket[0].data.data)
            chunkNrHex = ccnPacket.chunkNr.encode('hex')
            if not keyDuplication and interestsAndContents.has_key(chunkNrHex):
                print 'ALREADY HAS THE KEY', chunkNrHex
                keyDuplication = True
                duplicationNr = duplicationNr + 1
                print 'Duplication nr', duplicationNr
                
            if keyDuplication:
                chunkNrHex = chunkNrHex + '_' + str(duplicationNr)
                
            interestsAndContents[chunkNrHex] = ((ccnPacket, ipPacket[1]), (0, 0))
    elif ipPacket[0].data.data[:2] == CCN_TYPE_CONTENT:
        ccnPacket = ccn.CcnPacket(ipPacket[0].data.data)
        if df_flag:
            chunkNrHex = ccnPacket.chunkNr.encode('hex')
            
            if keyDuplication:
                #print 'Key duplication active'
                chunkNrHex = chunkNrHex + '_' + str(duplicationNr)
                
            if interestsAndContents.has_key(chunkNrHex):
                icTupleToodify = interestsAndContents[chunkNrHex]
                interestsAndContents[chunkNrHex] = (icTupleToodify[0], (ccnPacket, ipPacket[1]))
        else:
            chunkNrHex = ccnPacket.chunkNr.encode('hex')
            if keyDuplication:
                #print 'Key duplication active'
                chunkNrHex = chunkNrHex + '_' + str(duplicationNr)
                
            if interestsAndContents.has_key(chunkNrHex):
                icTupleToodify = interestsAndContents[chunkNrHex]
                interestsAndContents[chunkNrHex] = (icTupleToodify[0], (ccnPacket, 0))
                lastContentAdded = chunkNrHex
                
    elif (not df_flag and not mf_flag):
        if interestsAndContents.has_key(lastContentAdded):
            icTupleToodify = interestsAndContents[lastContentAdded]
            interestsAndContents[lastContentAdded] = (icTupleToodify[0], (icTupleToodify[1][0], ipPacket[1]))

def processFile(name, catalog):
    print 'processing file', name
    temp = name.split('_')
    FILE_NO = temp[0]
    DELAY = temp[3]
    JITTER = temp[5]
    CACHE_SIZE = temp[7]
    
    measurementObject = MeasurementObject(name, FILE_NO, DELAY, JITTER, CACHE_SIZE)
    filename = catalog + name
    
    f = open(filename)
    pcap = dpkt.pcap.Reader(f)
    
    ipPackets = []
    for ts, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        if type(eth.data) == dpkt.ip.IP:
            ip = eth.data
            ipPackets.append((ip, ts))
    
    downloadStartTime = ipPackets[0][1]
    downloadEndTime = ipPackets[len(ipPackets)-1][1]
    downloadTime = downloadEndTime - downloadStartTime
    print 'download time', downloadTime
    
    global interestsAndContents
    global lastContentAdded
    lastContentAdded = 0
    for ipPacket in ipPackets:
        try:
            processIpPacket(ipPacket)
        except Exception as e:
            print e
    
    delays = []
    for key in interestsAndContents.keys():
        iacTuple = interestsAndContents[key]
        interest = iacTuple[0]
        content = iacTuple[1]
        interestPacket = interest[0]
        interestTs = interest[1]
        
        contentPacket = content[0]
        contentTs = content[1]
        
        if contentPacket == 0 or contentTs == 0:
            continue
        delay = contentTs - interestTs
        delays.append(delay)
        
    if REMOVE_MAX:
        delays.remove(max(delays))
    
    if len(delays) == 0:
        print 'NO DELAYS IN THIS ONE'
        return measurementObject
    
    delaysMs = []
    #to ms
    for delay in delays:
        delaysMs.append(1000.0*delay);
    
    delays = delaysMs
            
    meanDelay = np.mean(delays)
    stdDev = np.std(delays)
    
#    delaysFiltered = []
#    for delay in delays:
#        if abs(delay-meanDelay)<1000:
#            delaysFiltered.append(delay)
#
#    delays = delaysFiltered

    print 'delay', meanDelay, 'std dev', stdDev
    minDelay = min(delays)
    maxDelay = max(delays)
    print 'min max del', minDelay, maxDelay
    numberOfContentObjects = len(interestsAndContents.keys())
    print 'number of content objects', numberOfContentObjects
    
    plt.figure(1)
    plt.clf()
    plt.cla()
    x = range(len(delays[0::10]))
  
    #plt.plot(x, delays[0::10], 'r.', markersize=1)
    plt.plot(x, delays[0::10], 'r+')
    plt.axhspan(meanDelay-stdDev, meanDelay+stdDev, alpha=0.25)
    plt.plot(x, len(x)*[meanDelay],linewidth=1)
    plt.xlabel('packet number')
    plt.ylabel('delay [ms]')
    plt.title('Delays of packets transmitted [ms] (delay: {0}, jitter: {1}, cache size: {2}, file: {3})'.format(DELAY, JITTER, CACHE_SIZE, FILE_NO), fontsize='small')
    
    save(catalog + name + '_fig1', ext="png", close=True, verbose=True)
    
    plt.figure(2)
    plt.clf()
    plt.cla()
    
    if GAUSS:
        x = np.linspace(min(delays), max(delays),200)
        plt.plot(x,mlab.normpdf(x,meanDelay,stdDev), color='red')
    
    spacing = np.linspace(min(delays), max(delays), 200, retstep=True)
    b = spacing[0]
    w = spacing[1]
    hist, bin_edges = np.histogram(delays, bins = b)
    
    hist_l = list(hist)
    bin_edges_l = list(bin_edges)
    maxNumberOfPackets = max(hist_l)
    maxIndex = hist_l.index(maxNumberOfPackets)
    delayOfMaxNumOfPacketsMin = bin_edges_l[maxIndex]
    delayOfMaxNumOfPacketsMax = delayOfMaxNumOfPacketsMin+w
    
    plt.bar(bin_edges[:-1], hist, width = w)
    plt.xlim(min(bin_edges), max(bin_edges))
    plt.xlabel('Delay [ms]')
    plt.ylabel('Number of packets received with a given delay')
    plt.title('Histogram of delays of received packets [ms] (delay: {0}, jitter: {1}, cache size: {2}, file: {3})'.format(DELAY, JITTER, CACHE_SIZE, FILE_NO), fontsize='small')
    
    save(catalog + name + '_fig2', ext="png", close=True, verbose=True)
    #plt.show()
    
    measurementObject.processMeasurements(meanDelay,
                        stdDev,
                        downloadTime,
                        minDelay, 
                        maxDelay,
                        numberOfContentObjects,
                        maxNumberOfPackets,
                        delayOfMaxNumOfPacketsMin,
                        delayOfMaxNumOfPacketsMax)
    
    return measurementObject


filesToProcess = os.listdir(catalogPath)
#filesToProcess = ['2_file_delay_0ms_jit_0ms_cache_50000']

measurementObjects = []
for fName in filesToProcess:
    if fName.count('png') == 0 and fName.count('txt') == 0 and fName.count('obj') == 0:
        interestsAndContents = {}
        keyDuplication = False
        duplicationNr = 0
        measurementObject = processFile(fName, catalogPath)
        measurementObjects.append(measurementObject)

filehandler = open(catalogPath + 'measurements.txt', 'w')
filehandler.write(measurementObjects[0].produceFirstLine())
for measurementObject in measurementObjects:
    filehandler.write(measurementObject.produceString())
filehandler.close()

import pickle
filehandler = open(catalogPath + 'measurementObjects.obj', 'w') 
pickle.dump(measurementObjects, filehandler)
filehandler.close()

x = []
meanDelay = []
stdDev = []
numberOfContentObjects = []
for measurementObject in measurementObjects:
    x.append(measurementObject.CACHE_SIZE)
    meanDelay.append(measurementObject.meanDelay)
    stdDev.append(measurementObject.stdDev)
    numberOfContentObjects.append(measurementObject.numberOfContentObjects)

#plt.figure(4)
#plt.plot(x, meanDelay, 'r.')
#save('fig4', ext="png", close=True, verbose=True)
#    
#plt.figure(5)
#plt.plot(x, stdDev, 'r.')
#save('fig5', ext="png", close=True, verbose=True)
#
#plt.figure(6)
#plt.plot(x, numberOfContentObjects, 'r.')
#save('fig6', ext="png", close=True, verbose=True)
