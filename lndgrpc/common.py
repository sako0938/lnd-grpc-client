import binascii
import os
import grpc
import sys
from pathlib import Path

from urllib.parse import urlparse,parse_qs
from base64 import urlsafe_b64decode
from cryptography.x509 import load_der_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


# Due to updated ECDSA generated tls.cert we need to let gprc know that
# we need to use that cipher suite otherwise there will be a handhsake
# error when we communicate with the lnd rpc server.
os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'


def get_cert(filepath=None):
    """Read in tls.cert from file

    Note: tls files need to be read in byte mode as of grpc 1.8.2
          https://github.com/grpc/grpc/issues/13866
    """
    filepath = filepath
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
        host=None,
        cert=None,
        cert_filepath=None,
        no_tls=False,
        macaroon=None,
        macaroon_filepath=None
    ):


        ###### Credentials Using Environmental Variables ######

        # # CASE 1: A folder with tls.cert, and admin.macaroon
        # export LND_CRED_PATH=/home/user/creds/my_favorite_node/lnd

        credential_path = os.getenv("LND_CRED_PATH", None)
        lnd_macaroon = os.getenv("LND_MACAROON", "admin.macaroon") 


        # # CASE 2: Running directly on a machine running LND
        # export LND_ROOT_DIR=/home/user/.lnd
        # export LND_NETWORK=mainnet

        root_dir = os.getenv("LND_ROOT_DIR", None)
        network = os.getenv("LND_NETWORK", None)

        if credential_path:
            credential_path = Path(credential_path)
            macaroon_filepath = str(credential_path.joinpath(lnd_macaroon).absolute())
            cert_filepath = str(credential_path.joinpath("tls.cert").absolute())

        elif root_dir and network:
            macaroon_filepath = str(root_dir.joinpath(f"data/chain/bitcoin/{network}/admin.macaroon").absolute())
            cert_filepath = str(root_dir.joinpath("tls.cert").absolute())


        ###### Credentials Using Variables Passed On Object Creation ######

        elif (macaroon_filepath and cert_filepath) or (macaroon and cert):
            pass

        elif host.startswith('lndconnect://'):
            pass

        else:
            print("Missing credentials!")
            sys.exit(1)


        ###### Define Host Using Environmental Variables ######

        node_ip = os.getenv("LND_NODE_IP")
        node_port = os.getenv("LND_NODE_PORT")


        ###### Define Host Using Variables Passed On Object Creation ######

        if host is None:
            host = f"{node_ip}:{node_port}"

        elif host.startswith('lndconnect://'):      # get both host and credentials from host

            ParsedLNDConnect=urlparse(host)
            ParsedLNDConnectQuery=parse_qs(ParsedLNDConnect.query)

            # when decoding the macaroon (and also the cert below), add  +'=='  because https://github.com/LN-Zap/lndconnect/
            # doesn't seem to properly pad the encoded data and python's `urlsafe_b64decode` will automatically ignore
            # any extra padding so can just add the max padding all the time.
            macaroon=urlsafe_b64decode(ParsedLNDConnectQuery['macaroon'][0]+'==').hex()

            # probably more complicated than just doing a simple encoding conversion but couldn't find any simple example or module to do that.
            # since the PEM data with the header and footer removed and then decoded is just DER data, read that in
            ProcessedCertificate=load_der_x509_certificate(urlsafe_b64decode(ParsedLNDConnectQuery['cert'][0]+'=='),default_backend())

            # then export it back out using normal PEM format, which is what GRPC is expecting.
            cert=ProcessedCertificate.public_bytes(encoding=serialization.Encoding.PEM)

            # now overwrite with just the actual host
            host=ParsedLNDConnect.netloc


        # handle passing in credentials and cert directly
        if macaroon is None:
            macaroon = get_macaroon(filepath=macaroon_filepath)

        if cert is None and no_tls == False:
            cert = get_cert(cert_filepath)

        self._credentials = generate_credentials(cert, macaroon)
        self.host = host

        self.channel = self.grpc_module.secure_channel(
                        self.host,
                        self._credentials, 
                        options =   [
                                        ('grpc.max_receive_message_length', 1024*1024*50),

                                        # if there aren't any calls for 30 seconds, then allow the server to disconnect.
                                        ("grpc.max_connection_idle_ms", 30000),

                                        # send keep alive pings so that streaming calls will not hang if the TCP socket is broken.
                                        # min value is 300001 until the fix for https://github.com/lightningnetwork/lnd/issues/7727 is in production.
                                        # this currently results in up to 5 minute delay on reconnection if the TCP socket is broken.
                                        ("grpc.keepalive_time_ms",300001),

                                        # set no limit on the number of keepalive pings that can be sent
                                        ('grpc.http2.max_pings_without_data', 0)
                                    ]
                         )

