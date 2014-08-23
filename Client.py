from tkinter import *
from tkinter import ttk
from threading import RLock
from queue import Queue
from threading import Thread
from PIL import ImageTk
import numpy as np
import matplotlib.pyplot as plt
import os
import math
from PIRQueryObject import PIRQueryObject

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
from Crypto import Random
from Crypto.Cipher import AES
from sys import byteorder
import random
from itertools import count
from tkinter import messagebox
import pickle 

codes = OpCodes()
S_M_PORT = 31100
active_servers = {}
serversPool = Queue()
serversQueryReply = list()
SEED_LENGTH = 128
class client_window(Frame):
    
    
    pirClient = None
    
    def __init__(self, parent):
        logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)
        self.logger = logging.getLogger("Client Window")
        
        
        
        #################### Global variables ####################
        
        self.DB_LENGTH = 500
        self.queryMethod=IntVar()
        self.desirableBit=0
        self.myParent = parent 
        
        self.myParent.title('PIR Client')
        self.masterFrame = ttk.Frame(self.myParent,padding=(0,10,0,5)) ###
        self.masterFrame.grid(column=0, row=0, sticky=(N, S, E, W))
        
        self.pirClient = PIRClient(self)
        
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
        
        self.icn_SM_disconnected = ImageTk.PhotoImage(file="icons/Red-icon32.png")
        self.icn_SM_connected = ImageTk.PhotoImage(file="icons/Green-icon32.png")
        self.icn_compare = ImageTk.PhotoImage(file="icons/compare24.png")
        self.icn_query = ImageTk.PhotoImage(file="icons/download24.png")
        self.icn_exit = ImageTk.PhotoImage(file="icons/exit24.png")

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
        
        self.chk_pir = ttk.Radiobutton(self.masterFrame, text='PIR', variable=self.queryMethod, value=1)
        self.chk_pir.grid(row=3,column=0,columnspan=2, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W, S))
        self.chk_pir.state(['selected'])
        self.queryMethod.set(1)
        
        self.chk_regular = ttk.Radiobutton(self.masterFrame, text='Standard', variable=self.queryMethod, value=2)
        self.chk_regular.grid(row=4,column=0,columnspan=2, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W, S))
        
        
        self.lbl_numOfServersDsc = ttk.Label(self.masterFrame, compound=LEFT, text="Amount of\nActive servers:" )
        self.lbl_numOfServersDsc.grid(row=3,column=1, columnspan=7, rowspan=2, sticky=(W))
#         self.lbl_numOfServersDsc.config(text = "bllablabalbalbla")

        self.lbl_numOfServers = ttk.Label(self.masterFrame, compound=LEFT, style='TLabel', text="0" )
        self.lbl_numOfServers.grid(row=3,column=7, rowspan=2, sticky=(E))
#         
        self.scl_bitChoice = ttk.Scale(self.masterFrame, orient=HORIZONTAL, from_=0.0, to=self.DB_LENGTH,command=self.updatDesiedBit)
        self.scl_bitChoice.grid(row=5, column=0, columnspan=8, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady,sticky=(W,E))
        self.scl_bitChoice.state(["disabled"])   # Disable the scale bar.
        
        self.lbl_bitIndex = ttk.Label(self.masterFrame, compound=CENTER,  style='TLabel' , text = '0')
        self.lbl_bitIndex.grid(row=6,column=1, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W,E))
        
        
        self.btn_query = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickQuery, style='TButton', text="Get value ",image=self.icn_query, width=button_width )
        self.btn_query.grid(row=7,column=0, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))
         
        self.lbl_result = ttk.Label(self.masterFrame, compound=CENTER, style='TLabel', text='XX',justify=LEFT)
        self.lbl_result.grid(row=7,column=7, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(E))
        
       
        self.btn_compare = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickCompare, style='TButton', text="Compare ", image=self.icn_compare, width=button_width )
        self.btn_compare.grid(row=8,column=0, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))
        
        self.btn_exit = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickExit, style='TButton', text="Exit ", image=self.icn_exit, width=button_width )
        self.btn_exit.grid(row=8,column=7, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(E))
       
    def updatDesiedBit(self,value):    
        self.lbl_bitIndex.configure(text= str(int(float(value))))
    
    def clickConnect(self): 
        self.pirClient.initateConnection(self.txt_SMAddress.get())
        
    
    def setNumOfActiveServersLbl(self,aNumOfActiveServers):
        currentSrtring = self.lbl_numOfServersDsc.cget('text')
        currentSrtring = currentSrtring[:-1]
        currentSrtring = currentSrtring + str(aNumOfActiveServers)
        self.lbl_numOfServersDsc.configure(text = aNumOfActiveServers)
        
