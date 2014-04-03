var http = require('http'),
    path = require('path'),
    fs = require('fs'),
    request = require('request')
    
var MODEL_SERVER = 'http://localhost:5000';

function get_root() {
    /*
     * Returns the root directory for modex.
     * */
    var launch_dir = __dirname;
    var directory_names = __dirname.split('/').slice(0, -2);
    return directory_names.join('/');
}

var PROJECT_ROOT = get_root();

var server = http.createServer(function (req, res) {
    var SERVEDIR = path.join(PROJECT_ROOT, 'src', 'frontend');
    var SERVEURL = SERVEDIR;
    var SPLITURL = req.url.split('/')
    var TOPDIR = SPLITURL[1];
    var FILE = SPLITURL[SPLITURL.length - 1];

    if(TOPDIR == 'assets') {
        SERVEURL = PROJECT_ROOT  + req.url; // overrides and goes to /assets since that's req.url
    }
    
    else if(req.url == '/') {
        SERVEURL = SERVEDIR + '/index.html';
    }
    
    else {
        SERVEURL = SERVEDIR + req.url;
    }
    
    fs.readFile(SERVEURL, function (err,data) {
    if (err) {
      res.writeHead(404);
      res.end(JSON.stringify(err));
      return;
    }
    res.writeHead(200);
    res.end(data);
  });
})

// has to be defined in this order otherwise it screws things up
var io = require('socket.io').listen(server);
server.listen(8080);

io.sockets.on('connection', function (socket) {
    console.log("New socket connection from client!");
    socket.on('game_state', function(state) {
        //determines if game is running or not.
        console.log(state);
        request.post(MODEL_SERVER, {form:{message_type:'game_state', game_state: state}});
    });
    socket.on('send_intervention', function(intervention) {
       request.post(MODEL_SERVER, {form:{message_type:'add_intervention', tax_value: intervention.tax_value, 
           activity: intervention.activity, year: intervention.year}});
    });
    socket.on('send_data', function (data) { 
        // this handles the data sent from the model.
        console.log(data);
    })
    socket.on('disconnect', function () { });
});


var model_listener = http.createServer(function (req, res) {
    // This server listener listens to the data from the client.
     // excuse the dirty hack, will fix later.
    req.on('data', function(data) {
        model_data = {}
        data_items = data.toString().split("&"); // separates parameters
        
        for(var i=0; i<data_items.length; i++) {
            split_items = data_items[i].split("=")
            model_data[split_items[0]] = parseInt(split_items[1])
        }
        console.log(model_data);

    });
    res.writeHead(200);
    res.end("finito");
})
model_listener.listen(9080);
