import time
from datetime import datetime, timedelta
import pytest
from src.kraken_websocket import KrakenWebSocket
from src.messages.ks_messages import *


@pytest.fixture
def public_channels():
    return [SubscriptionType.Book, SubscriptionType.Spread, SubscriptionType.Ticker, SubscriptionType.OHLC,
            SubscriptionType.Trade]


def ks_web_socket():
    ks = KrakenWebSocket(['XBT/USD'])
    ks.create_web_socket()
    return ks


def time_start_end(wait_time):
    time_now = datetime.now()
    end = datetime.now() + timedelta(seconds=wait_time)
    return time_now, end


def get_channel_id(channel=SubscriptionType.Book, pair='XBT/USD'):
    """
    Functions takes channel and pair parameter and returns the unique channel_id associated with this subscription
    :param channel: ohlc, book, trade, spread, ticker
    :param pair: XBT/USD
    :return: channel_pair
    """
    return '{}_{}'.format(channel, pair)


def subscription_validation(subscription_status, channel, expect):
    """
    Subscription validation function will perform assertions by comparing the received subscription status for a
    given channel and test it against the expected result
    """
    for key, value in expect.items():
        if key in subscription_status.keys():
            if value == subscription_status[key]:
                print('Subscription status message shows correct info for field: {}, value: {}'.format(key, value))
                assert True
            elif key == 'channelName' and subscription_status[key].find(channel) != -1:
                print(
                    'Subscription status message shows correct info for field: {}, value: {}, expected: {}'.format(key,
                                                                                                                   subscription_status[
                                                                                                                       key],
                                                                                                                   value))
                assert True
            else:
                print(
                    'Subscription status message doesn\'t match expected value for field: {}, value: {}, expected: {}'.format(
                        key, subscription_status[key], value))
                assert False
        else:
            print('Field: {} was not found in Subscription Status message'.format(key))
            assert False


