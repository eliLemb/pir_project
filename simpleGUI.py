import math
import os
import sys
from tkinter import *
from tkinter import Button, Label, Entry, Tk, SE
import tkinter

from bitstring import BitArray
from Crypto import Random
from Crypto.Cipher import AES
from sys import byteorder
import random
from itertools import count

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
 
    cipher = AES.new(key)
    return (cipher.encrypt(padded_message))
def decrypt(ciphertext, key):
    unpad = lambda s: s[:-s[-1]]
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext))[AES.block_size:]
 
    return plaintext
def createCWListPool():
    global CWListPool
    global amountOfCwToCreate
    CWListPool = []  
    amountOfCwToCreate = 2**(servers-1)-1
    
    for _ in range (0,amountOfCwToCreate):
        tempCw = BitArray(os.urandom((int)(math.sqrt(dataBaseSizeVar)/8)))
        CWListPool.append(tempCw)
#     print("size of CWlist:",CWListPool.__len__())    
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
#     print("matrix A",matrixA)
#     print("matrix B",matrixB)
    t=0  
    for i in  matrixA:  
        t+=i[0]   
#     print("seed per section:",t)    
def buildMatrices():
    matrix = []
    
    global numRows
    numRows = 2**servers
#     print("#servers = %d" %servers)
    for index in range (0,numRows):
        matrix.append([int(d) for d in bin(index)[2:].zfill(servers)])
    #   print(matrix)
    convertMatrix(matrix)
def createGFunctions(aSeedList):
    listOfGFunction = []
    
    for seed in aSeedList:   
        listOfGFunction.append(inflatorFunction(seed)) 
         
    return listOfGFunction  
def inflatorFunction(aSeedToInflate):
    gFunction = BitArray(encrypt(str(0).encode('utf-8'),aSeedToInflate))
    for i in range (1,(int)(math.sqrt(dataBaseSizeVar)/seedLength)):
        gFunction.append(encrypt(str(i).encode('utf-8'),aSeedToInflate))
    return BitArray(gFunction)
def createRandomSeeds():
    global amountOfSeeds
    seedListAsBytes = []
    amountOfSeeds = int((math.sqrt(dataBaseSizeVar)-1)*(2**(servers-1)-1)+2**(servers-1))
#     print("amount of seeds:",amountOfSeeds)
    for _ in range (0,amountOfSeeds):
        seedAsByte = BitArray(os.urandom(16))
        seedListAsBytes.append(seedAsByte.hex)
    return seedListAsBytes 
def createForcedTIndicator(aTempIndicatorList,aAmountOfCwToCreate):
    answer = 0
    for indicator in aTempIndicatorList:
        answer = answer ^ indicator
    return answer

def createTIndicatorsPool():
    tIndicatorsPool = list(range(0,2**(servers-1)))
#     print("created tInd:",tIndicatorsPool)
    return tIndicatorsPool 
# def createTIndicatorsPool():
#     tIndicatorsPool = []
#     tempIndicatorList = []
#     amountToCreate = amountOfSeeds #create indicators amount as seeds amount for important section with 1 indicator forced in important section
#     amountOfSeedsPerUnimportantSection = 2**(servers-1)-1
#     
#     newAmountToCreate = amountToCreate-amountOfSeedsPerUnimportantSection#include 3 seeds form important section
#     for tIndicatorIndex in range (0,newAmountToCreate):
#         if tIndicatorIndex == transformedRowIndex*amountOfSeedsPerUnimportantSection:# we entered the important section!
#             for _ in range(0,amountOfSeedsPerUnimportantSection):#creating 1 less indicator and forcing the last
#                 indicatorValue = random.randint(0,amountOfCwToCreate)
#                 tempIndicatorList.append(indicatorValue)
#                 tIndicatorsPool.append(indicatorValue)
#             indicatorValue = createForcedTIndicator(tempIndicatorList,amountOfCwToCreate)
#         else:
#             indicatorValue = random.randint(0,amountOfCwToCreate)
#         tIndicatorsPool.append(indicatorValue)
#         
#     return tIndicatorsPool  
def transformIndexBit():
    global transformedRowIndex
    global transformedColumnIndex
    transformedRowIndex    = int(bitToExtractIndex/(math.sqrt(dataBaseSizeVar)))#important section index
    transformedColumnIndex = int(bitToExtractIndex%(math.sqrt(dataBaseSizeVar)))
def createEjVector():
    global unitVectorJAsBytes
    rootedDatabaseSizeVar = (int)(math.sqrt(dataBaseSizeVar))
    unitVectorJAsBytes = BitArray(int = 1, length = rootedDatabaseSizeVar)
    unitVectorJAsBytes <<= ((rootedDatabaseSizeVar-1) - transformedColumnIndex)
