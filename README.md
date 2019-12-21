# Chain-Replication-Using-Python-Kazoo.
Python Chain Replication Server that can perform the Head, Replica and Tail in the Chain. This server uses Kazoo to connect to the Zookeeper. 
****************************************************************************************************************************
DETAILS OF THIS PROJECT: CHAIN REPLICATION 
****************************************************************************************************************************
This project is to implement chain replication. 
Specifically, we will be implementing a replica that will form part of a chain replication chain. 
We will deal with links (replicas) going away and new links arriving as the server connected in a network may be the head or the tail or just a replica in the chain.

The service we are providing to clients will be an incrementable hashtable. 
It is a hashtable whose key is a string and value is an integer.
The nodes in the chain cannot directly set the integer for a given key, but it can increment,decrement it(we decrement by incrementing with a negative number). 
If a key does not exist in the table, we act as if the key as a value of zero. 

The three operations we can do on the table are:
  get(key) - returns the current integer for the key, or zero if the key does not exist.
  inc(key, value) - increments the key by the given value.
  del(key) - deletes a key from the table, effectively setting its value to zero.

Only, Head server in the chain can receive and perform increment and decrement Operations from the client and this data is passed on along to all the nodes in the chain.
Only the Tail server,can receive perform Get request from the client.
 
For our implementations, we will use grcp with the proto file chain.proto(in the repository) to interoperate.

****************************************************************************************************************************
Here's some more details to understand the service methods for the head chain implementation.
****************************************************************************************************************************

1)proposeStateUpdate(HeadStateUpdateRequest) returns (ChainResponse):
  Called by the head during get or delete updates and is forwarded down the chain.
  When the tail gets state update, it responds directly to the Head.
 
2)getLatestXid(LatestXidRequest) returns (LatestXidResponse):
  Nodes get the latest xid from the tail and this xid is used for purging the sent list. 
  For example you can get the latest Xid from the Tail and know that everything before that Xid has been processed and you     can remove them form the list so that the list doesn't infinitely grow.
 
3)stateTransfer(HeadStateTransferRequest) returns (ChainResponse):
  New tail gets state transfer from previous node.
 
4)increment(IncrementRequest) returns (HeadResponse):
  Client asks the head to increment, then head increments the key with the value and then sends proposeStateUpdate.
 
5)delete(DeleteRequest) returns (HeadResponse);
  Client asks the head to delete, then head deletes the key and then sends proposeStateUpdate
 
6)get(GetRequest) returns (GetResponse);
  Client asks tail for value, tail responds with the key value.
 
7)xidProcessed(XidProcessedRequest) returns (ChainResponse);
  is for the Tail to let the Head know that it is done processing an operation with a particular xid. The head needs to know   which operation is being finished so that it can respond to the corresponding client, since there can be multiple clients   with open connections at any given time.


****************************************************************************************************************************
INFORMATION ON RUNNING THE CODE:
****************************************************************************************************************************
Zookeeper, Head Client jar file is included, for testing purposes.

First,
Git Clone this repository to a folder.
Make sure your System meets the Requirements specified in the Requirements file.
Connect to a Network using a Wifi-router or a Hotspot. Get the IP address of your System.

Zookeeper(for testing): zookeeper-dev-fatjar.jar
Then, Run Zookeeper jar file with IP address, 4-digit port number(default:2181) and a folder name as arguments.
Example: $ java -jar zookeeper-dev-fatjar.jar server 2181 datadir
Here, server takes default system IP adress, 2181 is the port number and datadir is the folder name that will get created(else updated) whenever Zookeeper is run.

Client(for testing): head_client.jar
Next Run head_client.jar file, by providing Zookeeper IP address and Port as arguments and connect to the Zookeeper. 
Example: $ java -jar head_client.jar 192.168.43.91:2181
Here, 192.168.43.91:2181 is the Zookeeper IP address and Port number. 

Server: head_server.py
Clone the code as many times as you want into a new python file to create as many replicas in the chain. Run every Python server code with different Port numbers to successfully connect and interact in the Network.
NOTE:
 Open the Python program and edit the IP address to your system IP address,as mentioned in the comments inside the code.

In Command prompt type:
$ python head_server.py (zookeeperhost:  port) (any random unique 4 digit port number to create server)
Eg: $ python head_server.py 192.168.43.217:2181 2205

Now in the terinal where you have run the Client file:
Use inc (key) (val)    Eg: inc "test" 100
    del (key)          Eg: del "test" 
    get (key)          Eg: get "test"
to interact with head and tail in the Chain and get Results.
