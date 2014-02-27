pubsub.ws
=========

Pubsub should be drastically simplified so that a "topic" should be WebSocket URL.
Then "subscribing" is just connecting to that URL, and "publishing"is .send()ing to it.

Since this makes nothing that WebSocket doesn't already do, the implementation can be handled entirely server side.
The one tip to "pubsub"iness might be that if you hit the websocket address over http, it gives a note.

Examples
========

A simple server feed:
```
temperature_subscription = WebSocket("ws://example.com/feeds/sensors/temperature")
temperature_subscription.onmessage = function(evt) {
  console.log("Temp is ", evt.data['t'])

```


A simple room:
```
channel = WebSocket("ws://example.com/chatrooms/ireland/")
channel.send({nickname: "McSkills"+Math.floor(Math.random()*222)})
channel.onmessage = function(evt) {
   $("#chatwindow").append("li").content(evt.data['nickname'] + ": " + evt.data['message'])
}
inputbox = $("#inputbox")
inputbox.click(function() { 
  channel.send(inputbox.content)
  inputbox.content = null;
})
```
