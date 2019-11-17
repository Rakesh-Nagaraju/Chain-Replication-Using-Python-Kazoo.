#Distributed Computing Assignment Project on Chain Replication
#Author: Rakesh Nagaraju, Student ID: 014279304
from concurrent import futures
from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.client import KazooRetry
from atexit import register
import kazoo.recipe.watchers
import sys
import time
import grpc
import chain_pb2
import chain_pb2_grpc
import time
import logging
#Loging Information.
logging.basicConfig()

#Head Chain Implementation using Python and kazoo for connection to Zookeeper.
#Creating a Class named ChainServer.
class ChainServer(chain_pb2_grpc.HeadChainReplicaServicer):
    
    def __init__(self):
        self.xid = 0
        self.hash_dict = {}
        self.sent_list = []
        self.head_server = True
        self.tail_server = True
        self.successor_Id = None
        self.successor_My_address = None
        self.predecessor_Id = None
        self.predecessor_My_address = None
        self.successor_Stub = None
        self.head_stub = None
        self.my_sess_id = None
        self.my_address = None
    
    #Funtion to Set Session id and Address.
    def set_vals(self, my_sess_id, my_address):
        self.my_sess_id = my_sess_id
        self.my_address = my_address
    
    #Function to find my Current position in Zookeeper and also find Head, Tail,
    #Succesors and Predecessors if any.
    def update(self, Sessions):
        suc_add = self.successor_My_address
        Sessions.sort()
        myIndex = Sessions.index((self.my_sess_id).lstrip("0x").encode("utf-8"))
        self.head_server = myIndex == 0
        self.tail_server = myIndex == len(Sessions) - 1
        if self.head_server == True:
            self.predecessor_Id = None
            self.predecessor_My_address = None
        else:
            self.predecessor_Id = Sessions[myIndex - 1]
            data, ver = zk.get("/headchain/" + Sessions[myIndex - 1])
            self.predecessor_My_address = data.decode("utf-8")
        if self.tail_server == True:
            self.successor_Id = None
            self.successor_My_address = None
        else:
            self.successor_Id = Sessions[myIndex + 1]
            data, ver = zk.get("/headchain/" + Sessions[myIndex + 1])
            self.successor_My_address = data.decode("utf-8")
        if suc_add != self.successor_My_address and self.tail_server == False:
            channel = grpc.insecure_channel(self.successor_My_address)
            self.successor_Stub = chain_pb2_grpc.HeadChainReplicaStub(channel)
            #Head State Transfer Update.
            print("Sending State Transfer Request...")
            request = chain_pb2.HeadStateTransferRequest(src=int(self.my_sess_id, 0), stateXid=self.xid, state=self.hash_dict, sent_list=self.sent_list)
            print(self.successor_Stub.stateTransfer(request))
        data, ver = zk.get("/headchain/" + Sessions[0])
        channel = grpc.insecure_channel(data)
        self.head_stub = chain_pb2_grpc.HeadChainReplicaStub(channel)
        data, ver = zk.get("/headchain/" + Sessions[len(Sessions)-1])
        channel = grpc.insecure_channel(data)
        self.tail_stub = chain_pb2_grpc.HeadChainReplicaStub(channel)
        print("My Current Info:")
        if self.head_server:
            print("I'm the Head!!! ")
        if self.tail_server:
            print("I'm the Tail!!! ")
        elif (self.head_server != True and self.tail_server != True):
            print("I'm a Replica!!!")
        print("Head val",str(self.head_server),"Tail: ",str(self.tail_server),"My My_address: ",str(self.my_address),"My Current xid: ",str(self.xid),
      "Hash_hash_dict(key,pair): ",str(self.hash_dict))

