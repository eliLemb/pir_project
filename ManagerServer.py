import logging
import socket
import threading

from FrameBuilder import FrameBuilder
from OpCodes import OpCodes
from PIRServerBasic import PIRServerBasic 
from PIRServerBasic import ThreadedRequestHandler


logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   
active_servers = {}
codes = OpCodes()

#T stands for threaded
class T_ManagerRequestHandler(ThreadedRequestHandler):
    from threading import RLock
    frameBuilder = FrameBuilder()
    
    lock = RLock()
    
    def __init__(self, request, client_address, server):
        ThreadedRequestHandler.__init__(self, request, client_address, server,'T_ManagerRequestHandler')
        return
    
    ##Handle hello msg from STD_server and insert it's ip and port
    def handleHello(self,payload):
        modifiedPayload = payload.decode('utf-8')
        serverCredential = modifiedPayload.split(':')
        insertIndex = active_servers.__len__()
        self.lock.acquire(blocking=True)
        active_servers[insertIndex] = (serverCredential[0],int(serverCredential[1]))
        self.lock.release()
        self.logger.info('STD_server was added at: %s' ,insertIndex)
        s_stdServer = self.connection_2_target(active_servers[insertIndex])
        self.assamble4ReplyHello(insertIndex,s_stdServer)
        self.send_2_target(s_stdServer)
        return insertIndex
    
    def assamble4ReplyHello(self,insertIndex,s_stdServer):
        self.logger.debug('reply ''hello_Ack'' to %s ',s_stdServer.getsockname())
        self.frameBuilder.assembleFrame(codes.getValue('hello_ack')[0],str(insertIndex))
#         s_stdServer.send(bytes(self.frameBuilder.getFrame())) 
   
    
    def handleServerQuantity(self):
        self.assamble4ServerQuantity()
        self.request.send(self.frameBuilder.getFrame())
    
    def assamble4ServerQuantity(self):
        self.logger.debug('reply ''server_quantity_request'' to %s ',self.request.getsockname())
        self.frameBuilder.assembleFrame(codes.getValue('server_quantity_reply')[0],str(active_servers.__len__()))
           
           
           
           
           
           
    ##Handling messages       
    def handleMsg(self,recvOpcode,msg):
        code = OpCodes.getCode(self, recvOpcode)
            
        if code == 'hello':
            self.logger.info(code)
            self.handleHello(msg)
        elif code == 'hello_ack':
            self.logger.info (code)
        elif code == 'server_quantity_request':
            self.logger.info (code)
            self.handleServerQuantity()
        elif code == 'server_quantity_reply':
            self.logger.info (code)
        elif code == 'servers_up':
            self.logger.info (code)
        elif code == 'servers_failed':
            self.logger.info (code)
        elif code == 'db_length':
            self.logger.info (code)
        elif code == 'db_length_request':
            self.logger.info (code)
        elif code == 'query':
            self.logger.info (code)
        elif code == 'query_response':
            self.logger.info (code)
        elif code == 'terminate':
            self.logger.info (code)
        elif code == 'ipAndPortRequest':
            self.logger.info (code)
        elif code == 'ipAndPortReply':
            self.logger.info (code)
        else:
            self.logger.info("Bad opCode")

       
    def connection_2_target(self,tu_address):
        self.logger.debug('creating socket connection to %s' , tu_address)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(tu_address)
            return s
#             connectedFlag = True
        except Exception: 
            self.logger.debug('connection to %s failed',tu_address)        
        
    
        
        
class ManagerServer(PIRServerBasic):
   
    def __init__(self, log_name, server_address, handler_class=T_ManagerRequestHandler):
        return PIRServerBasic.__init__(self, log_name, server_address, handler_class=handler_class)

    def activate(self, name, ipAddress, port):
#         logger = logging.getLogger(name)
#         logger.info("running at %s listens to port: %s ", ipAddress,port)
        tup_socket = (ipAddress, port) # let the kernel give us a port, tuple of the address and port
        server = ManagerServer(name,tup_socket, T_ManagerRequestHandler)
        PIRServerBasic.activate(self,name, ipAddress, port, server)
        t = threading.Thread(target=server.serve_forever)
        t.start()





if __name__ == '__main__':
    #     import threading
    port = 31100    
    ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    ManagerServer.activate(ManagerServer, 'Manager_Server', ipAddress, port)
    
    
    
    
    
    
    
    
    
    
    
    
    
