import sys
import argparse
import logging
import shlex
import paho.mqtt.client as mqttclient
import paho.mqtt.publish as publish
try :
	import readline
except ImportError:
	pass
logging.basicConfig(level=logging.DEBUG,format='%(levelname)s %(message)s') 
logger = logging.getLogger("mqtt")
def build_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('-d','--debug',help='if debug is false publish message else subscribe or else')
    p.add_argument('-a','--host',help='the default host is localhost',default="localhost")
    p.add_argument('-i','--id',help='id of the client')
    p.add_argument('-k','--keepalive',help='the time keepalive',default=60)
    p.add_argument('-p','--port',help='the default port is 1883,is the broker is ssl the default port is 8883',default=1883)
    p.add_argument('-u','--username',help='the username')
    p.add_argument('-P','--password',help='password')
    p.add_argument('-t','--topic',help='the subscribe topic')
    p.add_argument('--payload',help='the message to publish',action='store_true')
    p.add_argument('--qos',action='store_true',help='the desired quality of service level for the subscription. Defaults to 0',default=0)

    return p
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


def main(args=None):
    if args is None:
        args =sys.argv[1:]
    parser=build_parser()
    option=parser.parse_args(args)

    if option.debug:
        if option.id:
            mqttc =MQTTClass(option.id)
        else:
            mqttc =MQTTClass()
        mqttc.host=option.host
        mqttc.keepalive=option.keepalive
        mqttc.port=option.port
        mqttc.qos_level=option.qos
        mqttc.username=option.username
        mqttc.password=option.password
        mqttc.topic=option.topic
        try:
            mqttc.run()
            while True:
                chosen = input("publish message or unsubscribe the topic ? [p/u/N] :")
                if chosen != "" and not (chosen == "n" or chosen =="N" or chosen =="p" or chosen == "P" or chosen =="u" or chosen == "U"):
                    print("unrecognized choose")
                    continue
                elif chosen =="p" or chosen =="P":
                    while True:
                        rst =input("[topic] ")
                        if rst=="":
                            publish_topic=mqttc.topic
                        else:
                            publish_topic=rst
                        rst = input("[payload] ")
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
        except KeyboardInterrupt as e:

            logger.info('User aborted')
            sys.exit(255)
        except ProcessException as e:
            err="mqtt subscribe err :"
            logger.error(err,e[0])

if __name__== "__main__":
	main()