#     def getNumOfServersFromLbl(self):
#         self.lbl_numOfServersDsc.cget('text')
#      
    def setNumOfServers(self,aNumOfActiveServers):
        self.lbl_numOfServers.config(text = str(aNumOfActiveServers))
         
    def disableConnectBtn(self):
        self.btn_connect.state(["disabled"])
    
    def enableConnectBtn(self):
        self.btn_connect.state(["!disabled"])
        
    def ServerConnected_icon(self):
        self.lbl_connectionSts.config(image=self.icn_SM_connected)
    def ServerDisconnected_icon(self):
        self.lbl_connectionSts.config(image=self.icn_SM_disconnected)
        
    def enableScale(self):
        self.scl_bitChoice.state(["!disabled"])   # Enable the scale bar.
    
    def getCurrentScaleNum(self):
        return (int)(self.scl_bitChoice.get())
    
    def clickExit(self):
        self.myParent.destroy()
    
    def configureDBScale(self,valueToUpdate):
        self.scl_bitChoice.configure(to=valueToUpdate)    
    
    def clickQuery(self):
        if self.queryMethod.get()==1:
            self.logger.info("PIR radio selected")
            self.pirClient.executeQuery()

        elif self.queryMethod.get()==2:
            self.logger.info("Regular radio selected")
            self.generateRegQuery()
            
    def writeResultToLabel(self,aResultToWrite):
        self.lbl_result.configure(text=aResultToWrite,justify=LEFT)  
    
    def showWarningPopUp(self,aTitle,aMsg):
        messagebox.showinfo(aTitle,aMsg)
        
    def generateRegQuery(self):
        self.pirClient.executeQuery()
    
            
    def clickCompare(self):
        N = 2
#         queryResult = bin(int(self.lbl_result.cget("text")))
        results = (self.pirClient.currentQueryLength,self.pirClient.DB_LENGTH)
#         queryResult = 2
#         results = 10
        ind = np.arange(N)    # the x locations for the groups
        width = 0.1       # the width of the bars: can also be len(x) sequence

        plt.bar(ind, results, width, color='r')
        plt.bar(ind, results, width, color='g')
        
        plt.ylabel('Bits')
        plt.title('PIR vs. non PIR data transfer')
        plt.xticks(ind+width/2., ('PIR','regular') )

        plt.show()
        
        
        
 
    
    
    
    
    
class PIRClient():
    
    clientWindowManager = None
    lock = RLock()
    frameBuilder = FrameBuilder()
    pirQuery = None
    def __init__(self,aWindowManager):        
        logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)
        self.logger = logging.getLogger("Client")
        self.clientWindowManager = aWindowManager
        
    def initateConnection(self,aSMAddress):
#         self.clientWindowManager.showWarningPopUp("connection failed","asdsfd")

        self.t_SMConnection = threading.Thread(target = self.connect2SM,  args=(aSMAddress,))
        self.t_SMConnection.setDaemon(True)
        self.t_SMConnection.start()
    
    
    
    def connect2SM(self,aSMAddress):
        self.logger.debug('creating socket')
        soc_serverManager = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to server')
        
        try:

            soc_serverManager.connect((aSMAddress, S_M_PORT))
            self.saveServerDetails((aSMAddress,S_M_PORT,soc_serverManager)) ##tuple format: (IP, PORT, Active Socket)

            self.sayHelloToSM()
            self.getDBLength()
            self.getSTDservers()
            
            self.clientWindowManager.enableScale() 
            self.clientWindowManager.disableConnectBtn()
        except OSError: 
            self.logger.debug('connection failed')
        

        ##TODO move this.
#         soc_serverManager.send(self.frameBuilder.getFrame()) ##
#         self.readSocketForResponse(soc_serverManager)
    def calacLengthSent(self,queryToSend):
        self.currentQueryLength = self.pirQuery.calacQuerySize()
        
        
    def pushServersAndQueriesToSendIntoQueue(self,queriesToSend):
        serversPool.queue.clear()
        serversQueryReply.clear()
