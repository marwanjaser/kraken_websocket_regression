import websocket
import _thread
import time

from src.messages.ks_messages import *


class KrakenWebSocket:
    def __init__(self, pair=['XBT/USD']):
        self.url = "wss://ws.kraken.com"
        self.pair = pair
        self.num_of_channels = len(self.pair)
        self.connection_state = True
        self.pb_messages = dict()
        self.g_messages = dict()
        self.subscription_messages = dict()

    def subscribe(self, subscription_type):
        subscription = {"event": "subscribe", "pair": self.pair, "subscription": {"name": subscription_type}}
        subscription = convert_to_json(subscription)
        self.ws_send(subscription)

    def unsubscribe(self, subscription_type):
        unsubscription = {"event":"unsubscribe","pair":self.pair,"subscription":{"name":subscription_type}}
        unsubscription = convert_to_json(unsubscription)
        self.ws_send(unsubscription)
        time.sleep(0.1)

    def create_web_socket(self):
        self.ws = websocket.create_connection(self.url)
        self.connectionID = self.ws_rcv()
        self.check_connection_status()

    def check_connection_status(self):
        print('Checking Connection Status')
        if 'systemStatus' in self.g_messages:
            if self.g_messages['systemStatus'][0].message['status'] == 'online':
                print('Connection Status: Online')
                self.start_rcv_thread()
        time.sleep(1)

    def ws_send(self, message):
        self.ws.send(message)

    def ws_close(self):
        self.connection_state = False
        time.sleep(0.5)

    def clear_messages(self):
        self.pb_messages = dict()
        self.g_messages = dict()

    def start_rcv_thread(self):
        def run(*args):
            while self.connection_state:
                try:
                    self.ws_rcv()
                except websocket.WebSocketConnectionClosedException as e:
                    self.connection_state = False
            self.ws.close()
            # print("Stopping Thread...")
        _thread.start_new_thread(run, ())

    def ws_decode_and_store(self, message):
        if type(message) is list:
            self.message = PublicMessages(message)
            self.message.subscription_info()
            if self.message.subscription_details not in self.subscription_messages:
                self.subscription_messages[self.message.subscription_details] = {'public_message':[self.message]}
            elif 'public_message' not in self.subscription_messages[self.message.subscription_details]:
                self.subscription_messages[self.message.subscription_details]['public_message'] = [self.message]
            else:
                self.subscription_messages[self.message.subscription_details]['public_message'].append(self.message)

        elif type(message) is dict:
            self.message = general_messages(message)
            if self.message.is_subscription():
                if self.message.subscription_details not in self.subscription_messages:
                    self.subscription_messages[self.message.subscription_details] = {'general_message':self.message}
                elif 'general_message' not in self.subscription_messages[self.message.subscription_details]:
                    self.subscription_messages[self.message.subscription_details]['general_message']= self.message
                else:
                    self.subscription_messages[self.message.subscription_details]['general_message'] = self.message
            else:
                event = self.message.get_event()
                if event == 'heartbeat':
                    return
                if event not in self.g_messages:
                    self.g_messages[event] = list()
                self.g_messages[event].append(self.message)
        else:
            print('Failed to decode: {}'.format(message))

    def ws_rcv(self):
        msg = self.ws.recv()
        if len(msg) > 0:
            rcv_message = convert_from_json(msg)
            self.ws_decode_and_store(rcv_message)