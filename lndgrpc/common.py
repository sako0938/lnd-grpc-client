import binascii
import platform
import os
import grpc
import sys
from pathlib import Path

from lndgrpc.compiled import (
    lightning_pb2 as ln,
    lightning_pb2_grpc as lnrpc,
    router_pb2 as router,
    router_pb2_grpc as routerrpc,
    verrpc_pb2 as ver,
    verrpc_pb2_grpc as verrpc,
    walletkit_pb2 as walletkit,
    walletkit_pb2_grpc as walletkitrpc,
    signer_pb2 as signer,
    signer_pb2_grpc as signerrpc,
    walletunlocker_pb2 as walletunlocker,
    walletunlocker_pb2_grpc as walletunlockerrpc,
    invoices_pb2 as invoices,
    invoices_pb2_grpc as invoicesrpc,
)

system = platform.system().lower()

if system == 'linux':
    TLS_FILEPATH = os.path.expanduser('~/.lnd/tls.cert')
    ADMIN_MACAROON_BASE_FILEPATH = '~/.lnd/data/chain/bitcoin/{}/admin.macaroon'
    READ_ONLY_MACAROON_BASE_FILEPATH = '~/.lnd/data/chain/bitcoin/{}/readonly.macaroon'
elif system == 'darwin':
    TLS_FILEPATH = os.path.expanduser('~/Library/Application Support/Lnd/tls.cert')
    ADMIN_MACAROON_BASE_FILEPATH = '~/Library/Application Support/Lnd/data/chain/bitcoin/{}/admin.macaroon'
    READ_ONLY_MACAROON_BASE_FILEPATH = '~/Library/Application Support/Lnd/data/chain/bitcoin/{}/readonly.macaroon'
elif system == 'windows':
    TLS_FILEPATH = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'Lnd', 'tls.cert')
    ADMIN_MACAROON_BASE_FILEPATH = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'Lnd', 'data', 'chain', 'bitcoin', 'mainnet', 'admin.macaroon')
    READ_ONLY_MACAROON_BASE_FILEPATH = os.path.join(os.path.expanduser("~"), 'AppData', 'Local', 'Lnd', 'data', 'chain', 'bitcoin', 'mainnet', 'readonly.macaroon')
else:
    raise SystemError('Unrecognized system')


# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


def get_cert(filepath=None):
    """Read in tls.cert from file

    Note: tls files need to be read in byte mode as of grpc 1.8.2
          https://github.com/grpc/grpc/issues/13866
    """
    filepath = filepath or TLS_FILEPATH
    with open(filepath, 'rb') as f:
        cert = f.read()
    return cert


def get_macaroon(filepath=None):
    """Read and decode macaroon from file

    The macaroon is decoded into a hex string and returned.
    """
    if filepath is None:
        print("Must specify macaroon_filepath")
        sys.exit(1)

    with open(filepath, 'rb') as f:
        macaroon_bytes = f.read()
    return binascii.hexlify(macaroon_bytes).decode()


def generate_credentials(cert, macaroon):
    """Create composite channel credentials using cert and macaroon metadata"""
    # create cert credentials from the tls.cert file
    # if os.getenv("LND_HTTPS_TLS"):
    #     cert_creds = grpc.ssl_channel_credentials()
    # else:
    cert_creds = grpc.ssl_channel_credentials(cert)

    # build meta data credentials
    metadata_plugin = MacaroonMetadataPlugin(macaroon)
    auth_creds = grpc.metadata_call_credentials(metadata_plugin)

    # combine the cert credentials and the macaroon auth credentials
    # such that every call is properly encrypted and authenticated
    return grpc.composite_channel_credentials(cert_creds, auth_creds)


class MacaroonMetadataPlugin(grpc.AuthMetadataPlugin):
    """Metadata plugin to include macaroon in metadata of each RPC request"""

    def __init__(self, macaroon):
        self.macaroon = macaroon

    def __call__(self, context, callback):
        callback([('macaroon', self.macaroon)], None)


class BaseClient(object):
    grpc_module = grpc

    def __init__(
        self,
        ip_address=None,
        cert=None,
        cert_filepath=None,
        no_tls=False,
        macaroon=None,
        macaroon_filepath=None
    ):
        # Handle either passing in credentials_paths, or environment variable paths
        if macaroon_filepath is None:
            credential_path = os.getenv("LND_CRED_PATH", None)
            if credential_path == None:
                credential_path = Path.home().joinpath(".lnd")
                macaroon_filepath = str(credential_path.joinpath("data/chain/bitcoin/mainnet/admin.macaroon").absolute())
            else:
                credential_path = Path(credential_path)
                macaroon_filepath = str(credential_path.joinpath("admin.macaroon").absolute())

        if cert_filepath is None:
            credential_path = os.getenv("LND_CRED_PATH", None)
            credential_path = Path(credential_path)
            cert_filepath = str(credential_path.joinpath("tls.cert").absolute())

        if ip_address is None:
            node_ip = os.getenv("LND_NODE_IP")
            node_port = os.getenv("LND_NODE_PORT")
            ip_address = f"{node_ip}:{node_port}"

        # handle passing in credentials and cert directly
        if macaroon is None:
            macaroon = get_macaroon(filepath=macaroon_filepath)

        if cert is None and no_tls == False:
            cert = get_cert(cert_filepath)

        self._credentials = generate_credentials(cert, macaroon)
        self.ip_address = ip_address

    @property
    def _ln_stub(self):
        """Create a ln_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address,
            self._credentials, 
            # timeout=30,
            options=[('grpc.max_receive_message_length', 1024*1024*50), ("grpc.max_connection_idle_ms", 30000)]
        )
        return lnrpc.LightningStub(channel)

    @property
    def _router_stub(self):
        """Create a ln_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return routerrpc.RouterStub(channel)

    @property
    def _walletunlocker_stub(self):
        """Create a wallet_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return walletunlockerrpc.WalletUnlockerStub(channel)

    @property
    def _wallet_stub(self):
        """Create a wallet_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return lnrpc.WalletUnlockerStub(channel)

    @property
    def _walletkit_stub(self):
        """Create a wallet_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return walletkitrpc.WalletKitStub(channel)

    @property
    def _signer_stub(self):
        """Create a wallet_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return signerrpc.SignerStub(channel)


    @property
    def _version_stub(self):
        """Create a version_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return verrpc.VersionerStub(channel)

    @property
    def _invoices_stub(self):
        """Create a version_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return invoicesrpc.InvoicesStub(channel)

    @property
    def _invoices_servicer_stub(self):
        """Create a version_stub dynamically to ensure channel freshness

        If we make a call to the Lightning RPC service when the wallet
        is locked or the server is down we will get back an RPCError with
        StatusCode.UNAVAILABLE which will make the channel unusable.
        To ensure the channel is usable we create a new one for each request.
        """
        channel = self.grpc_module.secure_channel(
            self.ip_address, self._credentials, options=[('grpc.max_receive_message_length', 1024*1024*50)]
        )
        return invoicesrpc.InvoicesServicer(channel)
