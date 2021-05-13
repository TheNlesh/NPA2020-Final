import requests
import json
from secret import *
import time
from ncclient import manager
import xmltodict
from pprint import pprint

class WebEx:
    def __init__(self, bearer):
        self.bearer = bearer
        self.auth = {"Content-Type":"application/json", "Authorization":"Bearer {}".format(self.bearer)}

    def requestroomId(self, roomName):
        webex_url = "https://webexapis.com/v1/rooms"

        webex_response = requests.get(url=webex_url, headers=self.auth).json()['items']
        for room in webex_response:
            if room['title'] == roomName:
                return room['id']
        return "Not found"
    
    def setroomId(self, roomId):
        self.roomId = roomId

    def getLastestMsg(self, data='text'):
        webex_url = "https://webexapis.com/v1/messages"
        webex_param = {"roomId":self.roomId}
        webex_response = requests.get(url=webex_url, headers=self.auth, params=webex_param).json()
        return webex_response['items'][0][data]
    
    def sendMsg(self, text):
        webex_url = "https://webexapis.com/v1/messages"
        webex_param = {"roomId":self.roomId, 'text':text}
        webex_response = requests.post(url=webex_url, headers=self.auth, json=webex_param).json()
        return webex_response
    
    def delMsg(self, MsgId):
        webex_url = "https://webexapis.com/v1/messages/" + MsgId
        webex_response = requests.delete(url=webex_url, headers=self.auth)
        return webex_response

webExobj = WebEx(bearer)
roomId = webExobj.requestroomId(roomName="NPA2020@ITKMITL")

if roomId != "Not found":
    webExobj.setroomId(roomId)

    m = manager.connect(
        host = host,
        port = 830,
        username = username,
        password = password,
        hostkey_verify = False
    )

    def get_interfaces_state(int_name):
        netconf_filter = """
            <filter>
                <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                        <name>{}</name>
                    </interface>
                </interfaces-state>
            </filter>
        """.format(int_name)
        netconf_reply = m.get(filter=netconf_filter)
        resp_dict = xmltodict.parse(str(netconf_reply), dict_constructor=dict)['rpc-reply']['data']
        int_status = resp_dict['interfaces-state']['interface']
        return int_status['oper-status']


    while 1:
        msg = webExobj.getLastestMsg(data='text')
        print("The most recent message is {}".format(msg))

        if msg == "60070062":
            interface_state = get_interfaces_state("Loopback60070062")
            webExobj.sendMsg("Loopback60070062 - Operational status is {}".format(interface_state))
                
        
        elif msg.lower() == 'end':
            webExobj.sendMsg("Goodbye~")
            print("Terminated")
            break

        time.sleep(1)