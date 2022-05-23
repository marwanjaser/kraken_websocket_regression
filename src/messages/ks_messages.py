import json
from src.messages.schemas import *
from jsonschema import Draft3Validator


def convert_to_json(subscription_dict):
    return json.dumps(subscription_dict)


def convert_from_json(subscription_dict):
    return json.loads(subscription_dict)


class MsgTypes:
    ConnectionID = 'connectionID'
    Event = 'event'
    subscriptionStatus = 'subscriptionStatus'
    GeneralMessage = 'general_message'
    PublicMessage = 'public_message'


class SubscriptionType:
    Ticker = 'ticker'
    OHLC = 'ohlc'
    Trade = 'trade'
    Spread = 'spread'
    Book = 'book'


class PublicMessages:
    def __init__(self, message):
        self.message = message
        self.schema = None

    def get_channel_id(self):
        self.channelID = self.message[0]
        return self.channelID

    def get_payload(self):
        self.payload = self.message[1]
        self.get_channel_name()
        if self.channelName == SubscriptionType.OHLC:
            self.schema = schema_ohlc
            return self.ohlc()
        elif self.channelName == SubscriptionType.Trade:
            self.schema = schema_trade
            return self.trade()
        elif self.channelName == SubscriptionType.Spread:
            self.schema = schema_spread
            return self.spread()
        elif self.channelName == SubscriptionType.Book:
            self.schema = schema_book
            return self.book()
        elif self.channelName == SubscriptionType.Ticker:
            self.schema = schema_ticker
            return self.ticker()

    def get_channel_name(self):
        self.channelName = self.message[2]
        if '-' in self.channelName:
            self.channelName = self.channelName.split('-')[0]
        return self.channelName

    def get_pair(self):
        self.pair = self.message[3]
        return self.pair

    def ohlc(self):
        ohlc_structure = ['time', 'etime', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count']

        if len(ohlc_structure) == len(self.payload):
            self.fields = dict()
            for key, value in zip(ohlc_structure, self.payload):
                self.fields[key] = value
            return True
        else:
            print('Expected Payload Length:{}, Actual:{}', len(ohlc_structure), len(self.payload))
            return False

    def spread(self):
        spread_structure = ['bid', 'ask', 'timestamp', 'bidVolume', 'askVolume']

        if len(spread_structure) == len(self.payload):
            self.fields = dict()
            for key, value in zip(spread_structure, self.payload):
                self.fields[key] = value
            return True
        else:
            print('Expected Payload Length:{}, Actual:{}', len(spread_structure), len(self.payload))
            return False

    def trade(self):
        trade_payload_len = len(self.payload)
        trade_entry_structure = ['price', 'volume', 'time', 'side', 'ordType', 'misc']
        self.fields = list()
        for i in range(trade_payload_len):
            if len(trade_entry_structure) == len(self.payload[i]):
                self.trade_entry_fields = dict()
                for key, value in zip(trade_entry_structure, self.payload[i]):
                    self.trade_entry_fields[key] = value
                self.fields.append(self.trade_entry_fields)
            else:
                print('Expected Payload Length:{}, Actual:{}', len(trade_entry_structure), trade_payload_len)
                return False
        return True

    def ticker(self):
        data_struct1 = ['price', 'wholeLotVolume', 'lotVolume']
        data_struct2 = ['price', 'lotVolume']
        data_struct3 = ['today', 'last24Hours']

        ticker_structure = {'a': data_struct1,
                            'b': data_struct1,
                            'c': data_struct2,
                            'v': data_struct3,
                            'p': data_struct3,
                            't': data_struct3,
                            'l': data_struct3,
                            'h': data_struct3,
                            'o': data_struct3}

        if len(ticker_structure.keys()) == len(self.payload.keys()):
            self.fields = dict()
            for key, value in ticker_structure.items():
                if key not in self.payload:
                    print('Expected Key:{} not in Payload:{}', key, self.payload.keys())
                    return False
                else:
                    self.fields[key] = dict()
                    for index, data in enumerate(value):
                        self.fields[key][data] = self.payload[key][index]
            return True
        else:
            print('Expected Payload Length:{}, Actual:{}', len(ticker_structure), len(self.payload.keys()))
            return False

    def book(self):
        data_struct = ['price', 'volume', 'timestamp']
        book_structure = {'as': list(), 'bs': list()}

        if len(book_structure.keys()) == len(self.payload.keys()):
            for key, value in self.payload.items():
                if key not in book_structure.keys():
                    print('Expected Key:{} not in expected Book fields:{}'.format(key, book_structure.keys()))
                    return False

                self.fields = book_structure
                for index in range(len(value)):
                    tmp_dict = dict()
                    for field, data in zip(data_struct, value[index]):
                        tmp_dict[field] = data
                    self.fields[key].append(tmp_dict)
            return True
        else:
            print('Expected Payload Length:{}, Actual:{}', len(book_structure.keys()), len(self.payload.keys()))
            return False

    def subscription_info(self):
        self.subscription_details = '{}_{}'.format(self.get_channel_name(), self.get_pair())
        return self.subscription_details

    def schema_validation(self):
        if self.schema is None:
            self.get_payload()
        return Draft3Validator(self.schema).is_valid(self.message)


class general_messages:
    def __init__(self, message):
        self.message = message

    def get_event(self):
        return self.message['event']

    def get_channel_name(self):
        self.channelName = self.message['channelName']
        if '-' in self.channelName:
            self.channelName = self.channelName.split('-')[0]
        return self.channelName

    def get_pair(self):
        self.pair = self.message['pair']
        return self.pair

    def is_subscription(self):
        if self.get_event() == MsgTypes.subscriptionStatus:
            if self.message['status'] == 'subscribed':
                self.subscription_details = '{}_{}'.format(self.get_channel_name(), self.get_pair())
                return True
            else:
                return False
        else:
            return False

    def schema_validation(self):
        if self.is_subscription:
            self.schema = schema_subscription_status
            return Draft3Validator(self.schema).is_valid(self.message)