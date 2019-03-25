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

        @asyncio.coroutine
        def _websockets_compat_wrapper(ws, path):
            from .eth import Websocket
            request = testing.DummyRequest()
            web_socket = Websocket(ws,request)
            yield from web_socket(ws)

        self.loop.run_until_complete(websockets.serve(_websockets_compat_wrapper, 'localhost', 8765))

        @asyncio.coroutine
        def _echo_view_client():
            ws = yield from websockets.connect('ws://localhost:8765/eth')
            y = yield from ws.recv()
            response = json.loads(y)
            assert response.get('status') == 'success'
            msg = bytes('{"method": "eth_subscribe", "params": ["syncing"] }','utf-8')
            yield from ws.send(msg)
            r = yield from ws.recv()
            assert json.loads(r).get('jsonrpc') == "2.0"

        self.loop.run_until_complete(_echo_view_client())
