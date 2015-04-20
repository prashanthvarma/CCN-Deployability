'''
Created on Jan 17, 2013

@author: ccnx
'''


CCN_TYPE_INTEREST = '\x01\xd2'
CCN_TYPE_CONTENT = '\x04\x82'

HEADER_NAME1 = '\xf2\xfa\xcd'
HEADER_NAME2 = '\x00\xfa' #\xc5 or \xd5
HEADER_NAME3 = '\x00\xfa\xbd'
HEADER_CHUNK_NR = '\x00\xfa' #\x95 \x9d
HEADER_END = '\x00\x00'

#only for content packets
HEADER_SIGNED_INFO = '\x01\xa2\x03\xe2\x02\x85'
HEADER_CONTENT = '\x01\x9a'

class CcnPacket:
    def __init__(self, data):
        
        self.type = data[:2]
        
        if self.type  == CCN_TYPE_INTEREST:
            self.endOfHeader = self.processHeaderName(data)
            
        elif self.type  == CCN_TYPE_CONTENT:
            self.endOfHeader = self.processHeaderName(data)
        else:
            raise Exception('wrong type for CCN packet')
        
        
    def processHeaderName(self, data):
        tmp = data.split(HEADER_NAME1, 1)
        if len(tmp) == 2:
            tmp = tmp[1].split(HEADER_NAME2 ,1)
            self.name1 = tmp[0]
        else:
            raise Exception('Wrong format level1')
            
        if len(tmp) == 2:
            tmp = tmp[1].split(HEADER_NAME3 ,1)
            self.name2 = tmp[0]
        else:
            raise Exception('Wrong format level2', tmp)
        
        if len(tmp) == 2:
            tmp = tmp[1].split(HEADER_CHUNK_NR ,1)
            self.name3 = tmp[0]
        else:
            raise Exception('Wrong format level3')
        
        if len(tmp) == 2:
            tmp = tmp[1][1:].split(HEADER_END ,1)
            self.chunkNr = tmp[0]
        else:
            raise Exception('Wrong format level4', tmp)
        
        if len(tmp) == 2:
            return tmp[1]
        else:
            raise Exception('Wrong format level4')
            