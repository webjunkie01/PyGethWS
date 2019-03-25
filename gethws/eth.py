import asyncio

import threading

from pyramid.view import view_config

import json

import uuid

import greenlet

from aiopyramid.websocket.view import WebsocketConnectionView

from aiopyramid.helpers import synchronize, spawn_greenlet, use_executor, run_in_greenlet

import configparser

import websockets

import base64


from pyramid.response import Response


from web3 import Web3, HTTPProvider

from web3.utils.encoding import (
    FriendlyJsonSerde,
)


from eth_utils import (
    to_bytes,
    to_text,
)

import itertools

from datetime import datetime

try:
    import uwsgi
    from aiopyramid.websocket.config import UWSGIWebsocketMapper
    WSMapper = UWSGIWebsocketMapper
    WSMapper.use_bytes = True
except ImportError:
    from aiopyramid.websocket.config import WebsocketMapper
    WSMapper = WebsocketMapper

config = configparser.ConfigParser()

if not config.read('GethWS.ini'):
    raise config.Error('Could not open %s' % config)

ws_provider =  config.get('app:main', 'ws_provider')
http_provider = config.get('app:main', 'http_provider')
web3_provider = HTTPProvider(http_provider)
web3 = Web3(web3_provider)



def is_authenticated(request,token,timestamp):
    token = base64.b64decode(token).decode('utf-8')
    print("decoded token", token)
    print("timestamp",timestamp)
    pieces = token.split(' ')
    if len(pieces) <= 1:
        return {'status':'error','message':'Cannot continue'}
    auth_type = pieces[0]
    if auth_type == 'DEV':
        params = pieces[1].split('.')
        partner_key = params[0].strip()
        dev_signature = params[1].strip()
        chain_id = int(request.registry.settings.get('chain_id'))
        """
        get key secret from database

        """
        message = "{0} {1} {2}".format(request.method.strip(),'/eth',timestamp)
        signature = create_signature(message,dev.secret)
        if dev_signature == signature:
            return True
    return Response(
            headerlist=[
                ('Cache-Control', 'public,max-age=0'),
                ('Content-Type', 'application/json; charset=utf-8'),
            ],
            status=401,
            body=json.dumps({'status': 'unauthenticated','message': 'user not authenticated'}),
        )


class WebsocketMapper(WebsocketConnectionView):
    __view_mapper__ = WSMapper

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)

@view_config(route_name='eth',mapper=WSMapper )
class Websocket(WebsocketConnectionView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.loop = asyncio.get_event_loop()
        self.counter = itertools.count()
        self.connected = False

    @asyncio.coroutine
    async def subscribe(self,args):

        async with websockets.connect(ws_provider) as websocket:
            r = await websocket.send(args)
            while self.connected:
                new_entries = await websocket.recv()
                print("resp", new_entries)
                if new_entries:
                    await self.ws.send(new_entries)


    def encode_rpc_request(self, method, params):
       rpc_dict = {
           "jsonrpc": "2.0",
           "method": method,
           "params": params or [],
           "id": next(self.counter),
       }
       encoded = FriendlyJsonSerde().json_encode(rpc_dict)
       return to_bytes(text=encoded)

    @asyncio.coroutine
    def on_open(self):
        headers = dict(self.request.headers)
        """
            implement auth mechanisim to avoid abuse
        """
        # if self.request.matchdict['token']:
        #     auth = is_authenticated(self.request,self.request.matchdict['token'],self.request.matchdict['timestamp'])
        #     if auth != True:
        #         yield from self.ws.send(json.dumps({'status':'error','message':'Not authorized'}))
        #         return auth
        #     self.connected = True
        #     print("Welcome client!")
        #     yield from self.ws.send(json.dumps({'status':'success','message': 'Authorization successful'}))
        self.connected = True
        print("Welcome client!")
        yield from self.ws.send(json.dumps({'status':'success','message': 'Welcome'}))

    @asyncio.coroutine
    def on_close(self):
        print("Goodbye...")
        self.connected = False

    @asyncio.coroutine
    async def on_message(self, data):
        params = data.decode('utf-8')
        print(params)
        try:
            params = json.loads(params).get('params')
        except:
            return {'status': 'error','message': 'could not decode data'}
        print(params)
        method = "eth_subscribe"
        #params = ["logs", {"address": "0x48878C1aE781F4b68e8EC951F35C113353DF81Ca", "topics": ["0xf7ad76543f114c7bb00ff2cd992ff749d502ed5c0c6f87901ad48f6871fceca1"]}]
        #params = ["newHeads", {"includeTransactions": 'true'}]
        args = self.encode_rpc_request(method,params)
        asyncio.ensure_future(self.subscribe(args),loop=self.loop)







