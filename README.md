# PyGethWS
### A Websocket endpoint written in Python/Pyramid that connects to Geth WS-RPC server.

## Introduction
This endpoint was originally designed to connect to a local geth node. But when connected to infura it can access their extra websocket methods.

## Getting Started
```
  git clone https://github.com/webjunkie01/PyGethWS.git
  cd PyGethWS
  venv/bin/pip install -e .
  venv/bin/uwsgi --ini-paste GethWS.ini
```
If you go to `http://0.0.0.0:6540/` you should receive a json response similar to this
```
  {"GETH WS": "0.1.0", "url": "http://0.0.0.0:6540"}
```

## Examples

There's two Javascript examples that show how to connect to the endpoint located in the `js_examples` folder.

* subscribe.html  
Demonstrates how to connecto to the supported methods by geth like `logs`,`newHeads` and `newPendingTransactions`. If you connect to an infura endpoing you also can execute methods like `eth_getFilterLogs`, `eth_getFilterChanges`, etc.
* balance.html  
Demonstrates how to monitor eth balance changes for a given wallet address. This is not a supported eth method.