def test_subscribe_to_public_channel(public_channels):
    """
    Test Scenario:
    Send a subscribe message to all public channels, including, 'ohlc', 'book', 'trade', 'ticker', 'spread'

    Validation Criteria:
    - The received SubscriptionStatus message should indicate successful subscription and is validated field by field
    - The time between sending a subscribe message to receiving a SubscriptionStatus message is expected to be
    less than 5 seconds on the socket
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        ks = ks_web_socket()
        pair = 'XBT/USD'
        channel_id = get_channel_id(channel=channel, pair=pair)
        expect = {'event': 'subscriptionStatus', 'pair': pair, 'channelName': channel, 'status': 'subscribed'}
        ks.subscribe(channel)
        wait_time = 5
        time_now, end = time_start_end(wait_time)
        msg_found = False
        start = time.time()
        while time_now < end:
            if channel_id in ks.subscription_messages:
                print('Received subscription status message for channelID: {}'.format(channel_id))
                assert True
                subscription_status = ks.subscription_messages[channel_id][MsgTypes.GeneralMessage].message
                subscription_validation(subscription_status, channel, expect)
                msg_found = True
                break
            else:
                time_now = datetime.now()
                time.sleep(0.001)

        if msg_found:
            end = time.time()
            time_delta = end - start
            assert time_delta < 5
            print('Subscription Status message received in {} seconds'.format(time_delta))

        else:
            print(
                'Failed to receive subscription status message for channelID: {} within: {} seconds'.format(channel_id,
                                                                                                            wait_time))
            assert False
        ks.unsubscribe(channel)
        ks.ws_close()


def test_subscribe_to_incorrect_channel():
    """
    Test Scenario:
    Send a subscribe message to an invalid channel name, i.e. 'fake'

    Validation Criteria:
    - The received SubscriptionStatus message should indicate unsuccessful subscription and is validated field by field
    - The time between sending a subscribe message to receiving a SubscriptionStatus message is expected to be
    less than 5 seconds on the socket
    """
    channel = 'fake'
    print('Testing Channel: {}'.format(channel))
    ks = ks_web_socket()
    pair = 'XBT/USD'
    expect = {'errorMessage': 'Subscription name invalid', 'event': 'subscriptionStatus', 'pair': pair,
              'subscription': {'name': channel}, 'status': 'error'}
    ks.subscribe(channel)
    wait_time = 5
    time_now, end = time_start_end(wait_time)
    msg_found = False
    start = time.time()

    while time_now < end:
        if MsgTypes.subscriptionStatus in ks.g_messages:
            print('Received subscription status message for channelName: {}'.format(channel))
            assert True
            subscription_status = ks.g_messages['subscriptionStatus'][0].message
            subscription_validation(subscription_status, channel, expect)
            msg_found = True
            break
        else:
            time_now = datetime.now()
            time.sleep(0.1)

    if msg_found:
        end = time.time()
        time_delta = end - start
        assert time_delta < 5
        print('Subscription Status message received in {} seconds'.format(time_delta))

    else:
        print('Failed to receive subscription status message for channelID: {} within: {} seconds'.format(channel,
                                                                                                          wait_time))
        assert False
    ks.unsubscribe(channel)
    ks.ws_close()


def test_subscribe_with_incorrect_field(public_channels):
    """
    Test Scenario:
    Send a subscribe message to a public channel, adding the optional field 'Interval'.
    This field is only applicable to the 'ohlc' channel.

    Validation Criteria:
    if channel == ohlc:
        - The received SubscriptionStatus message should indicate successful subscription
    else:
        - The received SubscriptionStatus message should indicate successful subscription
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        ks = ks_web_socket()
        pair = 'XBT/USD'
        channel_id = get_channel_id(channel=channel, pair=pair)
        expect_error = {'errorMessage': 'Subscription {} doesn\'t require interval'.format(channel),
                        'event': 'subscriptionStatus', 'pair': pair, 'subscription': {'name': channel, 'interval': 1},
                        'status': 'error'}
        expect = {'event': 'subscriptionStatus', 'pair': pair, 'channelName': channel, 'status': 'subscribed',
                  'subscription': {'name': channel, 'interval': 1}}
        subscription = convert_to_json(
            {"event": "subscribe", "pair": [pair], "subscription": {"name": channel, "interval": 1}})
        ks.ws_send(subscription)
        wait_time = 5
        time_now, end = time_start_end(wait_time)
        msg_found = False
        while time_now < end:
            if 'subscriptionStatus' in ks.g_messages and channel != SubscriptionType.OHLC:
                print('Received subscription status message for channelName: {}'.format(channel))
                assert True
                subscription_status = ks.g_messages['subscriptionStatus'][0].message
                subscription_validation(subscription_status, channel, expect_error)
                msg_found = True
                break

            elif channel_id in ks.subscription_messages and channel == SubscriptionType.OHLC:
                print('Received subscription status message for channelName: {}'.format(channel))
                assert True
                subscription_status = ks.subscription_messages[channel_id][MsgTypes.GeneralMessage].message
                subscription_validation(subscription_status, channel, expect)
                msg_found = True
                ks.unsubscribe(channel)
                break

        if not msg_found:
            print('Failed to receive subscription status message for channelName: {} within: {} seconds'.format(channel,
                                                                                                                wait_time))
            assert False
        ks.ws_close()


