'''
@author: Eli
'''


import logging

class FrameBuilder(object):
    '''
    classdocs
    '''
    logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)
    
    frame2Send = bytearray()
    def __init__(self):
        self.logger = logging.getLogger("Frame Builder ")
    def assembleFrame (self,opCode,payload):
        try:
            self.frame2Send.clear()
            self.frame2Send.append(opCode)
            self.frame2Send.append(len(payload))
            self.frame2Send.extend(str.encode(payload))
        except BufferError:
            self.logger.debug('Memory error on ByteArray object')
        
    def getFrame(self):
        return self.frame2Send