import logging
import socket
import threading
import queue
import random
import time

# from PIL import Image


from FrameBuilder import FrameBuilder
from OpCodes import OpCodes
from PIRServerBasic import PIRServerBasic 
from PIRServerBasic import ThreadedRequestHandler
from threading import RLock
from bitstring import BitArray
from StdServer import StdServer

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
        s_stdServer = self.connection_2_target((active_servers[insertIndex][0],active_servers[insertIndex][1]))
    
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
        t_server = threading.Thread(target=server.serve_forever)
        t_server.start()
        t_cleanDeadServers = threading.Thread(target = server.check4DeadServer)
        t_cleanDeadServers.start()
        self.genarateDB(self)


    def addServer2ActiveServers(self,serverCredential):
        tup_serverCredential = serverCredential[0],int(serverCredential[1])
        self.lock.acquire(blocking=True)
        insertIndex = self.checkServerRegistered(tup_serverCredential)
#         insertIndex = active_servers.__len__()
        tup_serverCredential = tup_serverCredential+ (int(time.time()%1000000),)
        active_servers[insertIndex] = tup_serverCredential
        self.lock.release()
        self.logger.info('server was added at: %s' ,insertIndex)
        return insertIndex        
    
    def checkServerRegistered(self,serverCredential):
        try:
            insertIndex =  [ k for k, element in active_servers.items() if (element[0],element[1]) == serverCredential]
            if not insertIndex:
                if q_freeIndexs.empty():
                    return active_servers.__len__()
                else:
                    return q_freeIndexs.get(block=True, timeout=3)
            else:
                return insertIndex[0]
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
                self.logger.info('server %s was removed and its index will be recycled' ,keys)        
            self.lock.release()
            self.toCleanIndex.clear()        
    
    
    def genarateDB(self):
        self.b_DB = BitArray(hex(random.getrandbits(self.dbLengthMB *self.c_MB)))
        
        

# class SM_window(Frame):
# 
#     def __init__(self, parent):
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







if __name__ == '__main__':
    #     import threading
#     root = Tk()
#     root.geometry("700x500+300+100")
#     app = SM_window(root)
#     root.mainloop()  
 
    port = 31100    
    ipAddress = [(s.connect(('192.168.4.138', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
    ManagerServer.activate(ManagerServer, 'Manager_Server', ipAddress, port)
#      
    
    
    
    
    
    
    
    
    
    
    
    
