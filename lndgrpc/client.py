from datetime import datetime
import binascii

from .common import walletunlocker, ver, walletkit, signer, router, ln, BaseClient, invoices
from .errors import handle_rpc_errors

from lndgrpc.router import RouterRPC
from lndgrpc.walletunlocker import WalletUnlockerRPC
from lndgrpc.walletkit import WalletRPC
from lndgrpc.versioner import VersionerRPC
from lndgrpc.signer import SignerRPC
from lndgrpc.lightning import LightningRPC
from lndgrpc.invoices import InvoicesRPC
from lndgrpc.peers import PeersRPC
from lndgrpc.dev import DevRPC
from lndgrpc.neutrinokit import NeutrinoRPC
from lndgrpc.autopilot import AutoPilotRPC
from lndgrpc.chainnotifier import ChainNotifierRPC
from lndgrpc.chainkit import ChainKitRPC
from lndgrpc.watchtower import WatchTowerRPC
from lndgrpc.watchtowerclient import WTClientRPC
from lndgrpc.state import StateRPC

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