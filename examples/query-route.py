from pathlib import Path
import json
from pprint import pprint
import os
import base64
from time import sleep
from datetime import datetime, timedelta

# Pip installed Modules
from lndgrpc import LNDClient
from lndgrpc.client import ln
from protobuf_to_dict import protobuf_to_dict

credential_path = os.getenv("LND_CRED_PATH", None)
if credential_path == None:
	credential_path = Path.home().joinpath(".lnd")
	mac = str(credential_path.joinpath("data/chain/bitcoin/mainnet/admin.macaroon").absolute())
else:
	credential_path = Path(credential_path)
	mac = str(credential_path.joinpath("admin.macaroon").absolute())
	

node_ip = os.getenv("LND_NODE_IP")
node_port = os.getenv("LND_NODE_PORT")
tls = str(credential_path.joinpath("tls.cert").absolute())

lnd_ip_port = f"{node_ip}:{node_port}"

lnd = LNDClient(
	lnd_ip_port,
	macaroon_filepath=mac,
	cert_filepath=tls
	# no_tls=True
)

mypk = lnd.get_info().identity_pubkey

ignored = []

# from is a python keyword, so we gotta do something fancy here with kwargs
kwargs = {}
kwargs["from"] = bytes.fromhex("025093e0447f5f98ddaa0091e9e5720d0af7c582dcbf78c304364d19091f70fd0e")
kwargs["to"] = bytes.fromhex("020a1df50b701331a29782093210460b10eee0ac5ef6a01b9c51dff9b8fddf5fb0")
ignored.append(ln.NodePair(**kwargs))

fee_limit = ln.FeeLimit(fixed=11)


for i in range(50,1000,5):
    fee_limit = ln.FeeLimit(fixed=i)
    # Circular rebalance
    r = lnd.query_routes(
        pub_key=mypk,
        amt=100000,
        final_cltv_delta=40,
        fee_limit=fee_limit,
        # ignored_nodes=,
        # source_pub_key=,
        # ignored_pairs=ignored,
        cltv_limit=144,
        # outgoing_chan_id=695801744448487425,
        last_hop_pubkey=bytes.fromhex("020a1df50b701331a29782093210460b10eee0ac5ef6a01b9c51dff9b8fddf5fb0"),
    )
    try:
        print(r.routes[0].total_fees)
        break
    except AttributeError:
        pass


ignored = []
routes = []

for i in range(10,1000,5):
    fee_limit = ln.FeeLimit(fixed=i)
    # Circular rebalance
    r = lnd.query_routes(
        pub_key=mypk,
        amt=100000,
        final_cltv_delta=40,
        fee_limit=fee_limit,
        # ignored_nodes=,
        # source_pub_key=,
        ignored_pairs=ignored,
        cltv_limit=144,
        # outgoing_chan_id=695801744448487425,
        last_hop_pubkey=bytes.fromhex("03f9dc7982e336c1d4115459d59f40589db9db1a70adf741ed96584b79f60612cb"),
    )
    try:
        print(r.routes[0].total_fees)
        routes.append(r)
        kwargs = {}
        kwargs["from"] = bytes.fromhex(r.routes[0].hops[0].pub_key)
        kwargs["to"] = bytes.fromhex(r.routes[0].hops[1].pub_key)
        ignored.append(ln.NodePair(**kwargs))
        # break
    except AttributeError:
        pass




from hashlib import sha256
import secrets
preimageByteLength = 32
preimage = secrets.token_bytes(preimageByteLength)
m = sha256()
m.update(preimage)
preimage_hash = m.digest()

inv = lnd.add_invoice(100000,"rebalance test")
pr = lnd.decode_payment_request(inv.payment_request)
route = r.routes[0]
route.hops[-1].mpp_record.total_amt_msat = pr.num_msat
route.hops[-1].mpp_record.payment_addr = pr.payment_addr
lnd.send_to_route(
    pay_hash = bytes.fromhex(pr.payment_hash),
    route=route
)

# ln.list_channels().query("chan_id == 762928028804382736 | remote_pubkey == '037659a0ac8eb3b8d0a720114efc861d3a940382dcfa1403746b4f8f6b2e8810ba'")
