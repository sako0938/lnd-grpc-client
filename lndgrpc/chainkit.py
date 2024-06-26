from .common import chainkit, BaseClient
from .errors import handle_rpc_errors


class ChainKitRPC(BaseClient):

    @handle_rpc_errors
    def get_block(self,block_hash):
        request = chainkit.GetBlockRequest(block_hash=block_hash)
        response = self._chainkit_stub.GetBlock(request)
        return response

    @handle_rpc_errors
    def get_best_block(self):
        request = chainkit.GetBestBlockRequest()
        response = self._chainkit_stub.GetBestBlock(request)
        return response

    @handle_rpc_errors
    def get_block_hash(self,block_height):
        request = chainkit.GetBlockHashRequest(block_height=block_height)
        response = self._chainkit_stub.GetBlockHash(request)
        return response