def test_subscribe_with_wrong_pair_field(public_channels):
    """
    Test Scenario:
    Send a subscribe message to each public channel with wrong input on pair field. The WebSocket API expects a list
    to be provided. Instead, a string will be provided.
    This is expected to trigger an error on the subscription status message

    Validation Criteria:
    - The received SubscriptionStatus message should indicate unsuccessful subscription and is validated field by field
    - The time between sending a subscribe message to receiving a SubscriptionStatus message is expected to be
    less than 5 seconds on the socket
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        ks = ks_web_socket()
        pair = 'XBT/USD'
        subscription = convert_to_json({"event": "subscribe", "pair": pair, "subscription": {"name": channel}})
        expect = {'errorMessage': 'Pair field must be an array'.format(channel), 'event': 'subscriptionStatus',
                  'pair': pair, 'subscription': {'name': channel}, 'status': 'error'}
        ks.ws_send(subscription)
        wait_time = 5
        time_now, end = time_start_end(wait_time)
        msg_found = False
        while time_now < end:
            if 'subscriptionStatus' in ks.g_messages:
                print('Received subscription status message for channelName: {}'.format(channel))
                assert True
                subscription_status = ks.g_messages['subscriptionStatus'][0].message
                subscription_validation(subscription_status, channel, expect)
                msg_found = True
                break

        if not msg_found:
            print('Failed to receive subscription status message for channelName: {}'.format(channel))
            assert False

        ks.ws_close()


def test_subscribe_to_public_channel_multi_pairs(public_channels):
    """
    Test Scenario:
    Send a subscribe message to all available public channels, including, 'ohlc', 'book', 'trade', 'ticker', 'spread'
    with multiple pairs, e.g. XBT/USD and ETH/EUR

    Validation Criteria:
    - A SubscriptionStatus message is expected to be received for each of the pairs
    - Validate the contents of the SubscriptionStatus message
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        ks = ks_web_socket()
        pairs = ['XBT/USD', 'ETH/EUR']
        ks.pair = pairs
        ks.subscribe(channel)

        for pair in pairs:
            channel_id = get_channel_id(channel=channel, pair=pair)
            expect = {'event': 'subscriptionStatus', 'pair': pair, 'channelName': channel, 'status': 'subscribed'}

            wait_time = 5
            time_now, end = time_start_end(wait_time)
            msg_found = False
            while time_now < end:
                if channel_id in ks.subscription_messages:
                    print('Received subscription status message for channelID: {}'.format(channel_id))
                    assert True
                    subscription_status = ks.subscription_messages[channel_id][MsgTypes.GeneralMessage].message
                    subscription_validation(subscription_status, channel, expect)
                    msg_found = True
                    break
                else:
                    time_now = datetime.now()
                    time.sleep(0.1)
            if not msg_found:
                print('Failed to receive subscription status message for channelID: {} within: {} seconds'.format(
                    channel_id, wait_time))
                assert False
        ks.unsubscribe(channel)
        ks.ws_close()


def test_subscribe_to_public_channel_incorrect_pair(public_channels):
    """
    Test Scenario:
    Send a subscribe message to all available public channels, including, 'ohlc', 'book', 'trade', 'ticker', 'spread'
    with an incorrect pair, e.g. MAG/USD

    Validation Criteria:
    - A SubscriptionStatus message will indicate an error "Currency pair not supported MAG/USD"
    - Validate the contents of the SubscriptionStatus message
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        ks = ks_web_socket()
        pair = 'MAG/USD'
        ks.pair = [pair]
        ks.subscribe(channel)
        channel_id = get_channel_id(channel=channel, pair=pair)
        expect = {'errorMessage': 'Currency pair not supported MAG/USD'.format(channel), 'event': 'subscriptionStatus',
                  'pair': pair, 'subscription': {'name': channel}, 'status': 'error'}
        wait_time = 5
        time_now, end = time_start_end(wait_time)
        msg_found = False
        while time_now < end:
            if MsgTypes.subscriptionStatus in ks.g_messages:
                print('Received subscription status message for channelID: {}'.format(channel_id))
                assert True
                subscription_status = ks.g_messages['subscriptionStatus'][0].message
                subscription_validation(subscription_status, channel, expect)
                msg_found = True
                ks.ws.close()
                break
            else:
                time_now = datetime.now()
                time.sleep(0.1)
        if not msg_found:
            print(
                'Failed to receive subscription status message for channelID: {} within: {} seconds'.format(channel_id,
                                                                                                            wait_time))
            assert False
        ks.ws_close()


def test_subscribe_to_public_channel_multi_pair_incorrect_and_correct(public_channels):
    """
    Test Scenario:
    Send a subscribe message to all available public channels, including, 'ohlc', 'book', 'trade', 'ticker', 'spread'
    with an array of pairs that include a supported and another unsupported pair, e.g. MAG/USD and XBT/USD

    Validation Criteria:
    - Expected to receive two SubscriptionStatus messages
    - 1st SubscriptionStatus message will indicate an error "Currency pair not supported MAG/USD" for MAG/USD pair
    - 2nd SubscriptionStatus message will indicate successful subscription to the supported pair XBT/USD
    - Validate the contents of the SubscriptionStatus messages
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        ks = ks_web_socket()
        pairs = ['MAG/USD', 'XBT/USD']
        ks.pair = pairs
        ks.subscribe(channel)

        for pair in pairs:
            channel_id = get_channel_id(channel=channel, pair=pair)
            expect_error = {'errorMessage': 'Currency pair not supported MAG/USD'.format(channel),
                            'event': 'subscriptionStatus', 'pair': pair, 'subscription': {'name': channel},
                            'status': 'error'}
            expect = {'event': 'subscriptionStatus', 'pair': pair, 'channelName': channel, 'status': 'subscribed'}
            wait_time = 5
            time_now, end = time_start_end(wait_time)
            msg_found = False
            while time_now < end:
                if pair == 'MAG/USD':
                    if MsgTypes.subscriptionStatus in ks.g_messages:
                        for msg in ks.g_messages['subscriptionStatus']:
                            print('Received subscription status message for channelID: {}'.format(channel_id))
                            assert True
                            subscription_status = msg.message
                            subscription_validation(subscription_status, channel, expect_error)
                            msg_found = True
                        break
                    else:
                        time_now = datetime.now()
                        time.sleep(0.1)
                elif pair == 'XBT/USD':
                    if channel_id in ks.subscription_messages:
                        print('Received subscription status message for channelID: {}'.format(channel_id))
                        assert True
                        subscription_status = ks.subscription_messages[channel_id][MsgTypes.GeneralMessage].message
                        subscription_validation(subscription_status, channel, expect)
                        msg_found = True
                        break
                    else:
                        time_now = datetime.now()
                        time.sleep(0.1)

            if not msg_found:
                print('Failed to receive subscription status message for channelID: {} within: {} seconds'.format(
                    channel_id, wait_time))
                assert False
        ks.pair = ['XBT/USD']
        ks.unsubscribe(channel)
        ks.ws_close()


