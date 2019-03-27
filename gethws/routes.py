def includeme(config):
    # root
    config.add_route("root", "/")
    # WS
    config.add_route("eth", "/eth")
    config.add_route("balance", "/eth_balance/{address}")
