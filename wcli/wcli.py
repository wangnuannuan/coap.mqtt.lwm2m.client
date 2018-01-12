import socket
import sys
import argparse
import os
import subprocess
from pathlib import Path
# from coapthon.client.helperclient import HelperClient
# from coapthon.utils import parse_uri
import paho.mqtt.client as mqttclient
import paho.mqtt.publish as publish

import logging
import asyncio
from aiocoap import *
import lwm2mclient.lwm2mclient as lwm2mclient
import errno
import traceback
# coap_base_url='coap://'
logging.basicConfig(level=logging.DEBUG,format='%(levelname)s %(message)s') 
logger = logging.getLogger("myclient")
verbose = False
very_verbose = False
ver='1.0.0'


def coap_incoming_observation(observe_exec, response):
    if observe_exec:
        p = subprocess.Popen(observe_exec, shell=True, stdin=subprocess.PIPE)
        # FIXME this blocks
        p.communicate(response.payload)
    else:
        sys.stdout.buffer.write(b'---\n')
        if response.code.is_successful():
            sys.stdout.buffer.write(response.payload + (b'\n' if not response.payload.endswith(b'\n') else b''))
            sys.stdout.buffer.flush()
        else:
            print(response.code, file=sys.stderr)
            if response.payload:
                print(response.payload.decode('utf-8'), file=sys.stderr)

def coap_apply_credentials(context, credentials):
    if credentials.suffix == '.json':
        import json
        context.client_credentials.load_from_dict(json.load(credentials.open('rb')))
    else:
        print("Unknown suffix: %s (expected: .json)" % (credentials.suffix))