def test_unsubscribe_to_public_channel():
    """
    Test Scenario:
    Send a subscribe message to the 'book' public channel
    Wait for incoming feed within 20seconds or until we reach 20 messages are available in the feed queue
    Send unsubscribe message for the same channel

    Validation criteria:
    - Validate the contents of the unsubscribe message
    - Validate that the feed stops/halts after unsubscribing to a given channel, i.e. feed queue should not increase
    """
    channel = SubscriptionType.Book
    print('Testing Channel: {}'.format(channel))
    ks = ks_web_socket()
    pair = 'XBT/USD'
    channel_id = get_channel_id(channel=channel, pair=pair)
    expect_unsubscribe = {"channelName": channel, "event": "subscriptionStatus", "pair": pair,
                          "status": "unsubscribed", }
    ks.subscribe(channel)
    wait_time = 20
    time_now, end = time_start_end(wait_time)
    subscription_channel_msg_found = False
    while time_now < end:
        if channel_id in ks.subscription_messages:
            if MsgTypes.PublicMessage in ks.subscription_messages[channel_id]:
                print('Received subscription status and feed message for channelID: {}'.format(channel_id))
                assert True
                subscription_channel_msg_found = True
                break
        time.sleep(0.1)
        time_now = datetime.now()
    if subscription_channel_msg_found:
        # waiting 10 seconds for more incoming feed messages to ensure feed stops after unsubscription
        wait_time = 20
        time_now, end = time_start_end(wait_time)
        print('Waiting for incoming feed on the {} channel'.format(channel))
        while time_now < end:
            if len(ks.subscription_messages[channel_id][MsgTypes.PublicMessage]) > 20:
                print('Received subscription status and feed message for channelID: {}'.format(channel_id))
                assert True
                break
            time.sleep(0.1)
            time_now = datetime.now()
        ks.unsubscribe(channel)
        time.sleep(1)
        ks.connection_state = False
        ks.ws_close()
        msg_count = len(ks.subscription_messages[channel_id][MsgTypes.PublicMessage])
        print('Received {} msgs on the {} channel'.format(msg_count, channel))
        wait_time = 10
        time_now, end = time_start_end(wait_time)
        msg_found = False
        while time_now < end:
            if MsgTypes.subscriptionStatus in ks.g_messages:
                print('Received unsubscription status message for channelName: {}'.format(channel))
                assert True
                subscription_status = ks.g_messages['subscriptionStatus'][0].message
                subscription_validation(subscription_status, channel, expect_unsubscribe)
                msg_found = True
                break
            else:
                time_now = datetime.now()
                time.sleep(0.1)
        if not msg_found:
            print('Failed to receive unsubscription status message for channelID: {} within: {} seconds'.format(
                channel_id,
                wait_time))
            assert False
        time.sleep(
            10)  # wait 10 seconds to ensure that the feed array didn't increase in size on the respective channel
        new_msg_count = len(ks.subscription_messages[channel_id][MsgTypes.PublicMessage])
        if new_msg_count == msg_count:
            assert True
            print(
                'Feed halted successfully after unsubscribing to channel {}. Feed messages received after ubsubscribing = 0'.format(
                    channel))
        else:
            print(
                'Feed continued after unsubscribing to channel {}, number of received messages after unsubscribing: {}, expected: {}'.format(
                    channel, new_msg_count, msg_count))
            assert False
    else:
        print(
            'Failed to receive subscription status message for channelID: {} within: {} seconds'.format(channel_id,
                                                                                                        wait_time))
        assert False
    ks.ws_close()


