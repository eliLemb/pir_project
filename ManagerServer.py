from PIRServerBasic import PIRServerBasic 
from PIRServerBasic import ThreadedRequestHandler
import logging
import threading
import socket
from OpCodes import OpCodes
import socketserver


## T stands for threaded
class T_ManagerRequestHandler(ThreadedRequestHandler):
    from threading import RLock
        
    lock = RLock()
    
    def __init__(self, request, client_address, server):
        ThreadedRequestHandler.__init__(self, request, client_address, server,'T_ManagerRequestHandler')
        return
    
        
    def handleMsg(self,recvOpcode,msg):
        code = OpCodes.getCode(self, recvOpcode)
            
        if code == 'hello':
            self.logger.info(code)
        elif code == 'hello_Ack':
            self.logger.info (code)
        elif code == 'server_quantity_request':
            self.logger.info (code)
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




logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   
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
    
    
    
    
    
    
    
    
    
    
    
    
    