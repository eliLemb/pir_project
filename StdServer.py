from PIRServerBasic import PIRServerBasic
from PIRServerBasic import ThreadedRequestHandler
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import logging
import threading
import socket
from OpCodes import OpCodes
import atexit
from time import sleep



codes = OpCodes()
# logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   

class T_StdRequestHandler(ThreadedRequestHandler):
    from threading import RLock
        
    lock = RLock()
    b_isServerConnected=False
    b_isClientConnected=False
    def __init__(self, request, client_address, server):
        return ThreadedRequestHandler.__init__(self, request, client_address, server,'T_StdRequestHandler')
#     
#     def setup(self):
#         socketserver.BaseRequestHandler.setup(self)
        
            
#         self.send_hello_2_manager(self) #After the server up and running, it notifies the manager about itself
        
    def handleMsg(self,recvOpcode,msg):
        code = OpCodes.getCode(self, recvOpcode)
            
        if code == 'server_hello':
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
        elif code == 'pir_query':
            self.logger.info (code)
            self.handleQuery(msg)
        elif code == 'std_query':
            self.logger.info (code)
            self.handleQuery(msg)
        elif code == 'pir_query_reply':
            self.logger.info (code)
        elif code == 'std_query_reply':
            self.logger.info (code)
        elif code == 'terminate':
            self.logger.info (code)
        elif code == 'ip_and_port_request':
            self.logger.info (code)
        elif code == 'ip_and_port_reply':
            self.logger.info (code)
        elif code == 'client_hello':
            self.logger.info (code)
            self.handleClientConnection(msg)
        else:
            self.logger.info("Bad opCode")

    
    def finish(self):
        if (self.b_isClientConnected == True):
            self.logger.debug('Client disconnected')
            appWindownManager.clientOffline()        
        return ThreadedRequestHandler.finish(self)
    
    
    def handleClientConnection(self,msg):
#         appWindownManager.clientOnline()
        
        super(T_StdRequestHandler,self).handleClientConnection(msg)
        appWindownManager.clientOnline()

class StdServer(PIRServerBasic):
    managerServerAddresPort = ('192.168.4.1',31100)
    WELCOME_PORT = 31101    
    
    def __init__(self, log_name, handler_class=T_StdRequestHandler):
        self.selfIPAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        self.tup_socket = (self.selfIPAddress, self.WELCOME_PORT) # let the kernel give us a port, tuple of the address and port
#         self.selfIPAddress = server_address[0]
#         self.selfPort = server_address[1]
        self.toKillKeepAliveThread = True
        self.log_name = log_name
        return PIRServerBasic.__init__(self, log_name, self.tup_socket, handler_class=handler_class)
    
    def server_activate(self):
        return PIRServerBasic.server_activate(self) 
    
    def activate(self):
#         logger = logging.getLogger(name)
#         logger.info("running at %s listens to port: %s ", ipAddress,port)
#         tup_socket = (ipAddress, port) # let the kernel give us a port, tuple of the address and port
        
#         server = StdServer(self.log_name,self.tup_socket, T_StdRequestHandler)
#         atexit.register(self.die,self)
        

#         PIRServerBasic.activate(self,name, ipAddress, port)
        super(StdServer,self).activate(self.log_name, self.tup_socket[0], self.tup_socket[1])
        self.e_KeepAliveStop = threading.Event() #Object event will be used to stop the keep alive thread
        
        t_stdServer = threading.Thread(target=self.serve_forever)
        t_KeepAlive = threading.Thread(target=self.KeepAliveSendHello, args=(self.e_KeepAliveStop,))
        
        t_stdServer.setDaemon(True)
        t_KeepAlive.setDaemon(True)
        
        t_stdServer.start()
        t_KeepAlive.start()
        appWindownManager.disableBtnStartServer()
        appWindownManager.enableBtnStopServer()
        
        
    def KeepAliveSendHello(self,stopEvent):
        attempts = 0
        s_openToManager = self.connection_2_Manager()
        while ( attempts<3) :
            if(self.e_KeepAliveStop.isSet()):
                break
            if s_openToManager != None:
                self.send_hello_2_manager(s_openToManager)
            else:
                self.logger.info('connection to Manager Server failed')
                self.logger.info('Attempt: %s ',attempts+1)
                attempts = attempts + 1
            stopEvent.wait(StdServer.HELLO_INTERVAL)
#                 self.server_close()
#                 break
    
    
    def connection_2_Manager(self):
        self.logger.debug('creating socket connection to Manager_Server')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(self.managerServerAddresPort)
            return s
#             connectedFlag = True
        except Exception: 
            self.logger.debug('connection failed') 
            
    def send_hello_2_manager(self,s_openToManager):
        self.logger.debug(self.selfIPAddress)
        self.frameBuilder.assembleFrame(codes.getValue('server_hello')[0], self.selfIPAddress + ":" + str(self.WELCOME_PORT))
        self.logger.debug('sending ''serverHello'' to Manager_Server')
        s_openToManager.send(bytes(self.frameBuilder.getFrame()))


    def shutdown(self):
        appWindownManager.disableBtnStopServer()
        appWindownManager.enableBtnStartServer()
        self.toKillKeepAliveThread = False
        self.e_KeepAliveStop.set()
        return PIRServerBasic.shutdown(self) 
      
    def die(self):
#         raise Exception("Oopsy")
        self.logger.debug('EXIT')
        s_openToManager = self.connection_2_Manager(self.managerServerAddresPort)
        self.frameBuilder.assembleFrame(codes.getValue('hello')[0], '0' + ":" + '0')
        self.logger.debug('sending ''servers_failed'' to Manager_Server')
        s_openToManager.send(bytes(self.frameBuilder.getFrame()))





