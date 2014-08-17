import logging
import socket
import threading
import queue
import random
import time
import pickle 

from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *
from PIL.ImageTk import PhotoImage

from FrameBuilder import FrameBuilder
from OpCodes import OpCodes
from PIRServerBasic import PIRServerBasic 
from PIRServerBasic import ThreadedRequestHandler
from threading import RLock
from bitstring import BitArray
from StdServer import StdServer
import socketserver
import os
import os.path
q_freeIndexs = queue.Queue()
# logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   
active_servers = {}
codes = OpCodes()
WELCOME_PORT = 31100    
#T stands for threaded
class T_ManagerRequestHandler(ThreadedRequestHandler):
    lock = RLock()
#     frameBuilder = FrameBuilder()
#     global appWindownManager
    b_isServerConnected=False
    b_isClientConnected=False
    serverInsertIndex=-1
    def __init__(self, request, client_address, server):
        return ThreadedRequestHandler.__init__(self, request, client_address, server,'T_ManagerRequestHandler')
        
    
#     def handle(self):
#         self.logger.debug('handle')
#         while True:
#         # Echo the back to the client
#             try:
#                 data = self.request.recv(2)
#                 if data == '' or len(data) == 0:
#                     break
#             except Exception: 
#                 self.logger.debug('recv len failed')
#                 if (self.b_isServerConnected == True):
#                     self.logger.debug('STD_Server disconnected')
#                     self.lock.acquire(True)
#                     appWindownManager.removeConnectedServerIcon()
#                     active_servers.pop(self.serverInsertIndex)
#                     q_freeIndexs.put_nowait(self.serverInsertIndex)
#                     self.logger.info('server %s was removed and it''s index will be recycled' ,self.serverInsertIndex)        
#                     self.lock.release()
#                 if (self.b_isClientConnected == True):
#                     self.logger.debug('Client disconnected')
#                     appWindownManager.clientOffline()
#                 break
#             #Got data Successfully
#             recvOpcode = data[0] #first byte is op code
#             size = data[1]
#             try:
#                 data = self.request.recv(size)
#                 if data == '' or len(data) == 0:
#                     break
#             except Exception: 
#                 self.logger.debug('recv data failed')
#                 break
#             self.handleMsg(recvOpcode,data)                
#         return    
    
    
    
    def finish(self):
        if (self.b_isServerConnected == True):
            self.logger.debug('STD_Server disconnected')
            self.lock.acquire(True)
            appWindownManager.removeConnectedServerIcon()
            active_servers.pop(self.serverInsertIndex)
            q_freeIndexs.put_nowait(self.serverInsertIndex)
            self.logger.info('server %s was removed and it''s index will be recycled' ,self.serverInsertIndex)        
            self.lock.release()
        if (self.b_isClientConnected == True):
            self.logger.debug('Client disconnected')
            appWindownManager.clientOffline()        
        return ThreadedRequestHandler.finish(self)
    
    ##Handle hello msg from STD_server and insert it's ip and port
    def handleHello(self,payload):
        self.b_isServerConnected = True
        modifiedPayload = payload
        serverCredential = modifiedPayload.split(':')
        insertIndex,reassigment = self.server.addServer2ActiveServers(serverCredential)
        self.serverInsertIndex = insertIndex
        s_stdServer = self.connect2Target((active_servers[insertIndex][0],active_servers[insertIndex][1]))
        appWindownManager.addConnectedServerIcon(insertIndex,reassigment)
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
   
    def handleClientConnection(self,msg):
#         self.server.addClient(self.client_address)
        
        super(T_ManagerRequestHandler,self).handleClientConnection(msg)
#         appWindownManager.writeToScrolledConsole(msg)
        appWindownManager.clientOnline()
#         self.b_isClientConnected=True
#         self.request.send(bytes(msg,"utf-8"))
#         try:
#             self.request.recv(1)
#         except Exception: 
#             self.logger.debug('Client disconnected')
#             appWindownManager.clientOffline()
        
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
        self.bitLength = self.server.getDBLength()
        self.logger.info('DB length in bits: %s.',self.bitLength)
        self.logger.debug('reply ''db_length'' to %s ',self.request.getsockname())
        self.frameBuilder.assembleFrame(codes.getValue('db_length')[0],str(self.bitLength))
    
    
    def handleIpAndPortRequest(self,msg):
        requestedIndex = int(msg)
        self.assambleIPPort(requestedIndex)
        self.request.send(self.frameBuilder.getFrame())
        
    def assambleIPPort(self,requestedIndex):
        tup_serverCredential=active_servers[requestedIndex]
        index = str(requestedIndex)
        ip = tup_serverCredential[0]
        port = str(tup_serverCredential[1]) 
        self.frameBuilder.assembleFrame(codes.getValue('ip_and_port_reply')[0],index+":"+ip+":"+port)
        
        
        
    

    def killThisServer(self):
        pass