def test_increasing_epoch_on_spread_feed():
    """
    Test Scenario:
    Subscribe to the spread channel and compare the epoch on incoming feeds.
    Wait for at least a number of messages are available in the feed queue

    Validation Criteria:
    - Check if SubscriptionStatus and Spread feed messages are seen on the socket/channel
    - Check if epoch on subsequent messages in the 'spread' feed queue are an increasing order
    """
    channel = SubscriptionType.Spread
    print('Testing Channel: {}'.format(channel))
    ks = ks_web_socket()
    pair = 'XBT/USD'
    channel_id = get_channel_id(channel=channel, pair=pair)
    ks.subscribe(channel)

    wait_time = 30
    time_now, end = time_start_end(wait_time)
    subscription_channel_msg_found = False

    while time_now < end:
        if channel_id in ks.subscription_messages:
            if MsgTypes.PublicMessage in ks.subscription_messages[channel_id]:
                print('Received subscription status and feed message for channelID: {}'.format(channel_id))
                assert True
                subscription_channel_msg_found = True
                break

        time.sleep(0.1)
        time_now = datetime.now()

    num_of_messages_to_compare_epoch = 10
    if subscription_channel_msg_found:
        while len(ks.subscription_messages[channel_id]['public_message']) < num_of_messages_to_compare_epoch:
            time.sleep(1)
        epoch = 0
        for i in range(num_of_messages_to_compare_epoch):
            payload = ks.subscription_messages[channel_id]['public_message'][i]
            payload.get_payload()
            spread_fields = payload.fields
            spread_timestamp = float(spread_fields['timestamp'])
            if epoch == 0:
                epoch = spread_timestamp
            elif spread_timestamp >= epoch:
                print('New epoch: {} is higher or equal to previous epoch: {}, delta:{}'.format(spread_timestamp,
                                                                                                epoch,
                                                                                                spread_timestamp - epoch))
                epoch = spread_timestamp
                assert True
            elif spread_timestamp < epoch:
                print('New epoch: {} is less than previous epoch: {}, delta:{}'.format(spread_timestamp, epoch,
                                                                                       spread_timestamp - epoch))
                epoch = spread_timestamp
                assert False
    else:
        print('Failed to receive subscription status and feed message for channelName: {} within: {} seconds'.format(
            channel, wait_time))
        assert False

    ks.unsubscribe(channel)
    ks.ws_close()


