codes = {234 : 'server_hello', 235 : 'hello_ack', 236 : 'server_quantity_request' , 237 : 'server_quantity_reply' , 238 : 'servers_up' , 239 : 'servers_faild',  240 : 'db_length' , 241 : 'db_length_request' ,  242 : 'pir_query' , 243 : 'pir_query_reply' ,  244 : 'std_query' , 245 : 'std_query_reply' ,  246 : 'terminate' , 247 : 'ip_and_port_request' ,  248 : 'ip_and_port_reply',  249 : 'client_hello' }
 
class OpCodes(object):
    '''
    classdocs
    '''

    
    
    ##Find in the opCodes a code description by it's key     
    def getCode(self,codeToFind):
        try:
            return codes[codeToFind]
        except Exception:
            return
        
        
    ##Find in the opCodes a value by it's key     
    def getValue(self,valueToFind):
        try:
            return [ k for k, element in codes.items() if element == valueToFind]
        except Exception:
            return 