#         self.finish()
#         self.server.server_close()
        
           
           
    ##Handling messages       
    def handleMsg(self,recvOpcode,msg):
        code = OpCodes.getCode(self, recvOpcode)
            
        if code == 'server_hello':
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
        elif code == 'ip_and_port_request':
            self.logger.info (code)
            self.handleIpAndPortRequest(msg)
        elif code == 'ip_and_port_reply':
            self.logger.info (code)
        elif code == 'terminate':
            self.logger.info (code)
            self.killThisServer()
        elif code == 'client_hello':
            self.logger.info (code)
            self.handleClientConnection(msg)
        else:
            self.logger.info("Bad opCode")

       
    def connect2Target(self,tu_address):
        self.logger.debug('creating socket connection to %s' , tu_address)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(tu_address)
            return s
#             connectedFlag = True
        except Exception: 
            self.logger.debug('connection to %s failed',tu_address)        
        
    
        
        
class ManagerServer(PIRServerBasic):
    
    
    def __init__(self, log_name, handler_class=T_ManagerRequestHandler):
        ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        self.tup_socket = (ipAddress, WELCOME_PORT) # let the kernel give us a port, tuple of the address and port
        self.log_name = log_name
        return PIRServerBasic.__init__(self, log_name, self.tup_socket, handler_class=handler_class)
    
    def activate(self):
#         logger = logging.getLogger(name)
#         logger.info("running at %s listens to port: %s ", ipAddress,port)
#         tup_socket = (ipAddress, port) # let the kernel give us a port, tuple of the address and port
#         server = ManagerServer(name, T_ManagerRequestHandler)
        super(ManagerServer,self).activate(self.log_name, self.tup_socket[0], self.tup_socket[1])
#         PIRServerBasic.activate(self,name, ipAddress, port, server)
        self.addServer2ActiveServers(self.tup_socket)
        t_managerServer = threading.Thread(target=self.serve_forever)
        t_cleanDeadServers = threading.Thread(target = self.check4DeadServer)
#         self.genarateDB()
        appWindownManager.disableBtnStartServer()
        appWindownManager.enableBtnStopServer()
        
        t_managerServer.setDaemon(True)
        t_cleanDeadServers.setDaemon(True)
        
        t_managerServer.start()
        t_cleanDeadServers.start()

    def addServer2ActiveServers(self,serverCredential):
        tup_serverCredential = serverCredential[0],int(serverCredential[1])
        self.lock.acquire(blocking=True)
        insertIndex,reassigment = self.checkServerRegistered(tup_serverCredential)
#         insertIndex = active_servers.__len__()
        tup_serverCredential = tup_serverCredential + (int(time.time()%1000000),)
        active_servers[insertIndex] = tup_serverCredential
        self.lock.release()
        self.logger.info('server was added at: %s' ,insertIndex)
        return (insertIndex,reassigment)        
    
    def checkServerRegistered(self,serverCredential):
        try:
            insertIndex =  [ k for k, element in active_servers.items() if (element[0],element[1]) == serverCredential]
            if not insertIndex:
                if q_freeIndexs.empty():
                    return (active_servers.__len__(),False)
                else:
                    return (q_freeIndexs.get(block=True, timeout=3),False)
            else:
                return (insertIndex[0],True)
        except Exception:
            return 
    
    
    def check4DeadServer(self):
        self.toCleanIndex=[]    ##this list will hold index's of dead servers and will be removed after iteration
                                ##Because dictionary can't change size during iteration
        while True:
            time.sleep(PIRServerBasic.HELLO_INTERVAL*0.5)
            curTime=int(time.time()%1000000)
            self.lock.acquire(blocking=True)
            for key, element in active_servers.items():
                if (curTime - element[2] > PIRServerBasic.TIME_TO_LIVE):
                    if(key!=0):
                        self.logger.info('no living signal from server at: %s %s' ,key,element)
                        self.toCleanIndex.append(key)
            for keys in self.toCleanIndex:
                active_servers.pop(keys)
                q_freeIndexs.put_nowait(keys)
