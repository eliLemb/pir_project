from PIRServerBasic import PIRServerBasic
from PIRServerBasic import ThreadedRequestHandler
import logging
import threading
import socket
from OpCodes import OpCodes
import socketserver
from FrameBuilder import FrameBuilder


codes = OpCodes()

class T_StdRequestHandler(socketserver.BaseRequestHandler):
    from threading import RLock
        
    lock = RLock()
    
    def __init__(self, request, client_address, server):
        ThreadedRequestHandler.__init__(self, request, client_address, server,'T_StdRequestHandler')
        return
    
    def setup(self):
        socketserver.BaseRequestHandler.setup(self)
        self.send_hello_2_manager(self) #After the server up and running, it notifies the manager about itself
        
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
class StdServer(PIRServerBasic):
    frameBuilder = FrameBuilder()

    def __init__(self, log_name, server_address, handler_class=T_StdRequestHandler):
        self.selfIPAddress = server_address[0]
        self.selfPort = server_address[1]
        return PIRServerBasic.__init__(self, log_name, server_address, handler_class=handler_class)
    
    def server_activate(self):
        PIRServerBasic.server_activate(self)
        tupSocket = ('192.168.4.1', 31100)
        self.connection2Manager(tupSocket)
        return
    
    def activate(self, name, ipAddress, port):
        logger = logging.getLogger(name)
        logger.info("running at %s listens to port: %s ", ipAddress,port)
        tup_socket = (ipAddress, port) # let the kernel give us a port, tuple of the address and port
        server = StdServer('Server_Manager',tup_socket, T_StdRequestHandler)
        t = threading.Thread(target=server.serve_forever)
        t.start()
        
    def connection2Manager(self,tupSocket):
        self.logger.debug('creating socket connection to Manager_Server')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to Manager_Server')
        try:
            s.connect(tupSocket)
            connectedFlag = True
            t = threading.Thread(target=self.send_hello_2_manager(s))
            t.start()
        except Exception: 
            self.logger.debug('connection failed')        
        
        
    def send_hello_2_manager(self,s):
        self.logger.debug(StdServer.selfIPAddress)
        self.frameBuilder.assembleFrame(codes.getValue('hello')[0], StdServer.selfIPAddress + ":" + StdServer.selfPort)
        self.logger.debug('sending ''hello'' to Manager_Server')
        s.send(bytes(self.frameBuilder.getFrame(),"utf-8"))    
        T_StdRequestHandler.handle(self)
        


if __name__ == '__main__':
    port = 31109    
    ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    StdServer.activate(StdServer, 'Server_Manager', ipAddress, port)
    