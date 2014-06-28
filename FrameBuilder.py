'''
@author: Eli
'''



class FrameBuilder(object):
    '''
    classdocs
    '''
    
    frame2Send = bytearray()
    def __init__(self):
        '''
        Constructor
        '''
    def assembleFrame (self,opCode,payload):
        self.frame2Send.clear()
        self.frame2Send.append(opCode)
        self.frame2Send.append(len(payload))
        self.frame2Send.extend(str.encode(payload))
        
    def getFrame(self):
        return self.frame2Send