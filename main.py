# import socket
# import random
# 
# def client(string):
#     HOST, PORT = 'localhost', 31100
#     # SOCK_STREAM == a TCP socket
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     #sock.setblocking(0)  # optional non-blocking
#     sock.connect((HOST, PORT))
# 
#     print ("sending data => [%s]" % (string))
# 
#     sock.send(bytes(string, "utf-8"))
#     reply = sock.recv(16384)  # limit reply to 16K
#     print ("reply => \n [%s]" % (reply))
#     sock.close()
#     return reply
# 
# def main():
#     client('Python Rocks')
# 
# if __name__ == "__main__":
#     main()
from _ctypes import sizeof



'''''
http://python.about.com/od/python30/ss/30_strings_3.htm
'''''
import logging
import threading
import socket
from FrameBuilder import FrameBuilder
from time import sleep
from OpCodes import OpCodes
import binascii
import random
from bitstring import BitArray
import time

logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)
codes = OpCodes()

if __name__ == "__main__":
    logger = logging.getLogger('client')
    
#     while True:
#         sleep(1)
#         print(int(time.time()%1000000))
#     
#     
    s_c = ('123',344)
    a_s = {1: ('123',344),2:('345',1254667)}
    whatreturned = [ k for k, element in a_s.items() if element == s_c]
    for key, element in a_s.items():  
        print(key,element)



#     p_bitstring = BitArray(hex(random.getrandbits(2**20)))
#     logger.debug('BitArray s: %s' ,p_bitstring)
    
    frameBuilder = FrameBuilder()
    ip, port = '192.168.4.1', 31100
#     print (codes.get_code(b'242'))

    logger.info('Server on %s:%s', ip, port)
    
    # Connect to the server
    logger.debug('creating socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug('connecting to server')
    connectedFlag = True
    try:
        s.connect((ip, port))
    except Exception: 
        logger.debug('connection failed')
        connectedFlag = False
    while connectedFlag:

        message = input("Enter your message to the EchoServer: ")
#         print (codes.getValue('db_length')[0])
        frameBuilder.assembleFrame(codes.getValue('hello')[0],message)
#         my_bytes.append(245)
#         my_bytes.append(len(message))
#         my_bytes.extend(str.encode(message))
        logger.debug('sending data: "%s"', message)
        len_sent = s.send(frameBuilder.getFrame())
#         len_sent = s.send('240')

        # Receive a response
        logger.debug('waiting for response')
        response = s.recv(len_sent + len(threading.currentThread().getName()) + 3)
        logger.debug('response from server: "%s"', response)
#         print('response from server: ', response.encode("utf-8"))
        sleep(0.05)
    
    # Clean up
    logger.debug('closing socket')
    s.close()
    logger.debug('Client done')



