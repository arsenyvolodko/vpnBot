import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from cybernexvpn.cybernexvpn_client.client_logging.adapter import Adapter


CONFIG_DIR = Path(__file__).parent
BASE_DIR = CONFIG_DIR.parent.parent


load_dotenv(BASE_DIR / ".env")


class Configuration(object):

    api_url = None
    api_key = None
    timeout = 10
    logger = None

    @staticmethod
    def configure(api_url: str, api_key: str, logger=None, **kwargs):
        Configuration.api_url = api_url
        Configuration.api_key = api_key
        Configuration.timeout = kwargs.get("timeout", 10)
        Configuration.configure_logger(logger)

        Configuration.assert_has_api_credentials()

    @staticmethod
    def configure_logger(logger):
        if isinstance(logger, logging.Logger):
            Configuration.logger = Adapter(logger, {"context": {}})

    @staticmethod
    def instantiate(**kwargs):
        configuration = Configuration()
        configuration.configure(
            api_key=os.environ.get("CYBERNEXVPN_CLIENT_API_KEY"),
            api_url=os.environ.get("CYBERNEXVPN_CLIENT_API_URL"),
            # logger=Configuration.logger,
            **kwargs
        )
        return configuration

    @staticmethod
    def assert_has_api_credentials():
        if not Configuration.api_url or not Configuration.api_key:
            raise ValueError("API URL and API Key must be set")