class STD_window(Frame):
    o_standardServer=None
    def __init__(self, parent):
        self.myParent = parent 
        self.myParent.title('Standard Server')
        ### Our topmost frame is called myContainer1
        self.masterFrame = ttk.Frame(self.myParent,padding=(0,10,0,5)) ###
        self.masterFrame.grid(column=0, row=0, sticky=(N, S, E, W))
        self.l_serversConectedIcons=[]
        
        self.rowCounter = 1
        #------ constants for controlling layout ------
        button_width = 12      ### (1)
        button_height = 3
        
        button_padx = "2"    ### (2)
        button_pady = "1"    ### (2)

        buttons_frame_padx =  "3"   ### (3)
        buttons_frame_pady =  "2"   ### (3)        
        buttons_frame_ipadx = "3"   ### (3)
        buttons_frame_ipady = "1"   ### (3)
        # -------------- end constants ----------------

        
        self.style = ttk.Style(self.myParent)
        self.style.configure('TButton', font=("Arial", 12,'bold'))#larger Font for buttons
        self.style.configure('TCombobox', font=("Arial", 12,'bold'))#larger Font for buttons
        
        self.icn_startServer = PhotoImage(file="icons/TurnOn.png")
        self.icn_stopServer = PhotoImage(file="icons/TurnOff.png")
        self.icn_query = PhotoImage(file="icons/question2.png")
        self.icn_write = PhotoImage(file="icons/Document.png")
        self.icn_exit = PhotoImage(file="icons/exit.png")

        self.icn_serverConnected = PhotoImage(file="icons/Computer24.png")
        self.icn_userOnline = PhotoImage(file="icons/UserOnline.png")
        self.icn_userOffline = PhotoImage(file="icons/UserOffline.png")
        

        self.cb_listenPort = ttk.Combobox(self.masterFrame, textvariable=StdServer.WELCOME_PORT, style='TCombobox')
        self.cb_listenPort.bind('<<ComboboxSelected>>', self.updateWelcomePort)
        self.cb_listenPort['values'] = ('31101', '31102', '31103', '31104', '31105', '31106', '31107', '31108', '31109', '31110')
        self.cb_listenPort.set('31101')
        self.cb_listenPort.grid(row=0,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))
        
        
        self.btn_startServer = ttk.Button(self.masterFrame, compound=RIGHT, command=self.startUp, image=self.icn_startServer, style='TButton', text="Start Server ",width=button_width )
        self.btn_startServer.grid(row=1,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))    
        
        self.btn_stopServer = ttk.Button(self.masterFrame, compound=RIGHT, command=self.stopServer, image=self.icn_stopServer, style='TButton', text="Stop Server ",width=button_width )
        self.btn_stopServer.grid(row=2,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))
        
        self.btn_query = ttk.Button(self.masterFrame, compound=RIGHT, command=self.buttonClick, image=self.icn_query, style='TButton', text="Query ",width=button_width )
        self.btn_query.grid(row=3,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))    
        
        self.btn_write = ttk.Button(self.masterFrame, compound=RIGHT, command=self.buttonClick, image=self.icn_write, style='TButton', text="Write DB to File ",width=button_width )
        self.btn_write.grid(row=4,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))
        
        self.btn_exit = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickExit, image=self.icn_exit, style='TButton', text="Exit ",width=button_width )
        self.btn_exit.grid(row=5,column=1, columnspan=5, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))
        

        self.sp_bottom = ttk.Separator(self.masterFrame,orient=HORIZONTAL)
        self.sp_bottom.grid(row=6,column=0 ,columnspan=11, pady=5, sticky=(E, W))
 
        
        self.lbl_userSts = Label(self.masterFrame, image=self.icn_userOffline)
        self.lbl_userSts.grid(row=7, column=5, sticky=(E))
        self.disableBtnStopServer()
#         self.addConnectedServerIcon(1)
#         self.addConnectedServerIcon(2)
#         self.addConnectedServerIcon(3)
#         self.addConnectedServerIcon(4)

    def startUp(self):
#         ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        try:
            self.o_standardServer = StdServer('STD_Server', T_StdRequestHandler)
            self.o_standardServer.activate() 
        except:
#             self.o_standardServer.logger.debug('Something went wrong. Change port.')
            messagebox.showinfo("Server Error", "Server start-up failed.\nTry selecting different port.")
            
        
        
    def stopServer(self):
        self.o_standardServer.shutdown()
        self.o_standardServer.server_close()
    
    def enableBtnStopServer(self):
        self.btn_stopServer.state(["!disabled"])   # Disable the stop button.
        
    def disableBtnStopServer(self):
        self.btn_stopServer.state(["disabled"])   # Disable the stop button.
    
    def enableBtnStartServer(self):
        self.btn_startServer.state(["!disabled"])   # Disable the stop button.
        
    def disableBtnStartServer(self):
        self.btn_startServer.state(["disabled"])   # Disable the stop button.
    
    def clientOnline(self):
        self.lbl_userSts.config(image=self.icn_userOnline)
    
    def clientOffline(self):
        self.lbl_userSts.config(image=self.icn_userOffline)
    
    def updateWelcomePort(self,event):
        StdServer.WELCOME_PORT = int(self.cb_listenPort.get())
#         print(int(self.cb_listenPort.get()))
    
    def buttonClick(self):      
        pass
    
    def clickExit(self): 
        self.o_standardServer.shutdown()
        self.myParent.destroy()     











if __name__ == '__main__':
#     port = 31101
#     ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
#     StdServer.activate(StdServer, 'STD_Server', ipAddress, port)
    root = Tk()
    appWindownManager = STD_window(root)
    root.mainloop()
    