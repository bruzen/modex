#!/usr/bin/python2
# the main server code
# make sure to read src/backend/README.md if this confuses you.

import sys
from os.path import dirname, abspath, join as pathjoin

#'working directory': not the system working directory, but the directory this program is in (so that we can be run from anywhere and find the correct assets/ folder et al.)
PROJECT_ROOT = dirname(dirname(dirname(abspath(__file__)))) #currently, the project root is two levels up from the directory the server is

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

# autobahn changed their API between (which happens to be within the last month of so as of this commit)
# they added asyncio (which is py3.4-native) as an alternate option to twisted (which is py2-native),
# and hence moved moved classes from autobahn.* to autobahn.twisted.*
# evidence:
#  https://raw.github.com/tavendo/AutobahnPython/v0.7.0/examples/twisted/websocket/echo/server.py
#   ~~ the change happened here, now  ~~
#  https://raw.github.com/tavendo/AutobahnPython/v0.6.5/examples/websocket/echo/server.py
#  https://raw.github.com/tavendo/AutobahnPython/v0.6.4/examples/websocket/echo/server.py
#  https://raw.github.com/tavendo/AutobahnPython/v0.5.14/examples/websocket/echo/server.py
#  https://raw.github.com/tavendo/AutobahnPython/e1dae070e67a9361f14beba775c66961e06d43ff/demo/echo/echo_server.py

from autobahn.twisted.websocket import WebSocketServerFactory, WampWebSocketServerFactory, WebSocketServerProtocol, WampWebSocketServerProtocol
from autobahn.twisted.resource import * #WebSocketResource, HTTPChannelHixie76Aware


import json

# we are trying to set up a producer-consumer system, and twisted has this built in:
# https://twistedmatrix.com/documents/12.2.0/core/howto/producers.html
# ah, simpler: reactor.callLater

# TODO(kousu): set up WAMP and use it to push messages instead of using a 'raw' websocket


import csv

from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep


from models.eutopia.eutopia import Eutopia

    
#TODO(kousu): move this out to scratch/ for reference on how to host a web socket server using AutobahnPython
class CtlProtocol(WebSocketServerProtocol):
   def onConnect(self, request):
      print("Client connecting: {}".format(request.peer))

   def onOpen(self):
      print("WebSocket connection open.")
      
   def onMessage(self, payload, isBinary):
      if isBinary:
         print("Binary message received: {} bytes".format(len(payload)))
      else:
         print("Text message received: |{}|".format(payload.decode('utf8')))

      #self.sendMessage(json.dumps(data), isBinary)

   def onClose(self, wasClean, code, reason):
      print("WebSocket connection closed: {}".format(reason))
   


class ModelDataServer(WebSocketServerProtocol):
   def onConnect(self, request):
      print("Client connecting: {}".format(request.peer))

   def onOpen(self):
      print("WebSocket connection open.")
      
      #I want to speak dynamically: so, as data comes in, push it to the client
      # but I don't see how to do this?? what thread am I running on???
      # ah!
      dat = pathjoin(PROJECT_ROOT, "assets", "data", "static_lightbulbs.tsv")
      dat = open(dat)
      dat = csv.reader(dat, dialect=csv.excel_tab)
      header = next(dat)
      print("read header:", header)
      
      # this could probably be cleaner
      def feed():  #a coroutine, meant to be pumped by the twisted event loop
        for row in dat:
          J = dict(zip(header, row))
          print "pushing", J, "to the client"
          self.sendMessage(json.dumps(J))
          yield
      g = feed()
      
      def loop():  #wrap the coroutine in a callback that causes a loop setTimeout()-style playing nice with Twisted's loop (there's probably a cleaner way to do this, but shh)
        try:
          next(g)
          reactor.callLater(.3, loop)
        except StopIteration:
          pass
      loop()  #kick it off

   def onMessage(self, payload, isBinary):
      if isBinary:
         print("Binary message received: {} bytes".format(len(payload)))
      else:
         print("Text message received: |{}|".format(payload.decode('utf8')))

      #self.sendMessage(json.dumps(data), isBinary)

   def onClose(self, wasClean, code, reason):
      print("WebSocket connection closed: {}".format(reason))
      

if __name__ == '__main__':

   if len(sys.argv) > 1 and sys.argv[1] == 'debug':
      log.startLogging(sys.stdout)
      debug = True
   else:
      debug = False
   
   if debug:
     print "Starting server in", PROJECT_ROOT
   
   model = Eutopia([]) #the [] becomes model.log
   
   data_endpoint = WebSocketServerFactory("ws://localhost:8080",
                                    debug = debug,
                                    debugCodePaths = True)
   data_endpoint.protocol = ModelDataServer
   data_endpoint.model = model
   #data_endpoint.setProtocolOptions(allowHixie76 = True) # needed if Hixie76 is to be supported   
   
   ctl_endpoint = WebSocketServerFactory("ws://localhost:8080",
                                    debug = debug,
                                    debugCodePaths = True)
   ctl_endpoint.protocol = CtlProtocol
      
   webroot = pathjoin(PROJECT_ROOT,"src","frontend")
   assets = pathjoin(PROJECT_ROOT,"assets")
   if debug:
     print "putting", webroot,"at root"
     print "putting", assets,"at assets"
   
   ## we serve static files (most of the frontend html, js, and css) under "/" ..
   ## except for some which are under assets/
   ## and we have our WebSocket server under "/ws"
   root = File(webroot)
   assets = File(assets)
   data_resource = WebSocketResource(data_endpoint)
   ctl_resource = WebSocketResource(ctl_endpoint)
   
   root.putChild("assets", assets)  #TODO: do we prefer to have each entry in assets/ sit at the root (ie http://simulation.tld/data/ instead of http://simulation.tld/assets/data/)   
   root.putChild("ws", data_resource)    #this puts the websocket at /ws. You cannot put both the site and the websocket at the same endpoint; whichever comes last wins, in Twisted
   if debug:
     root.putChild("scratch", File(pathjoin(PROJECT_ROOT,"scratch")))
   root.putChild("ctl", ctl_resource) #this whole file is so not pythonic. Where's the D.R.Y. at, yo? --kousu
   
   #. <- /
   #./scratch <- /scratch
   #websocket <- /ws #random demo socket
   #websocket <- /ctl
   #RESTful ??
   
   ## both under one Twisted Web Site
   site = Site(root)
   #site.protocol = HTTPChannelHixie76Aware #  needed if Hixie76 is to be supported
   reactor.listenTCP(8080, site)

   print "Now open http://127.0.0.1:8080 in your browser"
   reactor.run()

