from tkinter import *
from tkinter import ttk
class MyApp:
    def __init__(self, parent):
        
        self.myParent = parent 
        
        ### Our topmost frame is called myContainer1
        self.myContainer1 = Frame(parent) ###
        self.myContainer1.pack(fill=BOTH,expand=YES)

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
        self.buttons_frame = Frame(self.myContainer1) ###
        self.buttons_frame.pack(fill=X,anchor=S,side=BOTTOM)    
#         self.buttons_frame.columnconfigure(0,weight=2)
        # top frame
        self.top_frame = Frame(self.myContainer1) 
        self.top_frame.pack(side=TOP,anchor=N)  ###
        
        # bottom frame
#         self.bottom_frame = Frame(self.myContainer1) ###   
#         self.bottom_frame.grid()  ###
        self.style = ttk.Style(self.myParent)
        self.style.configure("BW.TLabel", foreground="#000000")# Black

        self.icn_startServer = PhotoImage(file="icons/TurnOn.png")
        self.icn_turnOffServer = PhotoImage(file="icons/TurnOff.png")
        self.icn_userOnline = PhotoImage(file="icons/UserOnline.png")
        self.icn_userOffline = PhotoImage(file="icons/UserOffline.png")

        ### Now we will put two more frames, left_frame and right_frame,
        ### inside top_frame.  We will use HORIZONTAL (left/right)
        ### orientation within top_frame.
        
        # left_frame        
        self.left_frame = Frame(self.top_frame) ###
        self.left_frame.pack(side=LEFT,anchor=W)  ###
        
        self.btn_startServer = ttk.Button(self.left_frame, compound=LEFT, command=self.button1Click, image=self.icn_startServer, text="Start Server",width=button_width )
        self.btn_startServer.pack(side=LEFT, anchor='ne', padx=button_padx, pady=button_pady)    

        ### right_frame 
        self.right_frame = Frame(self.top_frame)
        self.right_frame.pack(side=RIGHT,anchor=E)  ###

        self.sp_bottom = ttk.Separator(self.buttons_frame,orient=HORIZONTAL)
        self.sp_bottom.pack(fill=X)
        # now we add the buttons to the buttons_frame    
        self.button1 = Button(self.buttons_frame, command=self.button1Click,text="OK",width=button_width)
#         self.button1.configure(text="OK")
#         self.button1.focus_force()       
#         self.button1.config( 
#             width=button_width,  ### (1)
#                  ### (2)
#             )

        self.button1.pack(side=LEFT,)    
        self.button1.bind("<Return>", self.button1Click_a)  
        
        
        
        self.lbl_userSts = Label(self.buttons_frame, image=self.icn_userOffline)
        self.lbl_userSts.pack(side=RIGHT)

#         self.lbl_userSts.configure( image=self.icn_userOnline)
#         
        self.button2 = Button(self.right_frame,command=self.button2Click, text="Cancel",width=button_width)
#         self.button2.configure(text="Cancel", fg = "red",bg="red")  
#         self.button2.configure( 
#             width=button_width,  ### (1)
#             padx=button_padx,    ### (2) 
#             pady=button_pady     ### (2)
#             )
    
        self.button2.pack(side=RIGHT)
#         self.button2.bind("<Return>", self.button2Click_a)   
#         
    def button1Click(self):      
        if self.button1["background"] == "green":  
            self.button1["background"] = "yellow"
        else:
            self.button1["background"] = "green"
    
    def button2Click(self): 
        self.myParent.destroy()     
        
    def button1Click_a(self, event):  
        self.button1Click()
                
    def button2Click_a(self, event): 
        self.button2Click() 


root = Tk()
myapp = MyApp(root)
root.mainloop()