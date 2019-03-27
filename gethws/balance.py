import asyncio
import json
import uuid
from decimal import Decimal
import configparser

from pyramid.view import view_config
from aiopyramid.websocket.view import WebsocketConnectionView
from web3 import Web3, HTTPProvider


try:
    from aiopyramid.websocket.config import UWSGIWebsocketMapper
    WSMapper = UWSGIWebsocketMapper
    WSMapper.use_bytes = True
except ImportError:
    from aiopyramid.websocket.config import WebsocketMapper
    WSMapper = WebsocketMapper


config = configparser.ConfigParser()

if not config.read("GethWS.ini"):
    raise config.Error("Could not open %s" % config)


http_provider = config.get("app:main", "http_provider")

web3_provider = HTTPProvider(http_provider)

web3 = Web3(web3_provider)

poll_interval = 3


@view_config(route_name="root", renderer="json")
@asyncio.coroutine
def root(request):
    wait_time = float(request.params.get("sleep", 0.5))
    yield from asyncio.sleep(wait_time)
    return {"GETH WS": "0.1.0", "url": request.application_url}


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


@view_config(route_name="balance", mapper=WSMapper)
class Websocket(WebsocketConnectionView):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.wallet_address = "0x0"
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.connected = False

    @asyncio.coroutine
    def get_balance(self):
        if web3.isAddress(self.wallet_address):
            return web3.eth.getBalance(self.wallet_address, "pending")
        return 0

    @asyncio.coroutine
    def printBalance(self, pid):
        b = 0
        while self.connected:
            yield from asyncio.sleep(poll_interval)
            a = yield from self.get_balance()
            if a != b:
                formatted_balance = web3.fromWei(a, "ether")
                yield from self.ws.send(
                    json.dumps(
                        {
                            "eth_balance": a,
                            "formatted_balance": "{:,.4f}".format(formatted_balance),
                        },
                        cls=DecimalEncoder,
                    )
                )
            b = yield from self.get_balance()

    @asyncio.coroutine
    def on_open(self):
        if self.request.matchdict["address"] and web3.isAddress(
            self.request.matchdict["address"]
        ):
            self.wallet_address = self.request.matchdict["address"]
            pid = uuid.uuid4()
            print("Welcome ", pid)
            self.connected = True
            asyncio.ensure_future(self.printBalance(pid))

    @asyncio.coroutine
    def on_message(self, data):
        if data.decode("utf-8"):
            message = data.decode("utf-8")
            if message == "__ping__":
                yield from self.ws.send(json.dumps({"message": "__pong__"}))

    @asyncio.coroutine
    def on_close(self):
        print("Goodbye...")
        self.connected = False
