import unittest
import asyncio

import websockets
from pyramid import testing
import json


class HomeTestCase(unittest.TestCase):

    def test_home_view(self):
        from .balance import root
        request = testing.DummyRequest()
        info = asyncio.get_event_loop().run_until_complete(root(request))
        assert 'GETH WS' in info.keys()


class WSTest(unittest.TestCase):
    """ Test aiopyramid websocket view. """

    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def test_echo_view(self):
        #from .eth import Websocket

        @asyncio.coroutine
        def on_message(ws):
            print("AA",w)

        @asyncio.coroutine
        def _websockets_compat_wrapper(ws, path):
            """ wrapper to ignore the path argument used witn websockets.serve """
            from .eth import Websocket
            ws = Websocket
            yield from ws.on_open(ws)

        self.loop.run_until_complete(websockets.serve(_websockets_compat_wrapper, 'localhost', 8765))

        @asyncio.coroutine
        def _echo_view_client():
            ws = yield from websockets.connect('ws://localhost:8765/eth')
            yield from ws.send(json.dumps({"params": ["newPendingTransactions", {"address": "0x2075967CFda86234d674402b452E6be47daDDf9E" }] }))
        self.loop.run_until_complete(_echo_view_client())