#                 appWindownManager.removeConnectedServerIcon()
                self.logger.info('server %s was removed and it''s index will be recycled' ,keys)        
            self.lock.release()
            self.toCleanIndex.clear()        
    
    

        
    def shutdown(self):
        appWindownManager.disableBtnStopServer()
        appWindownManager.enableBtnStartServer()
        return PIRServerBasic.shutdown(self)
   
    def genarateDB(self):
         
        # open the file for writing our DB
        fileObject = open(self.file_savedDB,'wb') 
#         self.b_DB = BitArray(hex(random.getrandbits(self.dbLengthMB *self.c_MB)))
        self.b_DB = BitArray(hex(random.getrandbits(16384)))
        pickle.dump(self.b_DB.bin,fileObject)
        fileObject.close()
        
    

        
class SM_window(Frame):
    o_serverManager=None
    def __init__(self, parent):
        self.myParent = parent 
        self.myParent.title('PIR Manager Server')
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

        ### We will use VERTICAL (top/bottom) orientation inside myContainer1.
        ### Inside myContainer1, first we create buttons_frame.
        ### Then we create top_frame and bottom_frame.
        ### These will be our demonstration frames.         
#         self.label = Label(self.myContainer1, text="Welcome")
#         self.label.pack(side=TOP,anchor='n')
#         # buttons frame
#         self.buttons_frame = Frame(self.myContainer1) ###
#         self.buttons_frame.pack(fill=X,anchor=S,side=BOTTOM)    
#         self.buttons_frame.columnconfigure(0,weight=2)
        # top frame
#         self.top_frame = Frame(self.myContainer1) 
#         self.top_frame.pack(side=TOP,anchor=N)  ###
        
        # bottom frame
#         self.bottom_frame = Frame(self.myContainer1) ###   
#         self.bottom_frame.grid()  ###
        
        
        
        self.style = ttk.Style(self.myParent)
        self.style.configure('TButton', font=("Arial", 12,'bold'))#larger Font for buttons
        
#         self.obj_serverConnected = Image.open("icons/Computer24.png")
        
        self.icn_startServer = PhotoImage(file="icons/TurnOn.png")
        self.icn_stopServer = PhotoImage(file="icons/TurnOff.png")
        self.icn_query = PhotoImage(file="icons/question2.png")
        self.icn_write = PhotoImage(file="icons/Document.png")
        self.icn_exit = PhotoImage(file="icons/exit.png")

        self.icn_serverConnected = PhotoImage(file="icons/Computer24.png")
        self.icn_userOnline = PhotoImage(file="icons/UserOnline.png")
        self.icn_userOffline = PhotoImage(file="icons/UserOffline.png")
        
        
        ### Now we will put two more frames, left_frame and right_frame,
        ### inside top_frame.  We will use HORIZONTAL (left/right)
        ### orientation within top_frame.
        
        # left_frame        
#         self.left_frame = Frame(self.top_frame) ###
#         self.left_frame.pack(side=LEFT,anchor=W,fill=Y)  ###
        
        self.btn_startServer = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickStartUp, image=self.icn_startServer, style='TButton', text="Start Server ",width=button_width )
        self.btn_startServer.grid(row=0,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))    
        
        self.btn_stopServer = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickStopServer, image=self.icn_stopServer, style='TButton', text="Stop Server ",width=button_width )
        self.btn_stopServer.grid(row=1,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))
        
        self.btn_query = ttk.Button(self.masterFrame, compound=RIGHT, command=self.displayQueryClick, image=self.icn_query, style='TButton', text="Query ",width=button_width )
        self.btn_query.grid(row=2,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))    
        
        self.btn_write = ttk.Button(self.masterFrame, compound=RIGHT, command=self.writeDB2File, image=self.icn_write, style='TButton', text="Create new DB",width=button_width)
        self.btn_write.grid(row=3,column=1, ipadx=button_padx, columnspan=5, ipady=button_pady,padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))

        self.btn_exit = ttk.Button(self.masterFrame, compound=RIGHT, command=self.clickExit, image=self.icn_exit, style='TButton', text="Exit ",width=button_width )
        self.btn_exit.grid(row=4,column=1, columnspan=5, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(N))
        
        self.txt_scrolledConsole = ScrolledText(self.masterFrame, wrap=WORD, undo=True, setgrid=True)
        self.txt_scrolledConsole.grid(row=0,column=6, columnspan=1, rowspan=5, ipadx=button_padx, ipady=button_pady, padx=buttons_frame_padx, pady=buttons_frame_ipady, sticky=(W))
        
        self.cnvs_connectedServersIcons = Canvas(self.masterFrame,width=160, height=32)
        self.cnvs_connectedServersIcons.grid(row=6, column=self.l_serversConectedIcons.__len__()+1)
        
        ### right_frame z
