# ionman
This is a demonstration of how Crossbar can be used as a web development framework for writing performance true Single Page Applications (SPA's) over websockets. HTTP is used to load the "first" page and some static content (CSS etc) , but essentially all web pages are subsequently served over websockets.

After loading the initial page, JS/CSS/Websockets are all persistent across further page transitions, you will note how quickly page transitions happen and how smooth the UI update is. A page transition happens over an OPEN websocket connection!!

###Anatomy of the framework

Crossbar inherrently lends itself to microservices based development, which is the vein in which this example is intended. There are three main components here;

* The message router (crossbar)  [.crossbar and ionman]
* The demo microservice [microservices/demo]
* The client / front-end code [static]
 
###Prerequisites

You will need Crossbar and all associated components, and in addition MongoDB and pymongo. (v3 is recommended) 

####Making it 'do' something

First you will need to check the repo out into a folder and import some default authentication records into your Mongo database, this should be possible with;
```bash
mongo < contrib/default_records.mongo
```
To get going you will need to do the following;

* Start crossbar, you can do this with the supplied shell script, note that the supplied example is pre-configured to run over SSL and comes with some dummy certificates;
```bash
$ ./start.sh 
2015-11-23T11:32:32+0000 [Controller  30655] Automatically choosing optimal Twisted reactor
2015-11-23T11:32:32+0000 [Controller  30655] Running on Linux and optimal reactor (epoll) was installed.
2015-11-23T11:32:32+0000 [Controller  30655]      __  __  __  __  __  __      __     __
2015-11-23T11:32:32+0000 [Controller  30655]     /  `|__)/  \/__`/__`|__) /\ |__)  |/  \
2015-11-23T11:32:32+0000 [Controller  30655]     \__,|  \\__/.__/.__/|__)/~~\|  \. |\__/
2015-11-23T11:32:32+0000 [Controller  30655]                                         
2015-11-23T11:32:32+0000 [Controller  30655]     Version: 0.11.1     
2015-11-23T11:32:32+0000 [Controller  30655] 
2015-11-23T11:32:32+0000 [Controller  30655] Starting from node directory /home/gareth/GitHub/ionman/.crossbar
2015-11-23T11:32:32+0000 [Controller  30655] Loading node configuration file '/home/gareth/GitHub/ionman/.crossbar/config.json'
2015-11-23T11:32:32+0000 [Controller  30655] Entering reactor event loop...
2015-11-23T11:32:32+0000 [Controller  30655] Joined realm 'crossbar' on node management router
2015-11-23T11:32:32+0000 [Controller  30655] No WAMPlets detected in enviroment.
2015-11-23T11:32:32+0000 [Controller  30655] Starting Router with ID 'worker1'...
2015-11-23T11:32:32+0000 [Router      30666] Worker running under CPython-EPollReactor
2015-11-23T11:32:33+0000 [Controller  30655] Router with ID 'worker1' and PID 30666 started
2015-11-23T11:32:33+0000 [Controller  30655] Router 'worker1': realm 'realm1' (named 'ionman') started
2015-11-23T11:32:33+0000 [Controller  30655] Router 'worker1': role 'role1' (named 'anonymous') started on realm 'realm1'
2015-11-23T11:32:33+0000 [Controller  30655] Router 'worker1': role 'role2' (named 'client') started on realm 'realm1'
2015-11-23T11:32:33+0000 [Controller  30655] Router 'worker1': role 'role3' (named 'authenticator') started on realm 'realm1'
2015-11-23T11:32:33+0000 [Controller  30655] Router 'worker1': role 'role4' (named 'server') started on realm 'realm1'
2015-11-23T11:32:33+0000 [Controller  30655] Router 'worker1': component 'component1' started
2015-11-23T11:32:33+0000 [Router      30666] Using default cipher list.
2015-11-23T11:32:33+0000 [Router      30666] OpenSSL DH modes not active - missing DH param file
2015-11-23T11:32:33+0000 [Router      30666] Ok, OpenSSL is using ECDH elliptic curve prime256v1
2015-11-23T11:32:33+0000 [Router      30666] Site (TLS) starting on 8443
2015-11-23T11:32:33+0000 [Controller  30655] Router 'worker1': transport 'transport1' started
```
* Next you will need to start a new terminal and go to the 'demo' microservice, which provides the routine used to render pages, if you change into *microservices/demo* you can then run it up with;
```bash
$ ./server.py foreground
2015-11-23 11:34:27+0000 [-] Log opened.
2015-11-23 11:34:27+0000 [-] Server> wss://localhost:8443/ws
2015-11-23 11:34:27+0000 [-] Starting factory <ionman.ComponentFactory object at 0x7f8fdb1a4150>
2015-11-23 11:34:27+0000 [WampWebSocketClientProtocol (TLSMemoryBIOProtocol),client] > connected to router
2015-11-23 11:34:27+0000 [WampWebSocketClientProtocol (TLSMemoryBIOProtocol),client] > dealing with [wampcra] challenge
2015-11-23 11:34:27+0000 [WampWebSocketClientProtocol (TLSMemoryBIOProtocol),client] > (demo) joined (ionman) [server] - 7190206942254795
2015-11-23 11:34:27+0000 [WampWebSocketClientProtocol (TLSMemoryBIOProtocol),client] > adding subscription @@ <demo.Subscriptions instance at 0x7f8fdb4127a0>
2015-11-23 11:34:27+0000 [WampWebSocketClientProtocol (TLSMemoryBIOProtocol),client] > adding registration @@ <demo.Registrations instance at 0x7f8fdb412ef0>
2015-11-23 11:34:27+0000 [WampWebSocketClientProtocol (TLSMemoryBIOProtocol),client] > initialting callback loop
```
You should see crossbar register the login (in your first window) with something like this;
```bash
2015-11-23T11:36:13+0000 [Router      30666] 1266989505295769> Authenticate (demo)
2015-11-23T11:36:13+0000 [Router      30666] onAuthenticate: X8Lda5BvxUjf3ZJ+zUVj6O9WXy626XvIz7Y9pQO14vE= {}
2015-11-23T11:36:13+0000 [Router      30666] 1266989505295769> Join (demo) as (server)
```
Now you should be ready to roll, crossbar should be serving pages on port 8443 using https, so if you point your browser at https://localhost:8443/ you should see the front page. Initially you will see "Sign In" in the top right hand corner and each page will welcome you as "guest". If you click on the "Sign In" button and sign in as "user@user" password "user", this will change.

![Screenshot of welcome page](https://github.com/oddjobz/ionman/blob/master/contrib/demo.png)

###The extra mile ...

To run this on a server with automatic starts, firstly you will need to make Crossbar run automatically, I would recommend using 'svs' which is well documented on the Crossbar site. The services ends up being started via rc.local using *svscanboot*, this sounds a little hacky but it works well.

To start microservices, you will need a startup script for each, jus the one in this instance. There is a demonstration script in the contrib folder which should work with minimal modification for most users. (it just depends on where in your filesystem you want to load the code) Essentially it runs the 'server.py' code from the microservice using "twistd", which is the standard launcher for "twisted" applications. (which is what Crossbar 'sits' on) If you run a microservice with "foreground" after it, then you get the easy-to-read debug, if you drop the 'foreground' then it expects to be run via 'twistd', which handles loggind, pid files etc etc ..
(and the sample start/stop calls twistd for you)

Note; you.do.not.need.a.web.server. Crossbar *is* a webserver, and yes, generally it IS fast enough in Python! :)

This should get you a complete set of dependencis (Ubuntu 15.10);
```bash
echo "deb http://repo.mongodb.org/apt/debian wheezy/mongodb-org/3.0 main" > /etc/apt/sources.list.d/mongodb-org-3.0.list 
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
apt-get update
useradd -m ionman
apt-get install git csh daemontools daemontools-run
apt-get install apt-get install build-essential libssl-dev python-pip pypy pypy-dev
apt-get install build-essential libssl-dev python-pip pypy pypy-dev libffi-dev
apt-get install python-pip python-dev mongodb-org python-pymongo
pip2 install crossbar
git clone https://github.com/oddjobz/ionman.git
mkdir /var/log/crossbar/
chown ionman:ionman /var/log/crossbar
```
And you may want to add;
```python
import sys
sys.setdefaultencoding('utf-8')
```
To beginning of; /usr/lib/python2.7/sitecustomize.py

