/* HDRJ.js
 *  javascript client for Hobo Delta Replication JSON.
 *
 * 
 */
 
  
function WebSocketLines(address) {
   /* Encapsulate a line-oriented WebSocket protocol.
    *
    * Example:
    *  First, run a websocket server. A quick way is:
    *  $ websockify -D 8081 --unix-target=/tmp/backendsocket
    *  $ nc -Ul /tmp/backendsocket
    *  Second, run this Javascript:
    *  l = new Lines("ws://localhost:8081/");
    *  l.on("line", function(line) {
    *    console.log("Received", line, "from", l.address());
    *  });
    */
      
   // WebSockets, despite essentially being TCP--a stream protocol--
   // only offer a packet-style API, probably because the usual stream APIs of write() and read() are intrinsically synchronous, which is impossible to use with javascript--
   // so to be safe we always need to do stream reconstruction whenever working with WebSockets.
   // see jsmpg for a more efficient implementation of reconstruction than this: https://github.com/phoboslab/jsmpeg/blob/master/jsmpg.js#L90
   
   
   // We need to do this reconstruction even though our use case
   // is line-oriented--a sort of packetization again!--
   // because we cannot guarantee that the server flushes its buffers at any particular time.
   // 
   // That means cannot at all expect one level of packet to fit into the boundaries of the other.
   
     var self = this; //js scoping rules mean that 'this' refers to the object the function, so the e.g. onmessage event handler gets the Changes 'this' stomped on
     
     this.ws = new WebSocket(address, "base64"); //we could also use 'binary' transfer mode, which changes some details below. we cannot use the plain mode because websockify denies it.
     this.buffer = "";
     
     this.address = function() { return this.ws.url; }
     
     this.ws.onmessage = function(evt) {
     // websockets
     // oh websockets..
     
       var payload = atob(evt.data); //extract from base64,
     
       // stream reconstruction
       self.buffer += payload;
     
       //then read out every complete line
       var lines = self.buffer.split("\n");
       // the *last* entry is the start of the next unfinished line;
       // if the last character in buffer was a newline then split will return an empty string
       // otherwise, a line got broken in the middle and we have the first half up to the break point
       // pop() without arguments eats the last entry
       self.buffer = lines.pop();
     
       lines.forEach(function(l) {
         self.trigger("line", l);
       })
     }
     
     this.ws.onerror = function(evt) { 
       //console.log("ws.error: ", evt);
       self.trigger("error", evt);
     }
     
     this.ws.onclose = function(evt) { 
       //console.log("ws.close: ", evt);
       self.trigger("close");
     }
   }
   _.extend(WebSocketLines.prototype, PourOver.Events, {
     close: function() {
       this.ws.close();
     }
   });
   

// Now that we can get changes out of postgres and into the web, we need somewhere to put them so that they can be rendered and interacted with.
// There are many ways to cache and query data in Javascript.
//  Using plain arrays containing objects (aka dictionaries) and writing manual scans is the oldest and probably most common;
//  Indeed, this is what the d3.csv() function provides and what, it seems, d3 expects.
//  There's a series of APIs, none ever yet fully implemented, for providing permanent storage for web pages; see http://diveintohtml5.info/storage.html
//  - DOM Storage
//  - LocalStorage
//  - WebSQL
//  - IndexedDB
// IndexedDB seems to be winning, and it's what PouchDB--which is an implementation of CouchDB right in javascript, adding foreign keys, replication and versioning--prefers to back itself with.
//   
// There are at least two libraries which do not spec storage but instead focus on queries:
//List all the in-JS DB options:
//  - crossfilter
//  - PourOver
// both of these do not provide Views.
//  PourOver is promising, but needs enhancements before it is usable for us.
//  It's initial design was to avoid doing round-trips--making the server a bottleneck to all the web clients--just to perform queries
// For example,
//   PourOver has something it calls a View, but they are not arranged to easily make multiples (the default implementation shares the same query--which it takes as the intersection of all defined filters--amongst all instances)
//   Also, PourOver's filters are like parameterized where statements, however they are quirky. makeExactFilter(dimension, [options]) demands that the possible options must be explicitly given. PourOver provides no way to make a filter corresponding to "select where dimension = $1" and no way to do "select unique(dimension)" which would at least make dealing with not knowing the options alright.
//   PourOver must be really good where you have a known data model and you just want to send lots of data and make it interactive.


// Whichever we go with, we should be watchful of the query patterns we use,
//  because--at least to some degree (be mindful of PourOver's point that hitting the server on every query is wasteful!)--
// The best in the long term would be to be able to treat the javascript database as a memoization cache; with items stored when asked for, with old items being evicted.

function HDRJPourOver(name, address) {  //this should be a mixin onto PourOver.Collection, or maybe it should be the ReplicatorProcess which sits and and you give a PourOver.Collection to at construction
     // XXX BEWARE: in the case that your dataset does not have primary keys on it, duplicate rows are legal, so if you get a message to remove a row you need to be careful to *only remove one*
   
     var self = this;
     
     self.name = name;
     self.collection = new PourOver.Collection([]);
     
     var feed = new WebSocketLines(address);
     self._feed = feed; //mostly for debugging
     
     feed.on("line", function(line) {
       delta = JSON.parse(line);
       
       // process the change
       // In (preliminary) HRDJ updates are simply a delete followed by an insert
       //  so we 
       // In the future, updates may be special cased to only send the changed elements.
       // In any event, seeing a "-" implies getting
       // For now, process deletes before inserts, in echo of the future code which will have to handle deletes and updates both by first scanning the table for the row to delete
       
       if(delta["-"]) {
         
         self.collection.removeItems(delta["-"]);
         // The way we handle  is madly inefficient; PourOver requires removed items to be the mutated items 
         // but the backend
         // So, we do one scan (.find()), and then once the item is found, internally PourOver does another scan, copying every item except the unfortunate soul into a new set
         var unfortunate_soul = _(self.collection.items).find(function(e) {
           e = _.clone(e);
           delete e.cid;
           return _.isEqual(e, delta["-"]);
         })
         
         if(unfortunate_soul) {
           self.collection.removeItems(unfortunate_soul);
         }
       }
       
       if(delta["+"]) {
         self.collection.addItems(delta["+"]);
       }
       
       self.trigger("update", delta);
     })
     
   }
   _.extend(HDRJPourOver.prototype, PourOver.Events, {
   });
   
   
function HRDJArray(address) {

}