#         while serversPool.qsize() != 0:
#                 serversPool.get_nowait()
        self.verifyServersAlive()
        for serverIndex in range(0,active_servers.__len__()):
            queryAsString = pickle.dumps(queriesToSend[serverIndex])
#             self.logger.info("Pickle query: %s  type: %s",queryAsString,type(queryAsString))
            serversPool.put((active_servers[serverIndex][2],queryAsString))
            
    

    def executeQuery(self):
        
        
        self.pirQuery = PIRQueryObject(self.currentServersQuantity,self.DB_LENGTH)
        self.logger.info("Requested bit: %d", self.clientWindowManager.getCurrentScaleNum())
        queryToSend = self.pirQuery.getPIRQuery(self.clientWindowManager.getCurrentScaleNum())
        self.calacLengthSent(queryToSend)
#         self.logger.info("query to send 0: %s",queryToSend[0])
#         self.logger.info("query to send 1: %s",queryToSend[1])

        self.pushServersAndQueriesToSendIntoQueue(queryToSend)
        for _ in queryToSend:
#             serverTuple = active_servers[targetServer]
#             avtiveTargetSocket = serverTuple[2]
            worker = Thread(target=self.sendQueries)
#             self.logger.info("Worker %s: created, connected to %s:%s",worker.getName(),serverTuple[0],serverTuple[1])
            worker.setDaemon(True)
            worker.start()
#             worker.join()
        serversPool.join()
#         self.logger.info("All threads returned")
        if(serversQueryReply.__len__() == active_servers.__len__()):
            self.logger.info("All servers replied to the query")
            
            desiredBit = self.pirQuery.calculateQueryResult(serversQueryReply)
            self.logger.info("List of responses: %s",serversQueryReply)

            self.clientWindowManager.writeResultToLabel(desiredBit)
    
          
    
    def verifyServersAlive(self):
        serversToRemovePool = []
        for (serverKey,(_,_,currentServer)) in active_servers.items():
            self.logger.info("Check server: %s alive",serverKey)
            try:
                self.sayHelloToServer(currentServer)
            except Exception:
                self.logger.info("server: %s is not present, removed",serverKey)
                serversToRemovePool.append(serverKey)
        for server2Remove in serversToRemovePool:
            del active_servers[server2Remove]
        
    def readSocketForResponse(self,runnigSocket):
        cur_thread = threading.currentThread()

        while True:
        # Echo the back to the client
            try:
                data = runnigSocket.recv(2)
                if data == '' or len(data) == 0:
                    break
            except Exception: 
                self.logger.debug('recv failed opcode and num bytes of Length')
                break
            #Got data Successfully
            self.recvOpcode = data[0] #first byte is op code
            lengthOfSize = data[1]
            try:
                data = runnigSocket.recv(lengthOfSize)
                if data == '' or len(data) == 0:
                    break
            except Exception: 
                self.logger.debug('recv data failed size')
                break
            size = int.from_bytes (data,byteorder='big')
            try:
                data = runnigSocket.recv(size)
                if data == '' or len(data) == 0:
                    break
            except Exception: 
                self.logger.debug('recv data failed payload')
                break
            self.payload = data
            self.logger.info("%s Received: %s %s",cur_thread.getName(),self.recvOpcode,self.payload )
            self.reponseHandler(self.recvOpcode,self.payload)
            break
             
    def reponseHandler(self,recvOpcode,msg):
        self.code = OpCodes.getCode(self, self.recvOpcode)
        
        if self.code == 'hello_ack':
            self.logger.info (self.code)
            self.clientWindowManager.ServerConnected_icon()
        elif self.code == 'server_quantity_reply':
            self.logger.info (self.code)
            self.handleQuantityReply(msg)
        elif self.code == 'servers_up':
            self.logger.info (self.code)
        elif self.code == 'servers_failed':
            self.logger.info (self.code)
        elif self.code == 'db_length':
            self.logger.info (self.code)
            self.handleDBLengthReply(msg)
        elif self.code == 'pir_query_reply':
            self.logger.info (self.code)
            self.handleQueryReply(msg)    
        elif self.code == 'std_query_reply':
            self.logger.info (self.code)
            self.handleQueryReply(msg)
        elif self.code == 'ip_and_port_reply':
            self.logger.info (self.code)
            self.handleIpAndPortReply(msg)
        else:
            self.logger.info("Bad opCode")        
    
            
    def sayHelloToSM(self):
        self.frameBuilder.assembleFrame(codes.getValue('client_hello')[0],"client says hello")
        self.sendAndHandleResponse(active_servers[0][2])        
    
    def sayHelloToServer(self,activeTargetSocket):
        self.frameBuilder.assembleFrame(codes.getValue('client_hello')[0],"client says hello")
        self.sendAndHandleResponse(activeTargetSocket)  
    
    def getSTDservers(self):
        self.frameBuilder.assembleFrame(codes.getValue('server_quantity_request')[0],"server currentServersQuantity request")
        self.sendAndHandleResponse(active_servers[0][2])
    
    def getDBLength(self):
        self.frameBuilder.assembleFrame(codes.getValue('db_length_request')[0],"DB length request")
        self.sendAndHandleResponse(active_servers[0][2])

    def sendQueries(self):
        t_frameBuilder = FrameBuilder()
        while True:
