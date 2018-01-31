#!/usr/bin/env node
var mosca = require('mosca');
var path = require("path");
var fs = require("fs");
//var steed = require("steed")();
var clUtils=require('command-node');

var runned=false;
var server=null;
var auth = {
    "*":{ 
        password:"",
        subscribe: [ 
                "a_public_topic", "another_public_topic"
            ],
        publish: []
    }
};
var options = {
    backend: {},
    stats: true,
    persistence: {
        factory: mosca.persistence.Memory
    }
};
function setaddr(host,port){
    options.host=host;
    options.port=parseInt(port);
}
function setbackend(parentPort,parentHost,parentPrefix){
    if (parentPort||parentHost) {
      options.backend.type = "mqtt";
      options.backend.port = 1883;
    }

    if (parentHost) {
      options.backend.host = parentHost;
    }

    if (parentPort) {
      options.backend.port = parentPort;
    }
    options.backend.prefix = parentPrefix;
}
function disableStats(){
    options.stats=false;
}
function setid(id){
    options.id=id;
}
function setsecure(securePort,key,cert,nonSecure){
    options.secure = {};
    options.secure.port = securePort;
    options.secure.keyPath = key;
    options.secure.certPath = cert;
    options.allowNonSecure = nonSecure;
}
function sethttp(httpPort,httpStatic,httpBundle,onlyHttp){
      options.http = {
        port: httpPort,
        static: httpStatic,
        bundle: httpBundle
      };
      options.onlyHttp = onlyHttp;
}
function sethttps(httpPort,httpStatic,httpBundle){
    if(options.secure) {
        options.https = {
            port:   httpsPort,
            static: httpsStatic,
            bundle: httpsBundle
        };
    } 
    else{
        console.error("must set secure first")
    }  
}
function readconfig(path){
    var opts = require(path.resolve(path));
    Object.keys(options).forEach(function(key) {
        if(typeof opts[key] === 'undefined') {
            opts[key] = options[key];
        }
    }); 
    options=opts; 
}
function setdb(db){
    options.persistence.path = db;
    options.persistence.factory = mosca.persistence.LevelUp;  
}
function setauth(path){
    fs.readFile(path, 'utf8', function (err, data) {
    if (!err){
       auth = JSON.parse(data);
    }
});
}

var authenticate = function (client, username, password, callback) {
    var authorized = false;
    if(username === undefined && auth["*"] !== undefined){
       authorized = true;
    }else if(username !== undefined && password !== undefined){
       var pw = 
          crypto.createHash('md5').update(username).update(password.toString()).digest("hex");
       if(auth[username] !== undefined && auth[username].password == pw){
           client.user = username;
           authorized = true;
       }
    }
    callback(null,authorized);
}
/*
 * publish and subscribe permissions defined in auth.json
 */
var authorizeSubscribe = function (client, topic, callback) {
    var answer = false;
    if(auth["*"] !== undefined && auth["*"].subscribe.indexOf(topic)>=0){
       answer = true;
    }else if(client.user !== undefined && auth[client.user].subscribe.indexOf(topic)>=0){
          answer = true;
    }
    callback(null, answer);
}

var authorizePublish = function (client, topic, payload, callback) {
    var answer = false;
    if(auth["*"] !== undefined && auth["*"].publish.indexOf(topic)>=0){
       answer = true;
    }else if(client.user !== undefined && auth[client.user].publish.indexOf(topic)>=0){
          answer = true;
    }
    callback(null, answer, payload);
}
function setup() {
    server.authenticate = authenticate;
    server.authorizePublish = authorizePublish;
    server.authorizeSubscribe = authorizeSubscribe;
    
    console.log('Mosca server is up and running.');
}
function start(){
    server = new mosca.Server(options);
    server.on("error", function (err) {
        console.log(err);
    });

    server.on('clientConnected', function (client) {
        console.log('Client Connected \t:= ', client.id);
    });

    server.on('published', function (packet, client) {
        console.log("Published :=", packet);
    });

    server.on('subscribed', function (topic, client) {
        console.log("Subscribed :=", topic);
    });

    server.on('unsubscribed', function (topic, client) {
        console.log('unsubscribed := ', topic);
    });

    server.on('clientDisconnecting', function (client) {
        console.log('clientDisconnecting := ', client.id);
    });

    server.on('clientDisconnected', function (client) {
        console.log('Client Disconnected     := ', client.id);
    });
    server.on('ready', setup);
    // server.published = function(packet, client, cb) {


    //   server.publish(newPacket, cb);
    // }

}

