# Regression Test Suite for the Kraken WebSocket API

This is a regression test suite built to validate the [Kraken WebSocket API](https://docs.kraken.com/websockets/#book-checksum)
 
### Project Structure:
File contains KrakenWebSocket API handler is built in this file, to create, send, receive, decode, store messages received on the WebSocket
```bash
kraken_websocket.py
```

File contains a list of test cases that will be called using the pytest module. Test case named def test_<> will be called by the pytest

```bash
test_ks_websocket.py
```

Kraken message types are defined in this file

```bash
messages/ks_messages.py
```

Json schemas supporting the Kraken WebSocket API message types and their corresponding data structures
```bash
messages/schemas.py
```

## Install

Pre-requisites: Docker engine to build the image from the Dockerfile
```bash
docker build -t kraken-test .
```

```bash
docker run kraken-test
```

## Usage

Running pytest against the project will call all test cases implemented in the Regression Test Suite

The `-s` option is to display the print messages on execution.

A test summary indicating number of test cases run and time duration will be displayed
```bash
src> pytest -s -vv
```

To call an individual test case, e.g. 'test_subscription_status_schema_validation':
```bash
src> pytest -s test_ks_websocket::test_subscription_status_schema_validation 
```

## References
[Kraken WebSocket API](https://docs.kraken.com/websockets/#book-checksum)

[websocket-client](https://websocket-client.readthedocs.io/en/latest/)