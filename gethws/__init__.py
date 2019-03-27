import logging.config

from pyramid.config import Configurator

from aiopyramid.websocket.helpers import ignore_websocket_closed


def main(global_config, **settings):

    # support logging in python3
    logging.config.fileConfig(
        settings["logging.config"], disable_existing_loggers=False
    )
    config = Configurator(settings=settings)
    config.include(".routes")
    config.scan()
    app = config.make_wsgi_app()
    return ignore_websocket_closed(app)
