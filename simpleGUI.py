import math
import os
import sys
from tkinter import *
from tkinter import Button, Label, Entry, Tk, SE
import tkinter

from Crypto import Random
from Crypto.Cipher import AES
from sys import byteorder


methodFlag = False
servers = 0
seedLength = 128

def encrypt(message, key=None, key_size=128):
    def pad(s):
        x = AES.block_size - len(s) % AES.block_size
        return s + (bytes([x]) * x)
 
    padded_message = pad(message)
 
    if key is None:
        key = Random.new().read(key_size // 8)
 
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
 
    return (iv + cipher.encrypt(padded_message))
def decrypt(ciphertext, key):
    unpad = lambda s: s[:-s[-1]]
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext))[AES.block_size:]
 
    return plaintext
def createCWList():
    global CWList
    CWList = []  
    for i in range (0,servers-1):
        CWList.append(os.urandom((int)(math.sqrt(dataBaseSizeVar)/8)))
def findKthCW():
    kthCw = 0
    tempGFunctionResult = 0
    tempCWResult = 0
    kthCw.to_bytes((int)(math.sqrt(dataBaseSizeVar)/8),byteorder="big")
    tempGFunctionResult.to_bytes((int)(math.sqrt(dataBaseSizeVar)/8),byteorder="big")
    tempCWResult.to_bytes((int)(math.sqrt(dataBaseSizeVar)/8),byteorder="big")
    
    for gFunctionIndex in range (0,servers):
        tempGFunctionResult = tempGFunctionResult ^ listOfGFunction[gFunctionIndex]
    for cwIndex in range(0,servers):
        tempCWResult = tempCWResult ^ CWList[cwIndex]
    kthCw = tempGFunctionResult ^ tempCWResult ^ unitVectorJAsBytes
    print("found Kth CW",kthCw)
    CWList.append(kthCw)
    pass
def inflatorFunction(aSeedToInflate):
    global gFunction
    global listOfGFunction
    listOfGFunction = []
    gFunction = []
    for i in range (0,(int)(math.sqrt(dataBaseSizeVar)/seedLength)):
        gFunction.append(encrypt(str(i).encode('utf-8'),aSeedToInflate))
    listOfGFunction.append(b"".join(gFunction))
    print("G(s)" ,listOfGFunction )
def convertMatrix(aMatrixToConvert):
    global matrixA
    global matrixB
    matrixA = []
    matrixB = []
    
    for index in range (0,numRows):
        if (aMatrixToConvert[index].count(1)%2) == 0:
            matrixA.append(aMatrixToConvert[index])
        else:
            matrixB.append(aMatrixToConvert[index])
def buildMatrices():
    matrix = []
    
    global numRows
    numRows = 2**servers
    print("#servers = %d" %servers)
    for index in range (0,numRows):
        matrix.append([int(d) for d in bin(index)[2:].zfill(servers)])
    print(matrix)
    convertMatrix(matrix)  
def createRandomSeeds():
    global seedListAsBinary
    global seedListAsBytes
    seedListAsBytes = []
    seedListAsBinary = []
    amountOfSeeds = int((math.sqrt(dataBaseSizeVar)-1)*(2**(servers-1)-1)+2**(servers-1))
    for seedsAmountIndex in range (0,amountOfSeeds):
#         print(int.from_bytes(os.urandom(16),byteorder="big"))
        seedAsByte = os.urandom(16)
        seedListAsBytes.append(seedAsByte)
        seedListAsBinary.append([int(d) for d in bin(int.from_bytes(seedAsByte,byteorder="big"))[2:].zfill(128)])
#     print(seedListAsBinary)
#     print(amountOfSeeds)
def createTIndicators():
    global tIndicators
    tIndicators = []
    for tIndicatorIndex in range (0,servers):
        tIndicators.append(tIndicatorIndex)