def test_increasing_epoch_on_trade_feed():
    """
    Test Scenario:
    Subscribe to the trade channel and compare the epoch on incoming feeds.
    Wait until at least 3 messages are available in the feed queue for comparison and validation
    Note: Trade message contains an array of trade/s, each trade with it's own timestamp

    Validation Criteria:
    - Compare the min epoch of latest feed is greater than or equal to the max epoch of previous feed in the queue
    """
    channel = SubscriptionType.Trade
    print('Testing Channel: {}'.format(channel))
    ks = ks_web_socket()
    pair = 'XBT/USD'
    channel_id = get_channel_id(channel=channel, pair=pair)
    ks.subscribe(channel)
    wait_time = 60
    time_now, end = time_start_end(wait_time)
    subscription_channel_msg_found = False

    while time_now < end:
        if channel_id in ks.subscription_messages:
            if MsgTypes.PublicMessage in ks.subscription_messages[channel_id]:
                print('Received subscription status and feed message for channelID: {}'.format(channel_id))
                assert True
                subscription_channel_msg_found = True
                break

        time.sleep(0.1)
        time_now = datetime.now()

    num_of_messages_to_compare_epoch = 2
    if subscription_channel_msg_found:
        while len(ks.subscription_messages[channel_id]['public_message']) < num_of_messages_to_compare_epoch:
            time.sleep(1)
        epoch = 0
        for i in range(num_of_messages_to_compare_epoch):
            payload = ks.subscription_messages[channel_id]['public_message'][i]
            payload.get_payload()
            trade_fields = payload.fields
            trade_timestamp_max = max([float(trade['time']) for trade in trade_fields])
            trade_timestamp_min = min([float(trade['time']) for trade in trade_fields])
            if epoch == 0:
                epoch = trade_timestamp_max
            elif trade_timestamp_min >= epoch:
                print('New epoch: {} is higher or equal to previous epoch: {}, delta:{}'.format(trade_timestamp_min,
                                                                                                epoch,
                                                                                                trade_timestamp_min - epoch))
                epoch = trade_timestamp_max
                assert True
            elif trade_timestamp_min < epoch:
                print('New epoch: {} is less than previous epoch: {}, delta:{}'.format(trade_timestamp_min, epoch,
                                                                                       trade_timestamp_min - epoch))
                epoch = trade_timestamp_max
                assert False

    else:
        print('Failed to receive subscription status and feed message for channelName: {} within: {} seconds'.format(
            channel, wait_time))
        assert False

    ks.unsubscribe(channel)
    ks.ws_close()


def test_book_ask_bid_price_and_depth_level():
    """
    Test Scenario:
    - Subscribe to the book channel and wait for the first message to arrive (snapshot message)
    - Repeat the test for different depth_levels [10, 25, 100, 500, 1000]

    Validation Criteria:
    - Ask price list is in ascending order, i.e. best ask price on top
    - Bid price list is in descending order, i.e. best bid price on top
    - Check depth parameter is effective against the received book message, depth_levels [10, 25, 100, 500, 1000]
    - Validate that the best ask price > best big price. Failure to meet this condition could be an indication of matching engine failure
    """
    channel = SubscriptionType.Book
    print('Testing Channel: {}'.format(channel))
    pair = 'XBT/USD'
    depth_levels = [10, 25, 100, 500, 1000]
    channel_id = get_channel_id(channel=channel, pair=pair)

    for depth_level in depth_levels:
        ks = ks_web_socket()

        print('Testing Channel: {}, Depth_level: {}'.format(channel, depth_level))
        subscription = convert_to_json(
            {"event": "subscribe", "pair": [pair], "subscription": {"name": channel, "depth": depth_level}})
        ks.ws_send(subscription)

        wait_time = 20
        time_now, end = time_start_end(wait_time)
        subscription_channel_msg_found = False

        while time_now < end:
            if channel_id in ks.subscription_messages:
                if MsgTypes.PublicMessage in ks.subscription_messages[channel_id]:
                    print('Received subscription status and feed message for channelID: {}'.format(channel_id))
                    assert True
                    subscription_channel_msg_found = True
                    break

            time.sleep(0.1)
            time_now = datetime.now()

        if subscription_channel_msg_found:
            book_msg = ks.subscription_messages[channel_id][MsgTypes.PublicMessage][0]
            book_msg.get_payload()
            as_fields = book_msg.fields['as']
            bs_fields = book_msg.fields['bs']
            as_price_list = [float(entry['price']) for entry in as_fields]
            print(
                'Verify that the Ask price list is in ascending order, i.e. displaying the best ask price on top: {}'.format(
                    as_price_list[0]))
            assert as_price_list == sorted(as_price_list)

            bs_price_list = [float(entry['price']) for entry in bs_fields]
            print(
                'Verify that the Bid price list is in descending order, i.e. displaying the best bid price on top: {}'.format(
                    bs_price_list[0]))
            assert bs_price_list == sorted(bs_price_list, reverse=True)

            print(
                'Verify that the best Ask price ({}) >= best Bid price ({})'.format(as_price_list[0], bs_price_list[0]))
            assert as_price_list[0] >= bs_price_list[0]

            print('Verify that the depth level is obtained per subscription request on Ask field, depth: {}'.format(
                depth_level))
            assert len(as_fields) == depth_level

            print('Verify that the depth level is obtained per subscription request on Bid field, depth: {}'.format(
                depth_level))
            assert len(bs_fields) == depth_level

        else:
            print(
                'Failed to receive subscription status and feed message for channelName: {} within: {} seconds'.format(
                    channel, wait_time))
            assert False

        ks.unsubscribe(channel)
        ks.ws_close()


