from .compiled import neutrino_pb2 as neutrino                # note: API docs call this neutrinorpc
from .compiled import neutrino_pb2_grpc as neutrinorpc        # note: API docs call this neutrinostub
from .common import BaseClient
from .errors import handle_rpc_errors


class NeutrinoRPC(BaseClient):

    def get_neutrino_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_neutrino_stub'):
            self._neutrino_stub = neutrinorpc.NeutrinoKitStub(self.channel)
        return self._neutrino_stub

    @handle_rpc_errors
    def add_peer(self, peer_addrs):
        """
        AddPeer
        """
        request = neutrino.AddPeerRequest(peer_addrs=peer_addrs)
        response = self.get_neutrino_stub().AddPeer(request)
        return response

    @handle_rpc_errors
    def disconnect_peer(self, peer_addrs):
        """
        DisconnectPeer
        """
        request = neutrino.AddPeerRequest(peer_addrs=peer_addrs)
        response = self.get_neutrino_stub().AddPeer(request)
        return response


    @handle_rpc_errors
    def get_block_header(self, hash):
        """
        GetBlockHeader
        """
        request = neutrino.GetBlockHeaderRequest(hash=hash)
        response = self.get_neutrino_stub().GetBlockHeader(request)
        return response


    @handle_rpc_errors
    def get_cfilter(self, hash):
        """
        GetCFilter
        """
        request = neutrino.GetCFilterRequest(hash=hash)
        response = self.get_neutrino_stub().GetCFilter(request)
        return response

    @handle_rpc_errors
    def is_banned(self, peer_addrs):
        """
        IsBanned
        """
        request = neutrino.IsBannedRequest(peer_addrs=peer_addrs)
        response = self.get_neutrino_stub().IsBanned(request)
        return response

    @handle_rpc_errors
    def status(self):
        """
        Status
        """
        request = neutrino.StatusRequest()
        response = self.get_neutrino_stub().Status(request)
        return response