#Function to Perform State Update.
    def proposeStateUpdate(self, HeadStateUpdateRequest, context):
        print("got state update request: {}".format(HeadStateUpdateRequest))
        if self.head_server:
          print("Returning RC=1, because I'm the Head.")
          return chain_pb2.ChainResponse(rc=1)
        if HeadStateUpdateRequest.src != int("0x"+self.predecessor_Id, 0):
          print("Returning RC=1, because its not from my Predecessor.")
          return chain_pb2.ChainResponse(rc=1)
        if HeadStateUpdateRequest.xid <= self.xid:
          print("Returning RC=1, because Xid is lesser than Mine.")
          return chain_pb2.ChainResponse(rc=1)
        self.hash_dict[HeadStateUpdateRequest.key] = HeadStateUpdateRequest.value
        self.xid = HeadStateUpdateRequest.xid
        #Call Xid Processed request.
        if self.tail_server == True:
         print("Sending Xid Processed Request...")
         request = chain_pb2.XidProcessedRequest(xid=self.xid)
         print(self.head_stub.xidProcessed(request))
        else:
         print("Sending State Update Request...")
         request = chain_pb2.HeadStateUpdateRequest(src=int(self.my_sess_id, 0), xid=HeadStateUpdateRequest.xid, key=HeadStateUpdateRequest.key, value=HeadStateUpdateRequest.value)
         self.sent_list.append(request)
         print(self.successor_Stub.proposeStateUpdate(request))
        #Call Latest Xid request.
        print("Latest Xid Request!!!")
        request = chain_pb2.LatestXidRequest()
        print("Sending Get latest Xid Request...")
        response = self.tail_stub.getLatestXid(request)
        if response.rc == 0:
         for request in self.sent_list:
          if (response.xid <= self.xid):
           self.sent_list.remove(request)
        print("Returning RC=0")
        return chain_pb2.ChainResponse(rc=0)

    #Function to Perform Get Latest Xid.
    def getLatestXid(self, LatestXidRequest, context):
        print("got get latest xid Request: {}".format(LatestXidRequest))
        if self.tail_server == False:
           print("Returning RC=1, because I'm not the Tail Server.")
           return chain_pb2.LatestXidResponse(rc=1, xid=self.xid)
        print("Returning RC=0")
        return chain_pb2.LatestXidResponse(rc=0, xid=self.xid)
    
    #Function to Perform State Transfer.
    def stateTransfer(self, HeadStateTransferRequest, context):
        print("got state transfer Request: {}".format(HeadStateTransferRequest))
        if self.head_server:
            print("Returning RC=1, because I'm the Head Server.")
            return chain_pb2.ChainResponse(rc=1)
        if HeadStateTransferRequest.src != int(self.predecessor_Id, 0):
            print("Returning RC=1, because its not from my Predecessor.")
            return chain_pb2.ChainResponse(rc=1)
        self.xid = HeadStateTransferRequest.stateXid
        self.hash_dict = HeadStateTransferRequest.state
        self.sent_list = HeadStateTransferRequest.sent_list
        print("Returning RC=0")
        return chain_pb2.ChainResponse(rc=0)
    
    #Increment Function, Request is received from Client received if Head else return rc=1 I'm not Head.
    def increment(self, IncrementRequest, context):
        print("got increment Request: {}".format(IncrementRequest))
        if self.head_server == False:
            print("Returning RC=1, because I'm not the Head server.")
            return chain_pb2.HeadResponse(rc=1)
        if IncrementRequest.key in self.hash_dict:
            self.hash_dict[IncrementRequest.key] += IncrementRequest.incrValue
        else:
            self.hash_dict[IncrementRequest.key] = IncrementRequest.incrValue
        if self.tail_server == False:
            self.xid += 1
            #Call Head State Update request.
            print("Sending State Update Request...")
            request = chain_pb2.HeadStateUpdateRequest(src=int(self.my_sess_id, 0), xid=self.xid, key=IncrementRequest.key, value=self.hash_dict[IncrementRequest.key])
            self.sent_list.append(request)
            print(self.successor_Stub.proposeStateUpdate(request))
        print("Returning RC=0")
        return chain_pb2.HeadResponse(rc=0)
    
    #Delete Function, Request is received from Client received if Head else return rc=1 I'm not Head.
    def delete(self, DeleteRequest, context):
        print("got delete Request: {}".format(DeleteRequest))
        if self.head_server == False:
            print("Returning RC=1, because I'm not the Head.")
            return chain_pb2.HeadResponse(rc=1)
        if DeleteRequest.key in self.hash_dict:
            self.hash_dict[DeleteRequest.key] = 0
        if self.tail_server == False:
            self.xid += 1
            #Call Head State Update request.
            print("Sending State Update Request...")
            request = chain_pb2.HeadStateUpdateRequest(src=int(self.my_sess_id, 0), xid=self.xid, key=DeleteRequest.key, value=self.hash_dict[DeleteRequest.key])
            self.sent_list.append(request)
            print(self.successor_Stub.proposeStateUpdate(request))
        print("Returning RC=0")
        return chain_pb2.HeadResponse(rc=0)
    
    #Get Function, Request is received from Client received if Tail else return rc=1 I'm not Tail.
    def get(self, GetRequest, context):
        print("got get Request: {}".format(GetRequest))
        if self.tail_server == False:
            print("Returning RC=1, because I'm not the Tail.")
            return chain_pb2.GetResponse(rc=1, value=0)
        if GetRequest.key in self.hash_dict:
            print("Returning RC=0")
            return chain_pb2.GetResponse(rc=0, value=self.hash_dict[GetRequest.key])
        print("Returning RC=0, but its value is 0.")
        return chain_pb2.GetResponse(rc=0, value=0)
    
    #Function to Perform Xid Processed.
    def xidProcessed(self, XidProcessedRequest, context):
        print("got xid processed: {}".format(XidProcessedRequest))
        if self.head_server:
            print("Returning RC=0")
            return chain_pb2.ChainResponse(rc=0)
        else:
            print("Returning RC=1")
            return chain_pb2.ChainResponse(rc=1)

try:
 #Creating a Server.
 cs = ChainServer()
 #Connecting to Zookeeper.
 zk = KazooClient(hosts=sys.argv[1])
 zk.start()
 zk.ensure_path("/headchain")
 #Get Session ID.
 sid, pw = zk.client_id
 #Change the below line to Your System's IP address.
 cs.set_vals(hex(sid),"10.0.0.48:" + sys.argv[2])
 server = grpc.server(futures.ThreadPoolExecutor())
 chain_pb2_grpc.add_HeadChainReplicaServicer_to_server(cs, server)
 #Change the below line to Your System's IP address.
 server.add_insecure_port("10.0.0.48:" + sys.argv[2])
 #Begin Server.
 server.start()
 #Change the below line to Your System's IP address.
 zk.create("/headchain/" + (hex(sid)).lstrip("0x"), ("10.0.0.48:" + sys.argv[2]).encode(),ephemeral=True)
 #Watchers to Update Head Tail Succesor and Predecessor when a node joins or leaves the Network.
 @zk.ChildrenWatch("/headchain")
 def watch_children(Sessions):
     cs.update(Sessions)
 while True:
     time.sleep(60)
 #Register to handle Termination.
 def deleteSelf():
     zk.delete("/headchain/" + str(hex(sid)))
     zk.stop()
 register(deleteSelf)
except:
 pass
#END
