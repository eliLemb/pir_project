'''
@author: Eli
'''


import logging
import struct
import math
class FrameBuilder(object):
    '''
    classdocs
    '''
    logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)
    
    frame2Send = bytearray()
    frame2SendPickle = []
    def __init__(self):
        self.logger = logging.getLogger("Frame Builder ")
    def assembleFrame (self,opCode,payload):
        try:
            self.frame2Send.clear()
            self.frame2Send.append(opCode)
            numOfBytesOfLength = math.ceil((len(payload).bit_length()/8))
            self.frame2Send.append(numOfBytesOfLength)   ##Number of bits of the length number
            lengthAsHex = hex(len(payload))
            lengthAsHex = lengthAsHex[2:]
            if len(lengthAsHex)%2 == 1:
                lengthAsHex = ''.join(('0',lengthAsHex))
            index = 0 
            for _ in range(0,numOfBytesOfLength):
                num = ''.join(('0x',lengthAsHex[index:index+2])) 
                numAsByte = num.encode('utf_8')
                self.frame2Send.append(int(lengthAsHex[index:index+2],16))
                index = index + 2
                
#             self.frame2Send.extend(str.encode(str(len(payload))))           ##the length of the payload
            if(opCode == 242):
                self.frame2Send.extend(payload)
            else:
                self.frame2Send.extend(str.encode(payload))
        except BufferError:
            self.logger.debug('Memory error on ByteArray object')
    
    def assembleFramePickle (self,opCode,payload):
        self.frame2SendPickle.append(opCode)
        self.frame2SendPickle.append(payload)
    
    def getFramePickle(self):
        return self.frame2SendPickle
    
    def getFrame(self):
        return self.frame2Send