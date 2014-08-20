import os
import math
import logging
import random
from bitstring import BitArray
import time
from Crypto import Random
from Crypto.Cipher import AES
from sys import byteorder
import random
from itertools import count
import pickle 

logging.basicConfig(level=logging.DEBUG,format='%(name)s: %(message)s',)   

class PIRQueryObject():
    

    DB_LENGTH = 0
    SEED_LENGTH = 128
    currentServersQuantity = 0
    amountOfSeeds = 0
    serversQuery = {}
    finaleServersQueries = {}
    CWListPool = []
    seedsPerSection = 0
   
        
    def __init__(self, aServersQuantity, aDBLength, aSeedLength = 128):
        self.logger = logging.getLogger("PIR Query")
        self.logger.debug("PIR query is UP!")
        self.DB_LENGTH = aDBLength
        self.SEED_LENGTH = aSeedLength
        self.currentServersQuantity = aServersQuantity
#         self.f = open("zVector", 'wb')

    def setDB(self,aB_DB):
        self.b_DB = aB_DB
        
    def encrypt(self,message, key=None, key_size=128):
        def pad(s):
            x = AES.block_size - len(s) % AES.block_size
            return s + (bytes([x]) * x)
     
        padded_message = pad(message)
        if key is None:
            key = Random.new().read(key_size // 8)
     
        cipher = AES.new(key)
        return (cipher.encrypt(padded_message))        

   
    def createRandomSeeds(self):
        seedListAsBytes = []
        self.amountOfSeeds = int((math.sqrt(self.DB_LENGTH)-1)*(2**(self.currentServersQuantity-1)-1)+2**(self.currentServersQuantity-1))
#         self.logger.info("amount of seeds:",self.amountOfSeeds)
        for _ in range (0,self.amountOfSeeds):
            seedAsByte = BitArray(os.urandom(16))
            seedListAsBytes.append(seedAsByte.hex)
        return seedListAsBytes        
    
    def createGFunctions(self,aSeedList):
        listOfGFunction = []
    
        for seed in aSeedList:   
            listOfGFunction.append(self.inflatorFunction(seed)) 
         
        return listOfGFunction    
    def createCWListPool(self):
        self.CWListPool = []  
        #tempCw = BitArray(os.urandom((int)(math.sqrt(dataBaseSizeVar)/8)))
    #     CWList.append(tempCw)
        for _ in range (1,2**(self.currentServersQuantity-1)):
            tempCw = BitArray(os.urandom((int)(math.sqrt(self.DB_LENGTH)/8)))
            self.CWListPool.append(tempCw)
#         self.logger.info("size of CWlist: %d",self.CWListPool.__len__())            
        
        
    def createForcedTIndicator(self,aTempIndicatorList,aAmountOfCwToCreate):
        answer = 0
        for indicator in aTempIndicatorList: 
            answer = answer ^ indicator
        return answer    
    
    
    def convertMatrix(self,aMatrixToConvert,aNumOfRows):
        self.matrixA = []
        self.matrixB = []
        
        for index in range (0,aNumOfRows):
            if (aMatrixToConvert[index].count(1)%2) == 0:
                self.matrixA.append(aMatrixToConvert[index])
            else:
                self.matrixB.append(aMatrixToConvert[index])
    #     self.logger.info("matrix A",matrixA)
    #     self.logger.info("matrix B",matrixB)
        t=0  
        for i in  self.matrixA:  
            t+=i[0]   
#         self.logger.info("seed per section:",t)            
        
            
    def buildMatrices(self):
        matrix = []
#         numRows
        numOfRows = 2**self.currentServersQuantity
#         self.logger.info("current Servers Quantity = %d" ,self.currentServersQuantity)
        for index in range (0,numOfRows):
            matrix.append([int(d) for d in bin(index)[2:].zfill(self.currentServersQuantity)])
        #   self.logger.info(matrix)
        self.convertMatrix(matrix,numOfRows)        
        
      
    def transformIndexBit(self):
#         global transformedRowIndex
#         global transformedColumnIndex
#         
        self.transformedRowIndex    = int(self.bitToExtractIndex/(math.sqrt(self.DB_LENGTH))) #### i'
        self.transformedColumnIndex = int(self.bitToExtractIndex%(math.sqrt(self.DB_LENGTH))) #### j
    
    

    def createEjVector(self):
#         global unitVectorJAsBytes
        rootedDatabaseSizeVar = (int)(math.sqrt(self.DB_LENGTH))
        self.unitVectorJAsBytes = BitArray(int = 1, length = rootedDatabaseSizeVar)
        self.unitVectorJAsBytes <<= ((rootedDatabaseSizeVar-1) - self.transformedColumnIndex)
#         self.logger.info (self.unitVectorJAsBytes.bin)


    def inflatorFunction(self,aSeedToInflate):
        gFunction = BitArray(self.encrypt(str(0).encode('utf-8'),aSeedToInflate))
        for i in range (1,(int)(math.sqrt(self.DB_LENGTH)/self.SEED_LENGTH)):
            gFunction.append(self.encrypt(str(i).encode('utf-8'),aSeedToInflate))
        return BitArray(gFunction)        
    
    def createTIndicatorsPool(self):
        tIndicatorsPool = list(range(0,2**(self.currentServersQuantity-1)))
#     print("created tInd:",tIndicatorsPool)
        return tIndicatorsPool 
    
#     def createTIndicatorsPool(self):
#         tIndicatorsPool = []
#         for tIndicatorIndex in range (0,2**(self.currentServersQuantity-1)):
#             tIndicatorsPool.append((tIndicatorIndex,tIndicatorIndex))
#         return tIndicatorsPool    
    
    
    def findKthCW(self,aListOfGFunction):
        tempGFunctionResult = BitArray(int = 0,length = (int)(math.sqrt(self.DB_LENGTH)))
        tempCWResult        = BitArray(int = 0,length =(int)(math.sqrt(self.DB_LENGTH)))
        
        for gFunction in aListOfGFunction:
            tempGFunctionResult = tempGFunctionResult ^ gFunction
        for cw in self.CWListPool:
            tempCWResult = tempCWResult ^ cw
        kthCw = tempGFunctionResult ^ tempCWResult ^ self.unitVectorJAsBytes
#     print("kthCW:",kthCw)
        self.CWListPool.append(kthCw)
        
    
    def appendCWListPoolToQuery(self):
#         global serversQueryWithCWAppended 
        serversQueryWithCWAppended = {}
        
        for serversIndex in range(0,self.currentServersQuantity):
            seedsList,indicatorsList = self.serversQuery[serversIndex]
            serversQueryWithCWAppended[serversIndex] = (seedsList,indicatorsList,self.CWListPool)
        self.logger.info("amount of CW: %s",self.CWListPool.__len__())  
    #     self.logger.info("server query with CWListPool",serversQueryWithCWAppended[0][2].__len__())
    #     self.logger.info("server query with CWListPool",serversQueryWithCWAppended[1])
    #     self.logger.info("server query with CWListPool",serversQueryWithCWAppended[2]
        return serversQueryWithCWAppended


        
    def assamblePIRQuery(self,aSeedsList,aListOfGFuncion,aTIndicatorsList):
        
#         self.serversQuery
        rootedDatabaseSizeVar = (int)(math.sqrt(self.DB_LENGTH))
        #  self.logger.info("rootedSize",rootedDatabaseSizeVar)
        #  self.logger.info("j index:",transformedColumnIndex)
        #  self.logger.info("i' index:",transformedRowIndex)
        
        
        tempSeedListPerSection = []
        
        startIndex = 0
        endIndex = 0
        
    #     self.logger.info("seed pool",seedListAsBytes)
        for serverAmountIndex in range(0,self.currentServersQuantity):
            self.serversQuery[serverAmountIndex] = ([],[])
        for sectionIndex in range(0,rootedDatabaseSizeVar):
            seedIndex = 0
            
            if sectionIndex == self.transformedRowIndex:# important section
                choosingMatrix = self.matrixB
                importantSectionIndicator = 0
            else:#not important section
                choosingMatrix = self.matrixA
                importantSectionIndicator = 1
                
            #prepares the indices for next withdrawal from seed pool for all runs except the first run
            startIndex = endIndex
            endIndex   = endIndex + 2**(self.currentServersQuantity-1) - importantSectionIndicator    
               
            if sectionIndex == 0: #first run
                startIndex = 0
                endIndex   = 2**(self.currentServersQuantity-1)-importantSectionIndicator    
            
            tempSeedListPerSection = aSeedsList[startIndex:endIndex]
            
            if importantSectionIndicator == 1:# when we in a section that is not important we have an array of 2^(k-1) seeds, and we need to add another seed to be modular
                tempSeedListPerSection.insert(0,0xFF)
            else:#important section
                tempGFunctionPerSection = aListOfGFuncion[startIndex:endIndex]
                self.findKthCW(tempGFunctionPerSection)
    #         self.logger.info("choosing matrix ",choosingMatrix,"section number:",sectionIndex+1)
    #         self.logger.info("list for a section",tempSeedListPerSection) 
            
            
            for choosingMatrixColumnIndex in choosingMatrix:
                matchSeedToServerList = [i for i, j in enumerate(choosingMatrixColumnIndex) if j == 1]
                #  self.logger.info("matchedListMatrix A",matchSeedToServerList)
                for serverIndex in matchSeedToServerList:
                    tmpSeedList,tmpIndicatorsList = self.serversQuery[serverIndex]
                    tmpSeedList.append(tempSeedListPerSection[seedIndex])
                    tmpIndicatorsList.append(aTIndicatorsList[seedIndex])
                    self.serversQuery[serverIndex] = (tmpSeedList,tmpIndicatorsList)
                seedIndex+=1
                # self.logger.info("server query",serversQuery)    
            random.shuffle(aTIndicatorsList)
    #     self.logger.info("server query",serversQuery[0])
    #     self.logger.info("server query",serversQuery[1])
    #     self.logger.info("server query",serversQuery[2])    
    
    
    def getPIRQuery(self,aBitToExtractIndex):
        self.bitToExtractIndex   = aBitToExtractIndex
        self.buildMatrices()
        seedList            = self.createRandomSeeds()
        listOfGFuncion      = self.createGFunctions(seedList)
        self.transformIndexBit()
        self.createCWListPool()
        listOfIndicators    = self.createTIndicatorsPool()
        self.createEjVector()
        self.assamblePIRQuery(seedList,listOfGFuncion,listOfIndicators)
        self.finaleServersQueries = self.appendCWListPoolToQuery()
#         self.calacQuerySize()
        return self.finaleServersQueries     
    
    
    def calacQuerySize(self):
        self.totSize = 0
        seeds,indcators,cws = self.finaleServersQueries[0]
        self.totSize = seeds.__len__() * self.SEED_LENGTH
        self.totSize = self.totSize + (cws.__len__() * (int)(math.sqrt(self.DB_LENGTH)))
        self.totSize = self.totSize + indcators.__len__()*(self.currentServersQuantity-1)
        self.totSize = self.totSize * self.currentServersQuantity
        return self.totSize
        
    def GfuncionXorCwListFunction(self,aListOfGFunction,aIndicatorsList,aCwList):
        tempListGFuncAndCw = []
        
        for G_S,tIndicator in zip(aListOfGFunction,aIndicatorsList):
            tempListGFuncAndCw.append(G_S^aCwList[tIndicator])
        
        return tempListGFuncAndCw
    
    
    def createZVector(self,aListOfGfuncionXorCwList):
        tempZ_Vector = BitArray()
        tempResultPerSection = BitArray(int = 0,length = (int)(math.sqrt(self.DB_LENGTH)))
        
        aListOfGfuncionXorCwList.reverse()
        while aListOfGfuncionXorCwList:
            tempResultPerSection = BitArray(int = 0,length = (int)(math.sqrt(self.DB_LENGTH)))
            for _ in range(0,self.seedsPerSection):
                tempResultPerSection = tempResultPerSection ^ aListOfGfuncionXorCwList.pop()
            tempZ_Vector.append(tempResultPerSection)
            
        return tempZ_Vector   


    def createRespone(self,aZVector):
#     print("db size and z vector:",aB_DB.length,aZVector.length)
        tempAnswer = 0
        for bitFromDB,bitFromZVector in zip(self.b_DB,aZVector):
            tempAnswer = tempAnswer + bitFromDB*bitFromZVector
        answer = tempAnswer%2    
        return answer


    def decryptQuery(self,aQueryFromUserToDecrypt):
#         global seedsPerSection
        rootedDatabaseSizeVar = (int)(math.sqrt(self.DB_LENGTH))
        seedListToInflate,indicatorsList,cwList = aQueryFromUserToDecrypt
        self.seedsPerSection = int(seedListToInflate.__len__()/rootedDatabaseSizeVar)
    
        listOfGFunction = self.createGFunctions(seedListToInflate)
    #     print("from server     seed list size:",seedListToInflate.__len__(),"g fun list size",listOfGFunction.__len__(),"indicators list size",indicatorsList.__len__())
    #     print("forcedIndicator:",indicatorsList[1])
#         self.logger.info("listOfGFunction - server side: %s",listOfGFunction)
    #     print("list indicators - server side:",indicatorsList)
    #     print("cw list ",cwList)
        listOfGfuncionXorCwList = self.GfuncionXorCwListFunction(listOfGFunction,indicatorsList,cwList)
        zVector = self.createZVector(listOfGfuncionXorCwList)#return a vector of length n
        response = self.createRespone(zVector)
#         self.f = open("zVector", 'ab+')
#         pickle.dump(zVector.hex, self.f)
#         self.f.close()
#         self.logger.info("server z vector: %s",zVector.hex)
    #     print("response:" ,response)
        return response
    
    
    def calculateQueryResult(self,aServersQueryReply):
        desiredBit = aServersQueryReply.count(1)%2        
        return desiredBit
    
        
        
        
###############################################################################
##            Getters Setters section                                        ##
###############################################################################         
   
    def setDBLength(self,aSizeToSet):
        if aSizeToSet < 16384:
            self.logger.info("Data Base size not valid")
        else:
            self.DB_LENGTH = aSizeToSet
    
    def setSeedSize(self,aSizeToSet):
        if aSizeToSet < 128:
            self.logger.info("Seed size not valid")
        else:
            self.SEED_LENGTH = aSizeToSet
    def setCurrentServersQuantity(self,aNumServersToUpdate):
        self.currentServersQuantity = aNumServersToUpdate
    
    
        