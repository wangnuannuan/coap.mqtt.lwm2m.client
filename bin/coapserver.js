#!/usr/bin/env node
var config = require('./config');
var clUtils = require('command-node');
var coap =require('coap');
var server =coap.createServer({type:config.coapserver.serverProtocol});
var port=5683;
var address="localhost";
registry={}
id=0;

function startserver(port,address,handleMessage){
	port=port;
	address=address;
	server.listen(port,address,function(){
		console.log('CoAP:start');
	})
	server.on('request',handleMessage)
}
function handleMessage(req,res){

	var method  = req.method.toString()
	var url     = req.url.toString()
	var value   = req.payload.toString()
	
	console.log('\nRequest received:')
	console.log('\t method:  ' + method)
	console.log('\t url:     ' + url)
	console.log('\t payload: ' + value)
	console.log('\t option: ',req.options)
	//registry[id++]=req;
	res.end('Received.')
}
function show(){
	clUtils.prompt();
}
function start(commands){
	console.log('coap server start')
	startserver(commands[0],commands[1],handleMessage);
	
}

var commands={
	'start':{
		parameters:['port','address'],
		description:'\tStart coap server',
		handler:start
	},
	'show':{
		parameters:[],
		description:'\tList all the client message',
		handler:show
	}
};
clUtils.initialize(commands, 'CoAP-Server> ');
