# Chain-Replication-Using-Python-Kazoo.
Python Chain Replication Server that can perform the Head, Replica and Tail in the Chain. This server uses Kazoo to connect to the Zookeeper. 
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
Clone the code as many times as you want into a new python file to create as many replicas in the chain. Run every Python server code with different Port numbers to succesfully connect and interact in the Network.
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
