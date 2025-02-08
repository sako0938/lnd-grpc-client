from .compiled import chainkit_pb2 as chainkit                # note: API docs call this chainrpc (which is weird because it is the same as chainnotifier)
from .compiled import chainkit_pb2_grpc as chainkitrpc        # note: API docs call this chainkitstub
from .common import BaseClient
from .errors import handle_rpc_errors


class ChainKitRPC(BaseClient):

    def get_chainkit_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_chainkit_stub'):
            self._chainkit_stub = chainkitrpc.ChainKitStub(self.channel)
        return self._chainkit_stub

    @handle_rpc_errors
    def get_block(self,block_hash):
        request = chainkit.GetBlockRequest(block_hash=block_hash)
        response = self.get_chainkit_stub().GetBlock(request)
        return response

    @handle_rpc_errors
    def get_best_block(self):
        request = chainkit.GetBestBlockRequest()
        response = self.get_chainkit_stub().GetBestBlock(request)
        return response

    @handle_rpc_errors
    def get_block_hash(self,block_height):
        request = chainkit.GetBlockHashRequest(block_height=block_height)
        response = self.get_chainkit_stub().GetBlockHash(request)
        return response



