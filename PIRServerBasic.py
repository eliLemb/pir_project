#!/usr/bin/env python

import logging
import socketserver
import threading
import socket
from OpCodes import OpCodes
from FrameBuilder import FrameBuilder




logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   
port = 0    
IP_CACHE = {'server1' : ('192.168.4.1',port)}

class ThreadedRequestHandler(socketserver.BaseRequestHandler):
    from threading import RLock
        
    lock = RLock()
    
    def __init__(self, request, client_address, server, name):
        self.logger = logging.getLogger(name)
        self.logger.debug('__init__')
        self.logger.debug('Client %s Connected' ,client_address)
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return
    
    def setup(self):
        self.logger.debug('setup')
        return socketserver.BaseRequestHandler.setup(self)
    
    def handle(self):
        self.logger.debug('handle')
        while True:
        # Echo the back to the client
            try:
                data = self.request.recv(2)
                if data == '' or len(data) == 0:
                    break
            except Exception: 
                self.logger.debug('recv failed')
                break
            #Got data Successfully
            recvOpcode = data[0] #first byte is op code
            size = data[1]
            try:
                data = self.request.recv(size)
                if data == '' or len(data) == 0:
                    break
            except Exception: 
                self.logger.debug('recv data failed')
                break
            payload = data
            self.handleMsg(recvOpcode,payload)
                
#             try:
#                 self.logger.debug('recv()->"%s"', payload)
#                 cur_thread = threading.currentThread()
#                 response = '%s: %s' % (cur_thread.getName(), payload)
#                     
# #                 self.lock.acquire(blocking=True)
#                 self.request.send(bytes(response,"utf-8"))
# #                 self.lock.release()
#             except Exception: 
#                 self.logger.debug('send failed')
#                 break
        return
            
    
    def finish(self):
        self.logger.debug('finish')
        return socketserver.BaseRequestHandler.finish(self)

    def send_2_target(self,s_activeConnection):
        try:
            s_activeConnection.send(bytes(self.frameBuilder.getFrame()))
        except Exception: 
            self.logger.debug('send failed')    
    
    
    
    
        
class PIRServerBasic(socketserver.ThreadingMixIn,socketserver.TCPServer):
    frameBuilder = FrameBuilder()

    def __init__(self, log_name,server_address, handler_class=ThreadedRequestHandler):
        self.logger = logging.getLogger(log_name)
        self.logger.debug('__init__')
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        return
      
    def server_activate(self):
        self.logger.debug('server_activate')
        socketserver.TCPServer.server_activate(self)
        return
       
    def serve_forever(self):
        self.logger.debug('waiting for request')
#         self.logger.info('Handling requests, press <Ctrl-C> to quit')
        while True:
            self.handle_request()
        return
       
    def handle_request(self):
        self.logger.debug('handle_request')
        return socketserver.TCPServer.handle_request(self)
       
    def verify_request(self, request, client_address):
#         self.logger.debug('verify_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.verify_request(self, request, client_address)
    
    def process_request_thread(self, request, client_address):
#         self.logger.debug('process_request_thread(%s, %s)', request, client_address)
        return socketserver.ThreadingMixIn.process_request_thread(self, request, client_address)
 
    def finish_request(self, request, client_address):
#         self.logger.debug('finish_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.finish_request(self, request, client_address)
         
    def close_request(self, request_address):
#         self.logger.debug('close_request(%s)', request_address)
        return socketserver.TCPServer.close_request(self, request_address)
    
    def server_close(self):
        self.logger.debug('server_close')
        return socketserver.TCPServer.server_close(self)
    
    def activate(self,name,ipAddress,port,server):
        server.logger = logging.getLogger(name)
        server.logger.info("running at %s listens to port: %s ", ipAddress,port)
#         tup_socket = (ipAddress, port) # let the kernel give us a port, tuple of the address and port
#         server = PIRServerBasic('STD_PirServer',tup_socket, ThreadedRequestHandler)
#         t = threading.Thread(target=server.serve_forever)
#         t.start()

    
#     #################################################################################################
#     ##
#     ##        DNS Related stuff
#     ##
#     #################################################################################################    
#     from threading import Thread, RLock
#     import lookup
#     import ipaddress
#     
#     class DNSQuery(object):
#         
#         lock = RLock()
#     
#         def __init__(self, data):
#             self.data = data
#     
#     #         _type = (data[2] >> 3) & 15  # Opcode bits
#     
#             self.domain = self.get_domain(240, data)
#             self.ip = ''
#     
#         @staticmethod
#         def get_domain(_type, data):
#             domain =  bytes.decode(data)
#     #         if _type == 240:  # Standard query
#     #             ini = 0
#     #             lon = data[ini]
#     #             while lon != 0:
#     #                 domain.append(str(data[ini + 1:ini + lon + 1], 'utf-8'))
#     #                 ini += lon + 1
#     #                 lon = data[ini]
#             return domain
#     
#         def look_up_ip(self):
#             if not  self.domain in DNSQuery.IP_CACHE:
#                 pass
#     #             ip_addr = lookup.get_ip(self.data)
#     #             with DNSQuery.lock:
#     #                 DNSQuery.IP_CACHE[self.domain] = ip_addr
#                 
#             else:
#                 print('In cache', self.domain, DNSQuery.IP_CACHE[self.domain])
#             return DNSQuery.IP_CACHE[self.domain][0]
#     
#         def response(self):
#             try:
#                 self.ip = self.look_up_ip()
#             except:
#                 return ''
#     #         if self.domain and self.ip:
#     #             packet = self.data[:2] + b"\x81\x80"
#     #             packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'  # Questions and Answers Counts
#     # 
#     #             packet += self.data[12:]  # Original Domain Name Question
#     #             packet += b'\xc0\x0c'  # Pointer to domain name
#     # 
#     #             packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
#     #             packet += ipaddress.IPv4Address(self.ip).packed  # 4bytes of IP
#     #         else:
#     #             packet = lookup.get_raw(self.data)
#     #             print('DNS Server fatal failed...')
#             return self.ip
#     
#     
#     class DNSResolver(Thread):
#     
#         def __init__(self, udps, addr, data):
#             super(DNSResolver, self).__init__()
#             self.udps = udps
#             self.addr = addr
#             self.data = data
#     
#         def run(self):
#             print("Request from: ", ':'.join([str(i) for i in self.addr]))
#     
#             try:
#                 dns_query = DNSQuery(self.data)
#                 dns_query.response()
#     #             dns_query.lock.acquire(blocking=True)
#     #             self.udps.send(str.encode(dns_query.response()))
#     #             dns_query.lock.release()
#                 
#             except OSError:
#                 return  # closed by client
#             print('Response: {0} -> {1}'.format(dns_query.domain, dns_query.ip))
#      

#     
#     
# ##                End of DNS Section
# #################################################################################################


    

# if __name__ == '__main__':
#     port = 31109    
#     ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
#     PIRServerBasic.activate(PIRServerBasic, 'Server', ipAddress, port)
#     
#     
#     
#     logger = logging.getLogger('Server')
#     logger.info("running at %s ", ipAddress)
#     address = (ipAddress, port) # let the kernel give us a port
#     server = PirServer(address, ThreadedEchoRequestHandler)
#     ip, port = server.server_address # find out what port we were given
#     #     self.logger.log('Server loop running in thread:')
#     t = threading.Thread(target=server.serve_forever)
#     #     t.setDaemon(True) # don't hang on exit
#     t.start()
    
    #     logger = logging.getLogger('client')
    #     logger.info('Server on %s:%s', ip, port)