#         self.right_frame = Frame(self.top_frame)
#         self.right_frame.pack(side=RIGHT,anchor=E)  ###

        self.sp_bottom = ttk.Separator(self.masterFrame,orient=HORIZONTAL)
        self.sp_bottom.grid(row=5,column=0 ,columnspan=11, pady=5, sticky=(E, W))
        # now we add the buttons to the buttons_frame    
#         self.button1 = Button(self.masterFrame, command=self.button1Click,text="OK",width=button_width)
#         self.button1.configure(text="OK")
#         self.button1.focus_force()       
#         self.button1.config( 
#             width=button_width,  ### (1)
#                  ### (2)
#             )

#         self.button1.pack(side=LEFT,)    
#         self.button1.bind("<Return>", self.button1Click_a)  
        
        
        self.lbl_userSts = Label(self.masterFrame, image=self.icn_userOffline)
        self.lbl_userSts.grid(row=6, column=6, sticky=(E))
        self.disableBtnStopServer()
#         self.addConnectedServerIcon(1)
#         self.addConnectedServerIcon(2)
#         self.addConnectedServerIcon(3)
#         self.addConnectedServerIcon(4)
        

    def clickStartUp(self):
#         ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
        self.o_serverManager = ManagerServer('Manager_Server', T_ManagerRequestHandler) 
        self.o_serverManager.activate()
        
    def clickStopServer(self):
        self.o_serverManager.shutdown()
        self.o_serverManager.server_close()
        
        
    
    def addConnectedServerIcon(self,position,reassigment):
        if reassigment==False:
            
            iconID = self.cnvs_connectedServersIcons.create_image(32*self.l_serversConectedIcons.__len__()+5,5, image=self.icn_serverConnected,anchor = NW)
#             lbl_serverConnected = Label(self.masterFrame, image=self.icn_serverConnected)
#             lbl_serverConnected.grid(row=6, column=self.l_serversConectedIcons.__len__()+1)
#             self.o_serverManager.logger.debug('Grid position: %s',self.l_serversConectedIcons.__len__())
            
#         self.rowCounter = self.rowCounter+1
            self.l_serversConectedIcons.append(iconID)
#             sleep(10)
#             lbl_serverConnected.destroy()
    
    def removeConnectedServerIcon(self):
        try:
            self.cnvs_connectedServersIcons.delete(self.l_serversConectedIcons.pop())
        except:
            self.logger.debug('Label remove failed')
    
    def enableBtnStopServer(self):
        self.btn_stopServer.state(["!disabled"])   # Enable the stop button.
        
    def disableBtnStopServer(self):
        self.btn_stopServer.state(["disabled"])   # Disable the stop button.
    
    def enableBtnStartServer(self):
        self.btn_startServer.state(["!disabled"])   # Enable the stop button.
        
    def disableBtnStartServer(self):
        self.btn_startServer.state(["disabled"])   # Disable the stop button.
    
    def clientOnline(self):
        self.lbl_userSts.config(image=self.icn_userOnline)
    
    def clientOffline(self):
        self.lbl_userSts.config(image=self.icn_userOffline)
    
    def displayQueryClick(self):   
        self.txt_scrolledConsole.insert(INSERT,str(len(self.o_serverManager.lastReceivedQuery)) + "\t")   
        self.txt_scrolledConsole.insert(INSERT,self.o_serverManager.lastReceivedQuery + "\n")
    def clickExit(self): 
        try:
            self.o_serverManager.shutdown()
            self.o_serverManager.server_close()
        finally:
            
            self.myParent.destroy()     

    def writeDB2File(self):
        self.o_serverManager.genarateDB()
        
    def writeToScrolledConsole(self,msg):
        pass
#         self.txt_scrolledConsole.insert( str(msg))

