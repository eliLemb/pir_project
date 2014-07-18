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

from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *

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


class client_window(Frame):
    
    def __init__(self, parent):
        self.queryMethod=''
        self.desirableBit=0
        self.myParent = parent 
        self.myParent.title('PIR Client')
        self.masterFrame = ttk.Frame(self.myParent,padding=(0,10,0,5)) ###
        self.masterFrame.grid(column=0, row=0, sticky=(N, S, E, W))
         #------ constants for controlling layout ------
        button_width = 12      ### (1)
        button_height = 3
        
        button_padx = "2"    ### (2)
        button_pady = "1"    ### (2)

        buttons_frame_padx =  "3"   ### (3)
        buttons_frame_pady =  "3"   ### (3)        
        buttons_frame_ipadx = "3"   ### (3)
        buttons_frame_ipady = "3"   ### (3)
        # -------------- end constants ----------------

        self.style = ttk.Style(self.myParent)
        self.style.configure('TButton', font=("Arial", 8,'bold'))#larger Font for buttons
        self.style.configure('TLabel', font=("Arial", 10,'bold'))#larger Font for buttons
        
        self.icn_SM_disconnected = PhotoImage(file="icons/Red-icon32.png")
        self.icn_SM_connected = PhotoImage(file="icons/Green-icon32.png")
        self.icn_compare = PhotoImage(file="icons/compare24.png")
        self.icn_query = PhotoImage(file="icons/download24.png")
        self.icn_exit = PhotoImage(file="icons/exit24.png")

        self.lbl_SMAddress = ttk.Label(self.masterFrame, compound=LEFT, style='TLabel', text="Server manager address: " )
        self.lbl_SMAddress.grid(row=0,column=0, columnspan=2, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))

        self.txt_SMAddress = ttk.Entry(self.masterFrame, justify=CENTER, width=button_width)
        self.txt_SMAddress.insert(0, '192.168.4.1')
        self.txt_SMAddress.grid(row=0,column=7, columnspan=1, rowspan=1, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(E))
        
#         self.lbl_padding = ttk.Label(self.masterFrame, compound=LEFT)
#         self.lbl_padding.grid(row=0,column=3, columnspan=3, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))
#         
        self.btn_connect = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickConnect, style='TButton', text="Connect ",width=button_width )
        self.btn_connect.grid(row=2,column=0, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))
        
        self.lbl_connectionSts = Label(self.masterFrame, image=self.icn_SM_disconnected)
        self.lbl_connectionSts.grid(row=2, column=7, sticky=(E))
        
        self.chk_pir = ttk.Radiobutton(self.masterFrame, text='PIR', variable=self.queryMethod, value='pir')
        self.chk_pir.grid(row=3,column=0,columnspan=2, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W, S))
        
        self.chk_regular = ttk.Radiobutton(self.masterFrame, text='Standard', variable=self.queryMethod, value='regular')
        self.chk_regular.grid(row=4,column=0,columnspan=2, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W, S))
        
        self.scl_bitChoice = ttk.Scale(self.masterFrame, orient=HORIZONTAL, from_=1.0, to=500.0,command=self.updatDesiedBit)
        self.scl_bitChoice.grid(row=5, column=0, columnspan=8, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady,sticky=(W,E))
        
        self.lbl_bitIndex = ttk.Label(self.masterFrame, compound=CENTER,  style='TLabel' , text = '1')
        self.lbl_bitIndex.grid(row=6,column=1, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W,E))
        
        
        self.btn_query = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickConnect, style='TButton', text="Get value ",image=self.icn_query, width=button_width )
        self.btn_query.grid(row=7,column=0, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))
         
        self.lbl_result = ttk.Label(self.masterFrame, compound=CENTER, style='TLabel', text='XX',justify=LEFT)
        self.lbl_result.grid(row=7,column=7, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(E))
        
       
        self.btn_compare = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickConnect, style='TButton', text="Compare ", image=self.icn_compare, width=button_width )
        self.btn_compare.grid(row=8,column=0, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))
        
        self.btn_exit = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickExit, style='TButton', text="Exit ", image=self.icn_exit, width=button_width )
        self.btn_exit.grid(row=8,column=7, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(E))
       
       
       
       
       
       
       
       
       
       
    def updatDesiedBit(self,value):    
        self.lbl_bitIndex.configure(text= str(int(float(value))))
    def clickConnect(self): 
        self.ServerConnected()
#         self.scl_bitChoice.configure(to=1000)
    def ServerConnected(self):
        self.lbl_connectionSts.config(image=self.icn_SM_connected)
    def ServerDisconnected(self):
        self.lbl_connectionSts.config(image=self.icn_SM_disconnected)
    def clickExit(self):
        self.myParent.destroy()


    
if __name__ == "__main__":
    logger = logging.getLogger('Client')
    root = Tk()
    appWindownManager = client_window(root)
    root.mainloop()
#     while True:
#         sleep(1)
#         print(int(time.time()%1000000))
#     
#     
#     s_c = ('123',344)
#     a_s = {1: ('123',344),2:('345',1254667)}
#     whatreturned = [ k for k, element in a_s.items() if element == s_c]
#     for key, element in a_s.items():  
#         print(key,element)
# 
# 
# 
# #     p_bitstring = BitArray(hex(random.getrandbits(2**20)))
# #     logger.debug('BitArray s: %s' ,p_bitstring)
#     
#     frameBuilder = FrameBuilder()
#     ip, port = '192.168.2.121', 31100
# #     print (codes.get_code(b'242'))
# 
#     logger.info('Server on %s:%s', ip, port)
#     
#     # Connect to the server
#     logger.debug('creating socket')
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     logger.debug('connecting to server')
#     connectedFlag = True
#     try:
#         s.connect((ip, port))
#     except Exception: 
#         logger.debug('connection failed')
#         connectedFlag = False
#     frameBuilder.assembleFrame(codes.getValue('clientHello')[0],"")
#     s.send(frameBuilder.getFrame())
#     while connectedFlag:
# 
#         message = input("Enter your message to the EchoServer: ")
# #         print (codes.getValue('db_length')[0])
#         frameBuilder.assembleFrame(codes.getValue('clientHello')[0],message)
# #         my_bytes.append(245)
# #         my_bytes.append(len(message))
# #         my_bytes.extend(str.encode(message))
#         logger.debug('sending data: "%s"', message)
#         len_sent = s.send(frameBuilder.getFrame())
# #         len_sent = s.send('240')
# 
#         # Receive a response
#         logger.debug('waiting for response')
#         response = s.recv(len_sent + len(threading.currentThread().getName()) + 3)
#         logger.debug('response from server: "%s"', response)
# #         print('response from server: ', response.encode("utf-8"))
#         sleep(0.05)
# #         connectedFlag = False
# 
#     # Clean up
#     logger.debug('closing socket')
#     s.close()
#     logger.debug('Client done')

    
    