#     print (unitVectorJAsBytes.bin)
def findKthCW(aListOfGFunction):
    tempGFunctionResult = BitArray(int = 0,length = (int)(math.sqrt(dataBaseSizeVar)))
    tempCWResult        = BitArray(int = 0,length =(int)(math.sqrt(dataBaseSizeVar)))
    
    for gFunction in aListOfGFunction:
        tempGFunctionResult = tempGFunctionResult ^ gFunction
    for cw in CWListPool:
        tempCWResult = tempCWResult ^ cw
    kthCw = tempGFunctionResult ^ tempCWResult ^ unitVectorJAsBytes
#     print("kthCW:",kthCw)
    CWListPool.append(kthCw)
def generateQuery(aSeedsList,aListOfGFuncion,aTIndicatorsList):
    global serversQuery
    rootedDatabaseSizeVar = (int)(math.sqrt(dataBaseSizeVar))
    #  print("rootedSize",rootedDatabaseSizeVar)
    #  print("j index:",transformedColumnIndex)
    #  print("i' index:",transformedRowIndex)
    tempSeedListPerSection = []
    serversQuery = {}
    startIndex = 0
    endIndex = 0

#     print("seed pool",seedListAsBytes)
    for serverAmountIndex in range(0,servers):
        serversQuery[serverAmountIndex] = ([],[])
    for sectionIndex in range(0,rootedDatabaseSizeVar):
        seedIndex = 0
        
        if sectionIndex == transformedRowIndex:# important section
            choosingMatrix = matrixB
            importantSectionIndicator = 0
        else:#not important section
            choosingMatrix = matrixA
            importantSectionIndicator = 1
            
        #prepares the indices for next withdrawal from seed pool for all runs except the first run
        startIndex = endIndex
        endIndex   = endIndex + 2**(servers-1) - importantSectionIndicator    
           
        if sectionIndex == 0: #first run
            startIndex = 0
            endIndex   = 2**(servers-1)-importantSectionIndicator    
        
        tempSeedListPerSection = aSeedsList[startIndex:endIndex]
#         tempIndcatorListPerSection = aTIndicatorsList[startIndex:endIndex]
       
        if importantSectionIndicator == 1:# when we in a section that is not important we have an array of 2^(k-1) seeds, and we need to add another seed to be modular
            tempSeedListPerSection.insert(0,0xFF)
#             tempIndcatorListPerSection.insert(0,0xFF)
        else:#important section
            tempGFunctionPerSection = aListOfGFuncion[startIndex:endIndex]
            findKthCW(tempGFunctionPerSection)
            

        for choosingMatrixColumnIndex in choosingMatrix:
            matchSeedToServerList = [i for i, j in enumerate(choosingMatrixColumnIndex) if j == 1]
            #  print("matchedListMatrix A",matchSeedToServerList)
            for serverIndex in matchSeedToServerList:
                tmpSeedList,tmpIndicatorsList = serversQuery[serverIndex]
                
                tmpSeedList.append(tempSeedListPerSection[seedIndex])
                tmpIndicatorsList.append(aTIndicatorsList[seedIndex])

#                 tmpIndicatorsList.append(tempIndcatorListPerSection[seedIndex])
                
                serversQuery[serverIndex] = (tmpSeedList,tmpIndicatorsList)
            seedIndex+=1
            # print("server query",serversQuery)  
        random.shuffle(aTIndicatorsList)  
#     print("server query",serversQuery[0])
#     print("server query",serversQuery[1])
#     print("server query",serversQuery[2])
def appendCWListPoolToQuery():
    global serversQueryWithCWAppended 
    serversQueryWithCWAppended = {}
    
    for serversIndex in range(0,servers):
        seedsList,indicatorsList = serversQuery[serversIndex]
        serversQueryWithCWAppended[serversIndex] = (seedsList,indicatorsList,CWListPool)
#     print("amount of CW:",CWListPool.__len__())  
#     print("server query with CWListPool",serversQueryWithCWAppended[0][2].__len__())
#     print("server query with CWListPool",serversQueryWithCWAppended[1])
#     print("server query with CWListPool",serversQueryWithCWAppended[2])
def GfuncionXorCwListFunction(aListOfGFunction,aIndicatorsList,aCwList):
    tempListGFuncAndCw = []
    
    for G_S,tIndicator in zip(aListOfGFunction,aIndicatorsList):
        tempListGFuncAndCw.append(G_S^aCwList[tIndicator])
    
    return tempListGFuncAndCw
def createZVector(aListOfGfuncionXorCwList):
    tempZ_Vector = BitArray()
    tempResultPerSection = BitArray(int = 0,length = (int)(math.sqrt(dataBaseSizeVar)))
    
    aListOfGfuncionXorCwList.reverse()
    while aListOfGfuncionXorCwList:
        tempResultPerSection = BitArray(int = 0,length = (int)(math.sqrt(dataBaseSizeVar)))
        for _ in range(0,seedsPerSection):
            tempResultPerSection = tempResultPerSection ^ aListOfGfuncionXorCwList.pop()
        tempZ_Vector.append(tempResultPerSection)
        
    return tempZ_Vector    