def transformIndexBit():
    global transformedRowIndex
    global transformedColumnIndex
    transformedRowIndex    = bitToExtractIndex/(math.sqrt(dataBaseSizeVar))
    transformedColumnIndex = bitToExtractIndex%(math.sqrt(dataBaseSizeVar))
def runHandler():
    global servers
    global dataBaseSizeVar
    global bitToExtractIndex
    global listOfGFunction
    global CWlist
    global unitVectorJAsBytes
    try:
        servers = int(serverAmount.get())
        try:
            dataBaseSizeVar = int(dataBaseSize.get())
#             print("RUN %d " %servers)
            try:
                bitToExtractIndex = int(ChosenBit.get())
                if (bitToExtractIndex >= dataBaseSizeVar) | (bitToExtractIndex < 0):
                    print("choose bit in range of 0 - " ,dataBaseSizeVar-1)
                else:    
                    if methodFlag == False:
                        print("False from Run")
                    else:
                        print("True from Run")
                    buildMatrices()
                    createRandomSeeds()
                    createTIndicators()
                    transformIndexBit()
                    for index in range (0,servers):
                        inflatorFunction(seedListAsBytes[index])
                    createCWList()
                    unitVectorJ = []
                    for index in range(0,(int)(math.sqrt(dataBaseSizeVar))):
                        if index == transformedColumnIndex:
                            unitVectorJ.append("1")
                        else:
                            unitVectorJ.append("0")
                    unitVectorJAsBytes = (int(str.encode(''.join(unitVectorJ)),2)).to_bytes((int)(math.sqrt(dataBaseSizeVar)/8),byteorder="big")
                    findKthCW()
            except ValueError:
                print("Choose a Bit to extract from DB")    
        except ValueError:   
            print("Enter a DataBase Size to start simulation")
    except ValueError:
        print("Enter an Amount of Server to start simulation")
       
def quitHandler():
        print("GOODBYE")    
        sys.exit(0)

root = Tk();

def methodFlagChoice():
    global methodFlag
    
    if var.get() == 0:
        methodFlag = False
    else:
        methodFlag = True
        
    if methodFlag == False:
        print("False")
    else:
        print("True")
            
var = IntVar()

root.geometry("400x270")
    
root.title("PIR PROJECT")
    
serverAmount = StringVar()
dataBaseSize = StringVar()
ChosenBit    = StringVar()

Label(root,text = "Amount Of Servers:",fg = "blue",borderwidth=15).grid(row=0,column=0)
    
mServerAmount = Entry(root,textvariable = serverAmount)   
mServerAmount.grid(row=0,column=1,columnspan= 2)

Label(root,text = "Data Base Size:",fg = "blue",borderwidth=15).grid(row=1,sticky=S)

mDataBaseSize= Entry(root,textvariable = dataBaseSize)   
mDataBaseSize.grid(row=1,column=1,columnspan= 2)

Label(root,text = "Choose bit from DB:",fg = "blue",borderwidth=15).grid(row=2,sticky=S)

mDataBaseBit= Entry(root,textvariable = ChosenBit)   
mDataBaseBit.grid(row=2,column=1,columnspan= 2)

Label(root,text = "Method Flag:",fg = "blue",borderwidth=15).grid(row=3,sticky=S)
            
falseBtn = Radiobutton(root,text = "False",variable=var, value=0,command=methodFlagChoice)
falseBtn.grid(row = 3,column = 1)
trueBtn = Radiobutton(root,text = "True",variable=var, value=1,command=methodFlagChoice)
trueBtn.grid(row = 3,column = 2)
   
runButton = Button(root,text = "Run",borderwidth = 5,command = runHandler)
runButton.grid(row = 4, columnspan = 3,pady=15)
quitButton = Button(root,text = "Quit",borderwidth = 5,command = quitHandler)
quitButton.grid(row = 4,columnspan = 2,column= 1,padx = 15)

root.mainloop()
    
    
    