#         Frame.__init__(self, parent)   
#         self.parent = parent
#         self.initUI()
#         
#     def initUI(self):
# #     self.parent.title("Windows")
#         self.style = Style()
#         self.style.theme_use()
#         self.pack(fill=BOTH, expand=1)
# 
#         
#         self.columnconfigure(1, weight=1)
#         self.columnconfigure(1, pad=7)
#         self.rowconfigure(1, weight=0)
#         self.rowconfigure(1, pad=5)
#         self.rowconfigure(2, weight=0)
#         self.rowconfigure(2, pad=5)
#         self.rowconfigure(3, weight=3)
#         self.rowconfigure(3, pad=5)
#         self.rowconfigure(4, weight=0)
#         self.rowconfigure(4, pad=5)
# #         self.rowconfigure(5, weight=9)
# #         self.rowconfigure(5, pad=5)
#         lbl = Label(self, text="Manager Server")
#         lbl.grid(row=0,sticky=W, pady=4, padx=5)
#         photoimage = PhotoImage(file="online-red-icon.gif")
#         print(photoimage.__str__())
#         
#         
# #         area = Text(self)
# #         area.grid(row=1, column=2, columnspan=2, rowspan=4,padx=5, sticky=E+W+S+N)
#         area = ScrolledText(self)
#         area.grid(row=1, column=1, columnspan=2, rowspan=3,padx=10, sticky=NSEW)
# #         
#         btn_start = Button(self, text="Start Server")
#         btn_start.grid(row=1, column=0,sticky=N)
#         
#         btn_stop = Button(self, text="Stop Server")
#         btn_stop.grid(row=2, column=0,sticky=N)
#         
#         btn_showQuery = Button(self, text="Show Query")
#         btn_showQuery.grid(row=3, column=0,sticky=N)
#         
#         line = Separator(self,orient=HORIZONTAL)
#         line.grid(row=4,columnspan=5 ,sticky=EW )
#         
#         hbtn = Button(self, text="Help" ,compound=TOP,image =photoimage)
#         hbtn.grid(row=5, column=0, padx=5)
#         
#         
#         
#         canvas = Canvas()
# #         canvas.grid(row =5, column = 0)
#         canvas.create_image(0,0, image=photoimage)        
#         
# #         PhotoImage(file="icons/histogram.gif")
#         
#         obtn = Button(self, text="OK",image = photoimage)
#         obtn.grid(row=5, column=2)
#         photoimage
#         img = ImageTk.PhotoImage(Image.open("True1.gif"))
#         panel = Label(root, image = img)
#         panel.pack(side = "bottom", fill = "both", expand = "yes")
        
        
        
        
#         self.columnconfigure(1, weight=1)
#         self.columnconfigure(4, pad=3)
#         self.rowconfigure(3, weight=1)
#         self.rowconfigure(5, pad=7)
#         
#         lbl = Label(self, text="Windows")
#         lbl.grid(sticky=E, pady=4, padx=5)
#         stext = ScrolledText(bg='white', height=10)
# #  
#         stext.insert(END, __doc__)
#         stext.pack(fill=BOTH, side=LEFT, expand=True)
#         stext.focus_set()
#         stext = ScrolledText(self)
#         stext.grid(row=1, column=1, rowspan=2,sticky=EW)

#         stext.grid()
        
#         abtn = Button(self, text="Activate")
#         abtn.grid(row=1, column=1)
#         
#         cbtn = Button(self, text="Close")
#         cbtn.grid(row=2, column=3, pady=4)
        

         
#         hbtn = Button(self, text="Help")
#         hbtn.grid(row=6, column=0, padx=5)
#  
#         obtn = Button(self, text="OK")
#         obtn.grid(row=6, column=2)     
#         quitButton = Button(self, text="Quit")
#         quitButton.place(x=50, y=50)





from time import sleep


if __name__ == '__main__':
    #     import threading
#     root = Tk()
#     root.geometry("700x500+300+100")
#     app = SM_window(root)
#     root.mainloop()  
    root = Tk()
    appWindownManager = SM_window(root)
    root.mainloop()
    
#     o_serverManager = ManagerServer('Manager_Server', T_ManagerRequestHandler) 
# 
#     t_managerServer = threading.Thread(target=o_serverManager.serve_forever)
#     t_managerServer.setDaemon(True)
#     t_managerServer.start()
# 
#     sleep(10)
#     o_serverManager.shutdown()
#     o_serverManager = ManagerServer('Manager_Server', T_ManagerRequestHandler) 
# 
#     t_managerServer = threading.Thread(target=o_serverManager.serve_forever)
#     t_managerServer.setDaemon(True)
#     t_managerServer.start()
#     sleep(10)
#     o_serverManager.shutdown()
    
    
    
    
    
    
    