def test_book_ask_bid_price_and_volume_updates():
    """
    Test Scenario:
    - Subscribe to the book channel and collect feeds for 60 seconds

    Validation Criteria:
    - Validate that number of update messages received is > 0
    - Validate that there is at least one update message related to the best bid price level and best ask price levels
    - Validate that the epoch on the update message for a given price level is greater than that of the last known epoch for the same price level
    - Bid price list is in descending order, i.e. best bid price on top
    - Validate that the volume field in the update messages is >= 0
    """
    channel = SubscriptionType.Book
    print('Testing Channel: {}'.format(channel))
    ks = ks_web_socket()
    pair = 'XBT/USD'
    channel_id = get_channel_id(channel=channel, pair=pair)

    ks.subscribe(channel)
    wait_time = 20
    time_now, end = time_start_end(wait_time)
    subscription_channel_msg_found = False
    while time_now < end:
        if channel_id in ks.subscription_messages:
            if MsgTypes.PublicMessage in ks.subscription_messages[channel_id]:
                print('Received subscription status and feed message for channelID: {}'.format(channel_id))
                assert True
                subscription_channel_msg_found = True
                break
        time.sleep(0.1)
        time_now = datetime.now()

    if subscription_channel_msg_found:
        wait_time = 120
        print('Waiting {} seconds for incoming feed on the {} channel'.format(wait_time, channel))
        time.sleep(wait_time)
        ks.unsubscribe(channel)  # unsubscribe to stop incoming feed and perform validation on queued messages
        book_msgs = ks.subscription_messages['book_XBT/USD']['public_message']
        book_msg = book_msgs[0]
        book_msg.get_payload()
        as_fields = book_msg.fields['as']
        bs_fields = book_msg.fields['bs']
        as_price_list = [float(entry['price']) for entry in as_fields]
        bs_price_list = [float(entry['price']) for entry in bs_fields]

        snapshot = book_msg.message[1]
        as_dict = {level[0]: level for level in snapshot['as']}
        bs_dict = {level[0]: level for level in snapshot['bs']}
        ask_bid_map = {'a': 'Ask', 'b': 'Bid'}

        best_ask_price = as_price_list[0]
        best_bid_price = bs_price_list[0]
        result_track_best_bid_ask_prices = {best_ask_price: 0, best_bid_price: 0}

        for msg in book_msgs[1:]:
            update_msg = msg.message[1]
            for update_type in ['a', 'b']:
                if update_type in update_msg:
                    for update_level in update_msg[update_type]:
                        price_level = update_level[0]
                        snapshot_dict = as_dict if update_type == 'a' else bs_dict

                        if price_level in snapshot_dict.keys():
                            volume_new = update_level[1]

                            assert float(volume_new) >= 0

                            print('{}, Price level:{}, Volume changed from: {} to: {}'.format(ask_bid_map[update_type],
                                                                                              price_level,
                                                                                        snapshot_dict[price_level][1],
                                                                                           volume_new))
                            time_previous = float(snapshot_dict[price_level][2])
                            time_update = float(update_level[2])
                            time_delta = time_update - time_previous
                            assert time_delta >= 0
                            print(
                                '{}, Price level:{}, Update received {} seconds since last snapshot or book update msg. from: {}, to: {}'.format(
                                    ask_bid_map[update_type], price_level, time_delta, time_previous, time_update))
                            snapshot_dict[price_level] = update_level[:3]

                            if update_type == 'a':
                                if float(price_level) == best_ask_price:
                                    result_track_best_bid_ask_prices[best_ask_price] += 1
                            if update_type == 'b':
                                if float(price_level) == best_bid_price:
                                    result_track_best_bid_ask_prices[best_bid_price] += 1

                            if update_type == 'a':
                                as_dict = snapshot_dict.copy()
                            else:
                                bs_dict = snapshot_dict.copy()

        total_num_of_update_messages = len(book_msgs) - 1
        if total_num_of_update_messages > 0:
            print('Number of received update messages on channel {} for pair {} is {}, Message Rate: {} msgs/sec'.format(channel, pair, total_num_of_update_messages, total_num_of_update_messages/wait_time))
            assert True
        else:
            print('Failed to receive any update messages on channel {} for pair {}  is {}, Message Rate: {} msgs/sec'.format(channel, pair, total_num_of_update_messages, total_num_of_update_messages/wait_time))
            assert False

        for best_price, counter in result_track_best_bid_ask_prices.items():
            if counter > 0:
                print('Checking for update messages on the best price: {}, # of received update messages: {}'.format(best_price, counter))
                assert True
            else:
                print('Failed to receive any update messages on channel {} for pair {} within {} seconds for best price level: {}, counter: {}.'.format(
                        channel, pair, wait_time, best_price, counter))
                assert False

    else:
        print('Failed to receive subscription status and feed message for channelName: {} within: {} seconds'.format(
            channel, wait_time))
        assert False

    ks.ws_close()


