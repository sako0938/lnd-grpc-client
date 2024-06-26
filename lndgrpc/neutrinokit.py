from .common import neutrino, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class NeutrinoRPC(BaseClient):
    @handle_rpc_errors
    def add_peer(self, peer_addrs):
        """
        AddPeer
        """
        request = neutrino.AddPeerRequest(peer_addrs=peer_addrs)
        response = self._neutrino_stub.AddPeer(request)
        return response

    @handle_rpc_errors
    def disconnect_peer(self, peer_addrs):
        """
        DisconnectPeer
        """
        request = neutrino.AddPeerRequest(peer_addrs=peer_addrs)
        response = self._neutrino_stub.AddPeer(request)
        return response


    @handle_rpc_errors
    def get_block_header(self, hash):
        """
        GetBlockHeader
        """
        request = neutrino.GetBlockHeaderRequest(hash=hash)
        response = self._neutrino_stub.GetBlockHeader(request)
        return response


    @handle_rpc_errors
    def get_cfilter(self, hash):
        """
        GetCFilter
        """
        request = neutrino.GetCFilterRequest(hash=hash)
        response = self._neutrino_stub.GetCFilter(request)
        return response

    @handle_rpc_errors
    def is_banned(self, peer_addrs):
        """
        IsBanned
        """
        request = neutrino.IsBannedRequest(peer_addrs=peer_addrs)
        response = self._neutrino_stub.IsBanned(request)
        return response

    @handle_rpc_errors
    def status(self):
        """
        Status
        """
        request = neutrino.StatusRequest()
        response = self._neutrino_stub.Status(request)
        return response