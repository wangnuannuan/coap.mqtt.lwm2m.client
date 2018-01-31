#!/usr/bin/env node
var mqtt =require('mqtt');
var path=require('path');
var fs=require('fs');
var clUtils = require('command-node');
//var Writable = require('readable-stream').Writable;

var options={host: 'localhost',qos: 0,retain: false,topic: '', message: ''};

function setkey(key){
	options.key=fs.readFileSync(key);
}
function setcert(cert){
	options.cert=fs.readFileSync(cert);
}
function setca(ca){
	options.ca=fs.readFileSync(ca);
}
function setprotocol(){
	if (options.key && option.cert&& !options.protocol){
		options.protocol='mqtts'
	}
}
function setport(option){
	if (typeof option !=='number'){
		console.warn('# Port: number expected, \'%s\' was given.', typeof option);
		return;
	}
	else{
		options.port=option;
	}
}
function sethost(host){
	options.host=host;
}
function setwill(topic,message,qos,retaion){
	options.will={};
	options.will.topic=topic;
	options.will.payload=message;
	options.will.qos=qos;
	options.will.retain=retaion;
}
function setsecure(insecure){
	if(insecure){
		options.rejectUnauthorized = false
	}
}

function setmessage(topic,message){
	options.topic=topic;
	options.message=message;
}

function sendpub(topic,message){
	var client = mqtt.connect(options);
    client.on('connect', function () {
    client.publish(topic,message, options, function (err) {
      if (err) {
        console.warn(err)
      }
      client.end()
    });
  });
  client.on('error', function (err) {
    console.warn(err)
    client.end()
  });
}
function setuser(username,password){
	options.username=username;
	options.password=password;
}
function setalive(time){
	option.keepAlive=time;
}
function sub(topic,qos){
	var client =mqtt.connect(options);
  	client.on('connect', function () {
	    client.subscribe(topic, { qos: qos }, function (err, result) {
	      	if (err) {
	        	console.error(err);
	     	}

	      	result.forEach(function (sub) {
	        	if (sub.qos > 2) {
	          		console.error('subscription negated to', sub.topic, 'with code', sub.qos)
	        	}
	      	})
	    });
  	});
  	client.on('message', function (topic, payload) {
      	console.log("Receive message: ",payload.toString())
  	});
    client.on('error', function (err) {
    	console.warn(err)
    	client.end()
  	});
}
function secure(commands){
	setkey(commands[0]);
	setcert(commands[1]);
	setsecure(commands[3]);
}
function clientpro(commands){
	setprotocol(commands[0]);
}
function clientca(commands){
	setca(commands[0]);
}
function clientaddr(commands){
	sethost(commands[0]);
	setport(commands[1]);
}
function clientwill(commands){
	setwill(commands[0],commands[1],commands[2],commands[3]);
}
function clientmsg(commands){
	if (commands[1][0]=='#'){
		path=commands[1].replace('#','');
		commands[1]=JSON.parse(fs.readFileSync(path));
	}
	setmessage(commands[0],JSON.stringify(commands[1]));
}
function clientalive(commands){
	setalive(commands[0]);
}
function clientuser(commands){
	setuser(commands[0],commands[1]);
}
function clientpub(commands){
	if (commands[1][0]=='#'){
		path=commands[1].replace('#','');
		commands[1]=JSON.parse(fs.readFileSync(path));
	}
	sendpub(commands[0],JSON.stringify(commands[1]));
}
function clientsub(commands){
	sub(commands[0],commands[1]);
}
var commands={
	'secure':{
		parameters:['key'],
		description:'\tpath to the secure file',
		handler:secure
	},
	'protocol':{
		parameters:[],
		description:'\tthe protocol to use, mqtt,mqtts, ws or wss',
		handler:clientpro
	},
	'ca':{
		parameters:['path'],
		description:'\tpath to the ca certificate',
		handler:clientca
	},
	'addr':{
		parameters:['host','port'],
		description:'\tthe broker host and port',
		handler:clientaddr
	},
	'will':{
		parameters:['will-topic','will-payload','will-qos','will-retain'],
		description:'\tthe will topic,the will message,the will qos,send a will retained message',
		handler:clientwill
	},
	'msg':{
		parameters:['topic','message'],
		description:'\tthe message topic and the message body',
		handler:clientmsg
	},
	'alive':{
		parameters:['time'],
		description:'\tsend a ping every XXX seconds',
		handler:clientalive
	},
	'user':{
		parameters:['username','password'],
		description:'\tthe username and password',
		handler:clientuser		
	},
	'pub':{
		parameters:['topic','message'],
		description:'\tmqtt publish [opts] topic [message]',
		handler:clientpub	
	},
	'sub':{
		parameters:['topic','qos'],
		description:'\tUsage: mqtt subscribe [opts] [topic]',
		handler:clientsub
	}
}
clUtils.initialize(commands,'MQTT-Client> ');