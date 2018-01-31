#!/usr/bin/env node
const coap =require('coap');
var Url=require('url');
var clUtils = require('command-node');
var config = require('./config');
var Readable = require('stream').Readable;
var options={},host,hostname,port,method,confirmable,
observe,pathname,query,options,headers,agent,
proxyUri,multicast,multicastTimeout,retrySend;
var fs=require('fs');
function setaccept(option){
	myoptions["Accept"]=option;
}
function setformat(option){
	myoptions["Content-Format"]=option;
}
function setproxy(option){
	req["Proxy-Uri"]=option;
}
function sendget(url,observe){
 	var path=Url.parse(url);
 	if (path.port==null){
 		path.port=5683;
 	}
    var request = {
        host: path.hostname,
        port: path.port,
        method: 'GET',
        pathname: path.pathname
    };
 	if (observe){
 		request.observe=true
 	}	
    if (options) {
    	for (option in options) {
      		if (options.hasOwnProperty(option)) {
        		request.setOption(option, options[option])
        	}
    	}
  	}
  	sendRequest(request);

}
function senddelete(url){
 	var path=Url.parse(url);
 	if (path.port==null){
 		path.port=5683;
 	}
    var request = {
        host: path.hostname,
        port: path.port,
        method: 'DELETE',
        pathname: path.pathname
    };

  	sendRequest(request);	
}
function sendvalue(url,method,value){
 	var path=Url.parse(url);
 	if (path.port==null){
 		path.port=5683;
 	}
    var request = {
        host: path.hostname,
        port: path.port,
        method: method,
        pathname: path.pathname,
        payload: value,
        options: {
            'Content-Format': config.coapserver.writeFormat
        }
    };	
    if (options) {
    	for (option in options) {
      		if (options.hasOwnProperty(option)) {
        		request.setOption(option, options[option])
        	}
    	}
  	}

  	sendRequest(request);
}
function senddiscover(url){
	var path=Url.parse(url);
 	if (path.port==null){
 		path.port=5683;
 	}
    var request = {
        host: path.hostname,
        port: path.port,
        method: 'GET',
        pathname: path.pathname,
        options: {
            'Accept': 'application/link-format'
        }
    };
    if (options) {
    	for (option in options) {
      		if (options.hasOwnProperty(option)) {
        		request.setOption(option, options[option])
        	}
    	}
  	}
  	sendRequest(request);
}
function sendRequest(request, callback) {
    var agent = new coap.Agent({type:config.coapserver.serverProtocol}),
        req = agent.request(request),
        rs = new Readable();

    req.on('response', function(res) {
        if (isObserveAction(res)) {
            res.pipe(process.stdout)
        } else {
            readResponse(res, callback);
        }
    });

    req.on('error', function(error) {
        callback(new errors.ClientConnectionError(error));
    });

    if (request.payload) {
        rs.push(request.payload);
        rs.push(null);
        rs.pipe(req);
    } else {
        req.end();
    }
}

function isObserveAction(res) {
    var observeFlag = false;

    for (var i = 0; i < res.options.length; i++) {
        if (res.options[i].name === 'Observe') {
            observeFlag = true;
        }
    }
    return observeFlag;
}
function readResponse(res, callback) {
    var data = '';

    res.on('data', function (chunk) {
        data += chunk;
    });

    res.on('error', function(error) {
        callback(new errors.ClientResponseError(error));
    });

    res.on('end', function(chunk) {
        if (chunk) {
            data += chunk;
        }
        console.log("response data ",data)
    });
}
function getreq(command){
	sendget(command[0],0);
}
function observereq(command){
	sendget(command[0],1);
}
function putpost(command){
	var value;
	var path;
	if (command[2][0]=='#'){
		path=command[2].replace('#','');
		command[2]=JSON.parse(fs.readFileSync(path))
	}
	console.log(command[2])
    console.log(JSON.stringify(command[2]))
	console.log(command[1].toUpperCase())
	sendvalue(command[0],command[1].toUpperCase(),JSON.stringify(command[2]));
}
function discoverreq(command){
	senddiscover(command[0]);
}
commands={
	'get':{
		parameters:['url'],
		description:'\tCoap client get ',
		handler:getreq
	},
	'observe':{
		parameters:['url'],
		description:'\tCoap client observe ',
		handler:observereq
	},
	'post':{
		parameters:['url','method','value'],
		description:'\tCoap client post ',
		handler:putpost
	},
	'put':{
		parameters:['url','method','value'],
		description:'\tCoap client put ',
		handler:putpost
	},
	'discover':{
		parameters:['url'],
		description:'\tCoap client discover ',
		handler:discoverreq
	}
}
clUtils.initialize(commands, 'CoAP-Client> ');