
from .common import BaseClient

from .router import RouterRPC
from .walletunlocker import WalletUnlockerRPC
from .walletkit import WalletRPC
from .versioner import VersionerRPC
from .signer import SignerRPC
from .lightning import LightningRPC
from .invoices import InvoicesRPC
from .peers import PeersRPC
from .dev import DevRPC
from .neutrinokit import NeutrinoRPC
from .autopilot import AutoPilotRPC
from .chainnotifier import ChainNotifierRPC
from .chainkit import ChainKitRPC
from .watchtower import WatchTowerRPC
from .watchtowerclient import WTClientRPC
from .state import StateRPC

class LNDClient(
    RouterRPC,
    WalletUnlockerRPC,
    WalletRPC,
    VersionerRPC,
    SignerRPC,
    LightningRPC,
    InvoicesRPC,
    PeersRPC,
    DevRPC,
    NeutrinoRPC,
    AutoPilotRPC,
    ChainNotifierRPC,
    ChainKitRPC,
    WatchTowerRPC,
    WTClientRPC,
    StateRPC
):
    pass


# def cli():
#     import code
#     # LNDClient gets all configuration parameters from environment variables!
#     lnd = LNDClient()

#     # Enter a shell for interacting with LND
#     code.interact(local=dict(globals(), **locals()))  