def createRespone(aB_DB,aZVector):
#     print("db size and z vector:",aB_DB.length,aZVector.length)
    tempAnswer = 0
    for bitFromDB,bitFromZVector in zip(aB_DB,aZVector):
        tempAnswer = tempAnswer + bitFromDB*bitFromZVector
    answer = tempAnswer%2    
    return answer
def decryptQuery(aQueryFromUserToDecrypt):
    global seedsPerSection
    rootedDatabaseSizeVar = (int)(math.sqrt(dataBaseSizeVar))
    seedListToInflate,indicatorsList,cwList = aQueryFromUserToDecrypt
    seedsPerSection = int(seedListToInflate.__len__()/rootedDatabaseSizeVar)

    listOfGFunction = createGFunctions(seedListToInflate)
#     print("from server     seed list size:",seedListToInflate.__len__(),"g fun list size",listOfGFunction.__len__(),"indicators list size",indicatorsList.__len__())
#     print("forcedIndicator:",indicatorsList[1])
#     print("listOfGFunction - server side:",listOfGFunction)
#     print("list indicators - server side:",indicatorsList)
#     print("cw list ",cwList)
    listOfGfuncionXorCwList = GfuncionXorCwListFunction(listOfGFunction,indicatorsList,cwList)
    zVector = createZVector(listOfGfuncionXorCwList)#return a vector of length n
    response = createRespone(b_DB,zVector)
#     print("server z vector:",zVector.hex)
#     print("response:" ,response)
    return response
def bitClientRequested(aListOfResponses):
    desiredBit = aListOfResponses.count(1)%2
    
    return desiredBit
def runHandler():
    global servers
    global dataBaseSizeVar
    global bitToExtractIndex
    global CWlist
    
    try:
        servers = int(serverAmount.get())
        try:
            dataBaseSizeVar = int(dataBaseSize.get())
            try:
                bitToExtractIndex = int(ChosenBit.get())
                if (bitToExtractIndex >= dataBaseSizeVar) | (bitToExtractIndex < 0):
                    print("choose bit in range of 0 - " ,dataBaseSizeVar-1)
                else:    
                    if methodFlag == False:
#                         print("False from Run")
                        pass
                    else:
#                         print("True from Run")
                        pass
                for _ in range(0,10):
                    #start of user-end for building&encoding the query
                    buildMatrices()
                    seedList       = createRandomSeeds()
                    listOfGFuncion = createGFunctions(seedList)
                    transformIndexBit()
                    createCWListPool()
                    listOfIndicators = createTIndicatorsPool()
                    createEjVector()
#                     print("client g function list: ",listOfGFuncion)
#                     print("from client     seed list size:",seedList.__len__(),"g fun list size",listOfGFuncion.__len__(),"indicators list size",listOfIndicators.__len__())
                    generateQuery(seedList,listOfGFuncion,listOfIndicators)
                    appendCWListPoolToQuery()
                    #end of user-end for building the query
                    
                    #start of server-end for decoding the query
                    global b_DB
                    b_DB = BitArray(hex(random.getrandbits(16384)))
                    listOfBitsToSend = []
                    for serverIndex in range(0,servers):
                        bitToSendToClient = decryptQuery(serversQueryWithCWAppended[serverIndex])
                        listOfBitsToSend.append(bitToSendToClient)
                    #####send bitToSend function######  
                      
                    #end of server-end for decoding the query
                    
                    #start client does XOR with all responses
                    requestedBit = bitClientRequested(listOfBitsToSend)
                    d_DbBit = int(b_DB.bin[bitToExtractIndex])
                    if requestedBit == d_DbBit:
                        print("success")
                    else:    
                        print("failed")
#                     print("Requested Bit from algorithm",requestedBit)
#                     print("Actual Bit from Date Base ",b_DB.bin[bitToExtractIndex],"at index:",bitToExtractIndex)
                    #end client does XOR with all responses
                quitHandler()              
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
mServerAmount.insert(0, "3")  
mServerAmount.grid(row=0,column=1,columnspan= 2)

Label(root,text = "Data Base Size:",fg = "blue",borderwidth=15).grid(row=1,sticky=S)

mDataBaseSize= Entry(root,textvariable = dataBaseSize)   
mDataBaseSize.insert(0, "16384")
mDataBaseSize.grid(row=1,column=1,columnspan= 2)

Label(root,text = "Choose bit from DB:",fg = "blue",borderwidth=15).grid(row=2,sticky=S)

mDataBaseBit= Entry(root,textvariable = ChosenBit)
mDataBaseBit.insert(0, "129")  
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
    
    
    
