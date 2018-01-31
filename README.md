
## Introduction
coap.mqtt.lwm2m is a command-line tool for everyday work with coap,mqtt,or lwm2m.

## Installation
 npm install -g coap.mqtt.lwm2m

## Usage
The library provides six command lin application including coap client/server,mqtt broker/client,lwm2m client/server.
This applications can be used to simulate the behavior of one of the peers of the communication.

### CoAP server command line application

This application simulates the use of coap server.It just provides command to start the server.

 command reference

	start ['port'] ['host']

         Starts a new coap server listening in the 'port'
         
### CoAP client commandline application

This application simulates the use of coap client . It provides commands to get ,put ,observe,post,discover.

command reference

	get ['url']
       send a 'get' request and the request path is 'url'
	observe ['url']
       send a 'get' request to observe the client
	post ['url'] ['post'] ['value']
       send a post request and the payload is 'value',if the value start with '#',the payload is a json file from the 'value'.
	put ['url'] ['put'] ['value']
       send a put request and the payload is 'value',if the value start with '#',the payload is a json file from the 'value'.
	discover ['url']
       send a discover request to find resource from 'url'

### MQTT server commandline application
This application simulates the use of mqtt broker.

command reference
    
	addr ['host'] ['port']
         port and host the server to listen to
    backend ['port'] ['host'] ['prefix']
         set the parent broker's port ,host and the prefix to use
    disstats
         disable the publishing of stats under $SYS'
    id ['id]
        the id of the broker in the $SYS/<id> namespace
    secure ['securePort'] ['key'] ['cert'] ['nonSecure']
          'securePort': the TLS port to listen to,
          'key': the server's private key,
          'cert': the certificate issued to the server,
          'nonSecure': start both a secure and non-secure server
    http ['httpPort'] ['httpStatic'] ['httpBundle']
          'httpPort': start an mqtt-over-secure-websocket server on the specified port,
          'httpStatic': serve some static files alongside the secure websocket client,
          'httpBundle': serve a MQTT.js-based client at /mqtt.js on HTTPS'
    config ['path']
          the config file to use (override every other option)
    db ['path']
          the path where to store the database
    auth ['path']
          the file containing the auths
    start
        start a mqtt server
    close
        close the broker
    pub ['topic'] ['payload']['retain']['qos']
        Publishes a packet on the MQTT broker
    sub ['topic]
        Subscribes to a topic on the MQTT broker
    