def test_public_channel_schema_validation(public_channels):
    """
    Test Scenario:
    - Subscribe to a public channel and validate the received public message/s to ensure that they match the json schema
    - Wait for 20 seconds to allow for more incoming messages to be added to the feed queue

    Validation Criteria:
    - Perform Json Schema validation against each message in the feed of the corresponding public channel
    - Perform Data Structure validation against each message in the feed of the corresponding public channel
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        pair = 'XBT/USD'
        channel_id = get_channel_id(channel=channel, pair=pair)
        ks = ks_web_socket()
        print('Testing Channel: {}'.format(channel))
        ks.subscribe(channel)
        wait_time = 20
        time_now, end = time_start_end(wait_time)
        subscription_channel_msg_found = False
        while time_now < end:
            if channel_id in ks.subscription_messages:
                if MsgTypes.PublicMessage in ks.subscription_messages[channel_id]:
                    print('Received subscription status and feed message for channelID: {}'.format(channel_id))
                    assert True
                    subscription_channel_msg_found = True
                    break
            time.sleep(0.1)
            time_now = datetime.now()

        time.sleep(10)  # waiting 10 seconds for more incoming feed messages to validate the json schema against

        max_num_of_feed_msgs_to_validate = 1 if channel == SubscriptionType.Book else 10  # in case of Book feed, the schema of the first message does not match that of subsequent update type messages

        if subscription_channel_msg_found:
            for iteration, feed_msg in enumerate(ks.subscription_messages[channel_id][MsgTypes.PublicMessage][
                                                 :max_num_of_feed_msgs_to_validate]):
                print(
                    'Validating incoming message #{} on the subscribed channel ({}) matches the expected json schema'.format(
                        iteration, channel))
                assert feed_msg.schema_validation()
                feed_data_structure_validation_result = feed_msg.get_payload()
                assert feed_data_structure_validation_result
                if feed_data_structure_validation_result:
                    print(
                        'Validated incoming message matches the expected data structure for subscription channel: {}'.format(
                            channel))
                    print(feed_msg.fields)
                else:
                    print(
                        'Failed message validation on incoming message for subscription channel: {}, msg: {}'.format(
                            channel, feed_msg.message))


def test_subscription_status_schema_validation(public_channels):
    """
    Test Scenario:
    - Subscribe to a public channel and wait to receive the SubscriptionStatus message

    Validation Criteria:
    - Perform Json Schema validation against the SubscriptionStatus message
    """
    for channel in public_channels:
        print('Testing Channel: {}'.format(channel))
        pair = 'XBT/USD'
        channel_id = get_channel_id(channel=channel, pair=pair)
        ks = ks_web_socket()
        print('Testing Channel: {}'.format(channel))

        ks.subscribe(channel)
        wait_time = 5
        time_now, end = time_start_end(wait_time)
        msg_found = False
        while time_now < end:
            if channel_id in ks.subscription_messages:
                print('Received subscription status message for channelID: {}'.format(channel_id))
                assert True
                subscription_status = ks.subscription_messages[channel_id][MsgTypes.GeneralMessage]
                print('Performing Json schema validation on Subscription Status message: {}'.format(subscription_status.message))
                assert subscription_status.schema_validation()
                msg_found = True
                break
            else:
                time_now = datetime.now()
                time.sleep(0.1)
        if not msg_found:
            print(
                'Failed to receive subscription status message for channelID: {} within: {} seconds'.format(channel_id,
                                                                                                            wait_time))
            assert False

        ks.unsubscribe(channel)
        ks.ws_close()
