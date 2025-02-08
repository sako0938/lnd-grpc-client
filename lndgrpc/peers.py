from .compiled import peers_pb2 as peers                # note: API docs call this peersrpc
from .compiled import peers_pb2_grpc as peersrpc        # note: API docs call this peersstub
from .common import BaseClient
from .errors import handle_rpc_errors




class PeersRPC(BaseClient):

    def get_peer_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_peer_stub'):
            self._peer_stub = peersrpc.PeersStub(self.channel)
        return self._peer_stub


    #not yet implemented
    pass