-  
# coap.mqtt.lwm2m.client
command line tool writted in python
## the usage
coap-client [-h] [--non] [-m METHOD] [--observe] [--observe-exec CMD]
                   [--accept MIME] [--proxy HOST[:PORT]] [--payload X]
                   [--content-format MIME] [-v] [-q] [--dump FILE]
                   [--interactive] [--credentials CREDENTIALS]

- --non, Send request as non-confirmable (NON) message
- --method, Name or number of request method to use ,the default is "GET"
- --observe, Register an observation on the resource
- --observe-exec,Run the specified program whenever the observed resource changes, feeding the response data to its stdin
- --accept, Content format to request
- --proxy, Relay the CoAP request to a proxy for execution
- --payload, Send X as payload in POST or PUT requests. If X starts with an '@', its remainder is treated as a file name and read from.
- --content-format, Content format sent via POST or PUT
- -v, --verbose, Increase the debug output
- -q, --quiet, Decrease the debug output
- --dump,Log network traffic to FILE
- --interactive, Enter interactive mode # careful: picked before parsing
- --credentials, Load credentials to use from a given file
- url,CoAP address to fetch
    
    
mqtt-client [-h] [-d DEBUG] [-a HOST] [-i ID] [-k KEEPALIVE] [-p PORT]
                   [-u USERNAME] [-P PASSWORD] [-t TOPIC] [--payload] [--qos]

lwm2m-client [-n endpointname] [-c createobj] [-s setobjvalue] [-r run/register]