async def coap_single_request(method='GET',non=None,payload=None,url='localhost',observe=False,accept=None,proxy=None,
	credentials=None,dump=None,content_format=None,context=None):

    try:
        code = getattr(numbers.codes.Code,method.upper())
    except AttributeError:
        try:
            code = numbers.codes.Code(int(method))
        except ValueError:
            print("Unknown method")

    if context is None:
        context = await Context.create_client_context(dump_to=dump)
    else:
        if dump:
            print("The --dump option is not implemented in interactive mode.", file=sys.stderr)

    if credentials is not None:
        coap_apply_credentials(context, credentials)

    request = Message(code=code, mtype=NON if non else CON)
    try:
        request.set_request_uri(url)
    except ValueError as e:
        logger.error(e[0])

    if not request.opt.uri_host and not request.unresolved_remote:
        print("Request URLs need to be absolute.")

    if accept:
        try:
            request.opt.accept = int(accept)
        except ValueError:
            try:
                request.opt.accept = numbers.media_types_rev[accept]
            except KeyError:
                print("Unknown accept type")

    if observe:
        request.opt.observe = 0
        observation_is_over = asyncio.Future()

    if payload:
        if payload.startswith('@'):
            try:
                request.payload = open(payload[1:], 'rb').read()
            except OSError as e:
                print("File could not be opened: %s"%e)
        else:
            request.payload = payload.encode('utf8')

    if content_format:
        try:
            request.opt.content_format = int(content_format)
        except ValueError:
            try:
                request.opt.content_format = numbers.media_types_rev[content_format]
            except KeyError:
                print("Unknown content format")


    if proxy is None:
        interface = context
    else:
        interface = proxy.client.ProxyForwarder(proxy, context)

    try:
        requester = interface.request(request)

        if observe:
            requester.observation.register_errback(observation_is_over.set_result)
            requester.observation.register_callback(lambda data, observe_exec=observe_exec: coap_incoming_observation(observe_exec, data))

        try:
            response_data = await requester.response
        except socket.gaierror as  e:
            print("Name resolution error:", e, file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            print("Error:", e, file=sys.stderr)
            sys.exit(1)

        if response_data.code.is_successful():
            sys.stdout.buffer.write(response_data.payload)
            sys.stdout.buffer.flush()
            if response_data.payload and not response_data.payload.endswith(b'\n'): # and not options.quiet:
                sys.stderr.write('\n(No newline at end of message)\n')
        else:
            print(response_data.code, file=sys.stderr)
            if response_data.payload:
                print(response_data.payload.decode('utf-8'), file=sys.stderr)
            sys.exit(1)

        if observe:
            exit_reason = await observation_is_over
            print("Observation is over: %r"%(exit_reason,), file=sys.stderr)
    finally:
        if not requester.response.done():
            requester.response.cancel()
        if options.observe and not requester.observation.cancelled:
            requester.observation.cancel()

async def coap_interactive():
    global interactive_expecting_keyboard_interrupt

    context = await Context.create_client_context()

    while True:
        try:
            # when http://bugs.python.org/issue22412 is resolved, use that instead
            line = await asyncio.get_event_loop().run_in_executor(None, lambda: input("aiocoap> "))
        except EOFError:
            line = "exit"
        line = shlex.split(line)
        if not line:
            continue
        if line in (["help"], ["?"]):
            line = ["--help"]
        if line in (["quit"], ["q"], ["exit"]):
            return

        current_task = asyncio.Task(single_request(line, context=context))
        interactive_expecting_keyboard_interrupt = asyncio.Future()

        done, pending = await asyncio.wait([current_task, interactive_expecting_keyboard_interrupt], return_when=asyncio.FIRST_COMPLETED)

        if current_task not in done:
            current_task.cancel()
        else:
            try:
                await current_task
            except SystemExit as e:
                if e.code != 0:
                    print("Exit code: %d"%e.code, file=sys.stderr)
                continue
            except Exception as e:
                print("Unhandled exception raised: %s"%(e,))

def error(msg, code=-1):
    for line in msg.splitlines():
        sys.stderr.write("[cli] ERROR: %s\n" % line)
    sys.stderr.write("---\n")
    sys.exit(code)
class ProcessException(Exception):
    pass	

class MQTTClass(mqttclient.Client):
    host = None
    port = None
    keepalive = None
    password = None
    topic = None
    username = None
    qos_level = None

    def on_connect(self,mqttc,obj,flags,rc):
        print ("connect success,rc: "+str(rc))

    def on_disconnect(self,mqttc,userdata,rc):
        if rc!=0:
            print ("Unexpected disconnect")
    def on_message(self,mqttc,obj,msg):
        print(msg.topic)
        print(" msg.qos: "+str(msg.qos))
        print(msg.payload)

    def on_publish(self, mqttc, obj, mid):
        print ("publish a message mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print("log message: "+string)

    def run(self):
        if self.username:
            self.username_pw_set(self.username,self.password)
        self.connect(self.host, self.port, self.keepalive)
        self.subscribe(self.topic, self.qos_level)
        self.loop_start()

parser = argparse.ArgumentParser(prog='clients',description='Command-lin code managemrnt tools for communication protocol',
	formatter_class=argparse.RawTextHelpFormatter)
subparsers = parser.add_subparsers(title='Commands',metavar='          ')
parser.add_argument('--version',action ='store_true',dest='version',help='print version number and exit')
subcommands = {}

def subcommand(name,*args,**kwargs):
    def __subcommand(command):
        if not kwargs.get('description') and kwargs.get('help'):
            kwargs['description'] = kwargs['help']
        if not kwargs.get('formatter_class'):
            kwargs['formatter_class'] = argparse.RawDescriptionHelpFormatter

        subparser = subparsers.add_parser(name, **kwargs)
        subcommands[name] = subparser

        for arg in args:
            arg = dict(arg)
            opt = arg['name']
            del arg['name']
            if isinstance(opt, str): # basestring
                subparser.add_argument(opt, **arg)
            else:
                subparser.add_argument(*opt, **arg)
        subparser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Verbose diagnostic output")
        subparser.add_argument("-vv", "--very_verbose", action="store_true", dest="very_verbose", help="Very verbose diagnostic output")
        def thunk(parsed_args):
            argv = [arg['dest'] if 'dest' in arg else arg['name'] for arg in args]
            argv = [(arg if isinstance(arg, basestring) else arg[-1]).strip('-').replace('-', '_') for arg in argv]
            argv = {arg: vars(parsed_args)[arg] for arg in argv if vars(parsed_args)[arg] is not None}

            return command(**argv)
        subparser.set_defaults(command=thunk)
        return command
    return __subcommand

# mqtt
@subcommand('mqtt',
	dict(name=['-d','--debug'],help='if debug is false publish message else subscribe or else'),
	dict(name=['-a','--host'],help='the default host is localhost'),
	dict(name=['-i','--id'],help='id of the client'),
	dict(name=['-k','--keepalive'],help='the time keepalive'),
	dict(name=['--p','--port'],help='the default port is 1883,is the broker is ssl the default port is 8883'),
	dict(name=['-u','--username'],help='the username'),
	dict(name=['-P','--password'],help='password'),
	dict(name=['-t','--topic'],help='the subscribe topic'),
	dict(name='--payload',dest='pub_payload',help='the message to publish'),
	dict(name='--qos',dest='qos_level',action='store_true',help='the desired quality of service level for the subscription. Defaults to 0'),
	help='mqtt client [-d] [-h hostname] [-i clientid] [-k keepalive] [-p port] [-u username [-P password]] [-v] -t topic',
	description=('subscribe topic from other client/broker'))
def mqtt(debug=True,host='localhost',client_id="",pub_payload=None,keepalive=60,port=1883,username=None,password=None,topic=None,qos_level=0):
	if topic is None:
		print ("please input the topic")
	if debug:
		if client_id:
			mqttc = MQTTClass(client_id)
		else:
			mqttc = MQTTClass()
		mqttc.host=host
		mqttc.keepalive=keepalive
		mqttc.port=port
		mqttc.qos_level=qos_level
		mqttc.username=username
		mqttc.password=password
		mqttc.topic=topic
		try:
			mqttc.run()
			while True:
				chosen = raw_input("publish message or unsubscribe the topic ? [p/u/N] :")
				if chosen != "" and not (chosen == "n" or chosen =="N" or chosen =="p" or chosen == "P" or chosen =="u" or chosen == "U"):
					print ("unrecognized choose")
					continue
				elif chosen =="p" or chosen =="P":
					while True:
						rst =raw_input("[topic] ")
						if rst=="":
							publish_topic=mqttc.topic
						else:
							publish_topic=rst
						rst = raw_input("[payload] ")
						if rst=="":
							print (" you must input the payload")
							continue
						else:
							publish_payload=rst
						try:
							mqttc.publish(publish_topic,publish_payload)
						except ProcessException as e:
							print ("publish error: "+e[0])
						break
				elif chosen =="u" or chosen =="U":
					mqttc.unsubscribe(mqttc.topic)
				else:
					break
		except ProcessException as e:
			err="mqtt subscribe err :"
			error(err,e[0])
@subcommand('coap',
	dict(name=['-n','--non'], help="Send request as non-confirmable (NON) message", action='store_true'),
	dict(name=['-m','--method'],help="Name or number of request method to use (default: %(default)s)", default="GET"),
	dict(name='--observe',dest='coap_observe',help="Register an observation on the resource", action='store_true'),
	dict(name=['-p','--payload'],help='the payload'),
	dict(name=['-a','--accept'],help="Content format to request"),
	dict(name='--proxy',dest='coap_proxy',help="Relay the CoAP request to a proxy for execution"),
	dict(name=['-d','--dump'],help="Log network traffic to FILE"),
	dict(name=['-u','--url'],help="CoAP address to fetch"),
	dict(name=['-c','--credentials'],help="Load credentials to use from a given file",type=Path),
    dict(name="--format",dest='content_format',help="Content format sent via POST or PUT"),
    dict(name='--interactive', dest='interactive',help="Enter interactive mode", action="store_true"),
	help='the coap client,send reuqest to coap server and receive response',
	description=('send request ,GET PUT POST DISCOVER and so on'))
def coap(method='GET',non=None,coap_observe=False,payload=None,accept=None,coap_proxy=None,dump=None,url='localhost',
    credentials=None,content_format=None,interactive=False):

    interactive_expecting_keyboard_interrupt = asyncio.Future()


    if not interactive:
        try:
            asyncio.get_event_loop().run_until_complete(coap_single_request(method=method,non=non,payload=payload,url=url,observe=coap_observe,
                accept=accept,proxy=coap_proxy,credentials=credentials,dump=dump,content_format=content_format,context=None))
        except KeyboardInterrupt:
            sys.exit(3)
    else:
        loop=asyncio.get_event_loop()
        task = asyncio.Task(coap_interactive())
        task.add_done_callback(lambda result: loop.stop())
        while not loop.is_closed():
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                if not interactive_expecting_keyboard_interrupt.done():
                    interactive_expecting_keyboard_interrupt.set_result(None)
            except SystemExit:
                continue
@subcommand('lwm2m',
    dict(name=['-c','--objecturi'],help="create resoure,[obj1,obj2,...]",action='store_true'),
    dict(name=['-s','--objvalue'],help="set the value of the resource",action='store_true'),
    dict(name=['-r','--register'],help="register the client"),
    help='the lwm2m client.create resource,set resource and register,-c objectUri -s objecturl/value',
    description="the lwm2m client")
def lwm2m(objecturi=None,objvalue=None,register=True):
    client=lwm2mclient.Client()

    if objecturi:
        check=True
        while check:
            chosen =raw_input("Input the object uri(n don't create any more): ")
            if chosen == "":
                continue
            elif chosen=="n" or chosen=="N":
                check=False
            else:
                client.createResource(chosen)
    if objvalue :
        check=True
        while check:
            chosen =raw_input("Input the object uri(n don't create any more): ")
            if chosen == "":
                continue
            elif chosen=="n" or chosen=="N":
                check=False
            else:
                client.setResource(chosen)
    if register :
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(client.register())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()
@subcommand('help',
    help='This help screen')
def help_():
    return parser.print_help()

def main():
    global verbose,very_verbise,remainder
    if sys.version_info[0]!=3:
        
        logger.error("the CLI is compatible with Python version 3")
    if len(sys.argv)<=1:
        help_()
        sys.exit(1)
    if  '--version' in sys.argv :
        logger.info(ver+"\n")
        sys.exit(0)
    pargs,remainder =parser.parse_known_args()
    status=1
    try:
        very_verbose =pargs.very_verbose
        verbose =very_verbose or pargs.verbose
        print(pargs)
        status =pargs.command(pargs)
        print("  ")
        print(status)
    except ProcessException as e:
        logger.error(
            "\"%s\" returned error code %d.\n"
            "Command \"%s\" in \"%s\"" % (e[1], e[0], e[2], e[3]), e[0])
    except OSError as e :
        if e[0] == errno.ENOENT:
            logger(
                "Could not detect one of the command-line tools.\n"
                "You could retry the last command with \"-v\" flag for verbose output\n", e[0])
        else:
            logger.error('OS Error :%s' % e[1],e[0])
    except KeyboardInterrupt as e:
        logger.info('User aborted',-1)
        sys.exit(255)
    except Exception as e:
        if very_verbose:
            traceback.print_exc(file=sys.stdout)
        print("Unknown Error")
        logger.error(e)
        #logger.error('Unknown Error :%s' %str(e),255)
    sys.exit(status or 0)

if __name__ == "__main__":
    main()




	