#             self.logger.info('%s Fetching socket from to queue ',threading.currentThread().getName())
            (targetSocket,query2Send) = serversPool.get(True)
            self.logger.info("length of query to send %d",len(query2Send))
            t_frameBuilder.assembleFrame(codes.getValue('pir_query')[0],query2Send)
            targetSocket.send(t_frameBuilder.getFrame())
            self.readSocketForResponse(targetSocket)
#             self.sendAndHandleResponse(targetSocket)
            serversPool.task_done()
    
    def sendAndHandleResponse(self,activeSocket):
        activeSocket.send(self.frameBuilder.getFrame())
#         activeSocket.send(pickle.dump(self.frameBuilder.getFramePickle()),flags=0)
        self.readSocketForResponse(activeSocket)
        
    
    
###############################################################################
##    Handling functions in this section                                     ##
###############################################################################        
    def handleQuantityReply(self,msg):
        self.currentServersQuantity = int(msg)
        self.clientWindowManager.setNumOfServers(self.currentServersQuantity)
        soc_serverManager = active_servers[0][2]
        for currentServer in range(1, self.currentServersQuantity):
            self.frameBuilder.assembleFrame(codes.getValue('ip_and_port_request')[0],str(currentServer))
            soc_serverManager.send(self.frameBuilder.getFrame())
            self.readSocketForResponse(soc_serverManager)
        self.currentServersQuantity = active_servers.__len__()
         
    def saveServerDetails(self,serverCredential):
        self.lock.acquire(blocking=True)
        active_servers[active_servers.__len__()] = serverCredential
        self.lock.release()
           
    def handleIpAndPortReply(self,msg):
        modifiedMsg = msg.decode('utf-8')
        try:
            index,stdIP,stdPort = modifiedMsg.split(':',3)
        except Exception: 
                self.logger.debug('Bad ipAndPortRequest format')
        
        soc_stdServer=self.connect2Target((stdIP,int(stdPort)))
        self.sayHelloToServer(soc_stdServer) 
        self.lock.acquire(blocking=True)
        active_servers[int(index)] = (stdIP,int(stdPort),soc_stdServer)
        self.lock.release()
        self.logger.debug('STD Server:%s on Port:%s was added in index:%s ', stdIP,stdPort,str(index))
    
    def handleQueryReply(self,msg):
        serversQueryReply.append(int(msg))
    
    def handleDBLengthReply(self,msg):
        modifiedMsg = msg.decode('utf-8')
        self.DB_LENGTH = int(modifiedMsg)
        self.clientWindowManager.configureDBScale(self.DB_LENGTH-1)
        self.logger.info('Data base size is updated to:%s',self.DB_LENGTH )

    def connect2Target(self,tu_address):
        self.logger.debug('creating socket connection to %s' , tu_address)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(tu_address)
            return s
        except Exception: 
            self.logger.debug('connection to %s failed',tu_address)
            
            
    def setSMIPAdress(self,aIPAdress):
        pass
              
if __name__ == "__main__":
    root = Tk()
    appWindownManager = client_window(root)
    root.mainloop()

