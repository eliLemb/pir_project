import logging
import socket
import threading
import queue
import random

from FrameBuilder import FrameBuilder
from OpCodes import OpCodes
from PIRServerBasic import PIRServerBasic 
from PIRServerBasic import ThreadedRequestHandler
from threading import RLock
from bitstring import BitArray

q_freeIndexs = queue.Queue()
logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   
active_servers = {}
codes = OpCodes()

#T stands for threaded
class T_ManagerRequestHandler(ThreadedRequestHandler):
    
#     frameBuilder = FrameBuilder()
    
    
    def __init__(self, request, client_address, server):
        ThreadedRequestHandler.__init__(self, request, client_address, server,'T_ManagerRequestHandler')
        return
    
    ##Handle hello msg from STD_server and insert it's ip and port
    def handleHello(self,payload):
        modifiedPayload = payload.decode('utf-8')
        serverCredential = modifiedPayload.split(':')
        insertIndex = ManagerServer.addServer2ActiveServers(self.server,serverCredential)
        s_stdServer = self.connection_2_target(active_servers[insertIndex])
    
        if s_stdServer != None:
            self.assamble4ReplyHello(insertIndex,s_stdServer)
            self.send_2_target(s_stdServer)
            return insertIndex
        else:
            return -1
    
    def assamble4ReplyHello(self,insertIndex,s_stdServer):
        self.logger.debug('reply ''hello_Ack'' to %s ',s_stdServer.getsockname())
        self.frameBuilder.assembleFrame(codes.getValue('hello_ack')[0],str(insertIndex))
#         s_stdServer.send(bytes(self.frameBuilder.getFrame())) 
   
    
    def handleServerQuantity(self):
        self.assamble4ServerQuantity()
        self.request.send(self.frameBuilder.getFrame())
    
    def assamble4ServerQuantity(self):
        self.logger.debug('reply ''server_quantity_request'' to %s ',self.request.getsockname())
        self.logger.info('Current servers count %s',active_servers.__len__())
        self.frameBuilder.assembleFrame(codes.getValue('server_quantity_reply')[0],str(active_servers.__len__()))
           
           
    def handleDBLengthReq(self):
        self.assamble4DBLength()
        self.request.send(self.frameBuilder.getFrame())

    def assamble4DBLength(self):        
        bitLength = ManagerServer.b_DB._getlength()
        self.logger.info('DB length in bits: %s.',bitLength)
        self.logger.debug('reply ''db_length'' to %s ',self.request.getsockname())
        self.frameBuilder.assembleFrame(codes.getValue('db_length')[0],str(bitLength))
               
    def killThisServer(self):
        pass
#         self.finish()
#         self.server.server_close()
        
           
           
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
            self.handleDBLengthReq()
        elif code == 'query':
            self.logger.info (code)
        elif code == 'query_response':
            self.logger.info (code)
        elif code == 'ipAndPortRequest':
            self.logger.info (code)
        elif code == 'ipAndPortReply':
            self.logger.info (code)
        elif code == 'terminate':
            self.logger.info (code)
            self.killThisServer()
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
    lock = RLock()

    def __init__(self, log_name, server_address, handler_class=T_ManagerRequestHandler):
        return PIRServerBasic.__init__(self, log_name, server_address, handler_class=handler_class)

    def activate(self, name, ipAddress, port):
#         logger = logging.getLogger(name)
#         logger.info("running at %s listens to port: %s ", ipAddress,port)
        tup_socket = (ipAddress, port) # let the kernel give us a port, tuple of the address and port
        server = ManagerServer(name,tup_socket, T_ManagerRequestHandler)
        PIRServerBasic.activate(self,name, ipAddress, port, server)
        self.addServer2ActiveServers(server,tup_socket)
        t = threading.Thread(target=server.serve_forever)
        t.start()
        self.genarateDB(self)

    def addServer2ActiveServers(self,serverCredential):
        tup_serverCredential = serverCredential[0],int(serverCredential[1])
        self.lock.acquire(blocking=True)
        insertIndex = self.ifServerRegistered(tup_serverCredential)
#         insertIndex = active_servers.__len__()
        active_servers[insertIndex] = tup_serverCredential
        self.lock.release()
        self.logger.info('server was added at: %s' ,insertIndex)
        return insertIndex        
    
    
    def ifServerRegistered(self,serverCredential):
        try:
            insertIndex =  [ k for k, element in active_servers.items() if element == serverCredential]
            if not insertIndex:
                if q_freeIndexs.empty():
                    return active_servers.__len__()
                else:
                    return q_freeIndexs.get_nowait()
            else:
                return insertIndex[0]
        except Exception:
            return 
    
    def genarateDB(self):
        self.b_DB = BitArray(hex(random.getrandbits(self.dbLengthMB *self.c_MB)))
        
        

if __name__ == '__main__':
    #     import threading
    port = 31100    
    ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    ManagerServer.activate(ManagerServer, 'Manager_Server', ipAddress, port)
    
    
    
    
    
    
    
    
    
    
    
    
    
