import sys
from .client import LNDClient
from .common import get_macaroon, get_cert
from lndgrpc.aio.async_client import AsyncLNDClient

MAJOR = sys.version_info[0]
MINOR = sys.version_info[1]

__version__ = "0.5.2"