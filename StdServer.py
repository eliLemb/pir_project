from PIRServerBasic import PIRServerBasic
from PIRServerBasic import ThreadedRequestHandler
import logging
import threading
import socket
from OpCodes import OpCodes



codes = OpCodes()
logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   
managerServerAddresPort = ('192.168.4.1',31100)
class T_StdRequestHandler(ThreadedRequestHandler):
    from threading import RLock
        
    lock = RLock()
    
    def __init__(self, request, client_address, server):
        ThreadedRequestHandler.__init__(self, request, client_address, server,'T_StdRequestHandler')
        return
#     
#     def setup(self):
#         socketserver.BaseRequestHandler.setup(self)
        
            
#         self.send_hello_2_manager(self) #After the server up and running, it notifies the manager about itself
        
    def handleMsg(self,recvOpcode,msg):
        code = OpCodes.getCode(self, recvOpcode)
            
        if code == 'hello':
            self.logger.info(code)
        elif code == 'hello_ack':
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




class StdServer(PIRServerBasic):

    def __init__(self, log_name, server_address, handler_class=T_StdRequestHandler):
        self.selfIPAddress = server_address[0]
        self.selfPort = server_address[1]
        return PIRServerBasic.__init__(self, log_name, server_address, handler_class=handler_class)
    
    def server_activate(self):
        PIRServerBasic.server_activate(self)
        s_openToManager = self.connection_2_Manager(managerServerAddresPort)
        if s_openToManager != None:
            t = threading.Thread(target=self.send_hello_2_manager(s_openToManager))
            t.start()
             
        else:
            self.logger.info('connection to Manager Server failed')
            self.shutdown()
#         tupSocket = ('192.168.4.1', 31100)
#         self.connection2Manager(tupSocket)
        return 
    
    def activate(self, name, ipAddress, port):
#         logger = logging.getLogger(name)
#         logger.info("running at %s listens to port: %s ", ipAddress,port)
        tup_socket = (ipAddress, port) # let the kernel give us a port, tuple of the address and port
        server = StdServer(name,tup_socket, T_StdRequestHandler)
        PIRServerBasic.activate(self,name, ipAddress, port, server)
        t = threading.Thread(target=server.serve_forever)
        t.start()
        
    def connection_2_Manager(self,tu_address):
        self.logger.debug('creating socket connection to Manager_Server')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(tu_address)
            return s
#             connectedFlag = True
        except Exception: 
            self.logger.debug('connection failed')        
        
        
    def send_hello_2_manager(self,s_openToManager):
        self.logger.debug(self.selfIPAddress)
        self.frameBuilder.assembleFrame(codes.getValue('hello')[0], self.selfIPAddress + ":" + str(self.selfPort))
        self.logger.debug('sending ''hello'' to Manager_Server')
        
        s_openToManager.send(bytes(self.frameBuilder.getFrame()))
#         while True:

#             s_openToManager.recv()        
#         T_StdRequestHandler.handle(self)
        


if __name__ == '__main__':
    port = 31105
    ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    StdServer.activate(StdServer, 'STD_Server', ipAddress, port)
    