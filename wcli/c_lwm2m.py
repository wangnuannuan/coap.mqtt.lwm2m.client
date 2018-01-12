import sys
import argparse
import logging
import shlex
import lwm2mclient.lwm2mclient as lwm2mclient
import asyncio

try :
	import readline
except ImportError:
	pass
logging.basicConfig(level=logging.DEBUG,format='%(levelname)s %(message)s') 
logger = logging.getLogger("lwm2m")
def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('-n','--endpointname',help='the device name')
    p.add_argument('-c','--objecturi',help="create resoure,[obj1,obj2,...]")
    p.add_argument('-s','--objvalue',help="set the value of the resource")
    p.add_argument('-r','--register',help="register the client")

    return p
def main(args=None):
    if args is None:
        args=sys.argv[1:]
    parser=build_parser()
    option=parser.parse_args(args)

    client=lwm2mclient.Client()
    try:
        if '-n' in args:
            client.endpointName=option.endpointname


        if option.objecturi=='yes':
            check=True
            while check:
                chosen =input("Input the object uri(n don't create any more): ")
                if chosen == "":
                    continue
                elif chosen=="n" or chosen=="N":
                    check=False
                else:
                    client.createResource(chosen)
        if option.objvalue == 'yes':
            check=True
            while check:
                chosen =input("set the object value(n don't create any more): ")
                if chosen == "":
                    continue
                elif chosen=="n" or chosen=="N":
                    check=False
                else:
                    str1=chosen.split(" ",2)
                    client.setResource(str1[0],str1[1],str1[2])

        if option.register =='yes':
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(client.register())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()
    except KeyboardInterrupt as e:
        logger.info("User aborted")
        sys.exit(255)