function pubmsg(topic,payload,retain,qos,cb){
    var newPacket = {
        topic: 'echo/' + topic,
        payload: payload,
        retain: retain,
        qos: parseInt(qos)
      };
      server.publish(newPacket, cb);
}
function serverpub(commands){
    pubmsg(commands[0],commands[1],commands[2],commands[3],commands[4])
}
function serverclose(command){
    server.close();
}
function submsg(commands){
    server.subscribe(commands[0]);
}
function serveraddr(command){
    setaddr(command[0],command[1]);
}
function serverbackend(command){
    setbackend(command[0],command[1],command[2]);
}
function serverunstats(command){
    disableStats();
}
function serverid(command){
    setid(command[0]);
}
function serversecure(command){
    setsecure(command[0],command[1],command[2],command[3]);
}
function serverhttp(command){
    sethttp(command[0],command[1],command[2],command[3],command[4]);
}
function serverhttps(command){
    sethttps(command[0],command[1],command[2],command[3]);
}
function serverconfig(command){
    readconfig(command[0]);
}
function serverdb(command){
    setdb(command[0]);
}
function serverauth(command){
    setauth(command[0]);
}
function serverstart(command){
    start();
}
var commands={
    'start':{
        parameters:[],
        description:'\tStart mqtt server',
        handler:serverstart
    },
    'close':{
        parameters:[],
        description:'\tClose mqtt server',
        handler:serverclose 
    },
    'pub':{
        parameters:['topic','payload','retain','qos'],
        description:'\tPublishes a packet on the MQTT broker',
        handler:serverpub    
    },
    'sub':{
        parameters:['topic'],
        description:'\tSubscribes to a topic on the MQTT broker',
        handler:submsg   
    },
    'addr':{
        parameters:['host','port'],
        description:'\tthe port and the host to listen to',
        handler:serveraddr
    },
    'backend':{
        parameters:['port','host','prefix'],
        description:'\tthe parent port and parent host to connect to,the prefix to use in the parent broker',
        handler:serverbackend
    },
    'disstats':{
        parameters:[],
        description:'\tdisable the publishing of stats under $SYS',
        handler:serverunstats
    },
    'id':{
        parameters:['id'],
        description:'\tthe id of the broker in the $SYS/<id> namespace',
        handler:serverid
    },
    'secure':{
        parameters:['securePort','key','cert','nonSecure'],
        description:"\tthe TLS port to listen to,the server's private key,the certificate issued to the server,start both a secure and non-secure server",
        handler:serversecure  
    },
    'http':{
        parameters:['httpPort','httpStatic','httpBundle','onlyHttp'],
        description:'\tstart an mqtt-over-websocket server on the specified port,serve some static files alongside the websocket client,serve a MQTT.js-based client at /mqtt.js on HTTP,start only an mqtt-over-websocket server',
        handler:serverhttp  
    },
    'https':{
        parameters:['httpPort','httpStatic','httpBundle'],
        description:'\tstart an mqtt-over-secure-websocket server on the specified port,serve some static files alongside the secure websocket client,serve a MQTT.js-based client at /mqtt.js on HTTPS',
        handler:serverhttps  
    },
    'config':{
        parameters:['path'],
        description:'\tthe config file to use (override every other option)',
        handler:serverconfig  
    },
    'db':{
        parameters:['path'],
        description:'\tthe path were to store the database',
        handler:serverdb  
    },
    'auth':{
        parameters:['path'],
        description:'\tthe file containing the auths',
        handler:serverauth  
    }

};
clUtils.initialize(commands,'MQTT-Server> ');