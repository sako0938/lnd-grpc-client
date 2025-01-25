from .compiled import watchtower_pb2 as watchtower                # note: API docs call this watchtowerrpc
from .compiled import watchtower_pb2_grpc as watchtowerrpc        # note: API docs call this watchtowerstub
from .common import BaseClient
from .errors import handle_rpc_errors



class WatchTowerRPC(BaseClient):

    def get_watchtower_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_watchtower_stub'):
            self._watchtower_stub = watchtowerrpc.WatchtowerStub(self.channel)
        return self._watchtower_stub

    @handle_rpc_errors
    def wt_get_info(self, **kwargs):
        """
        GetInfo
        """
        response = self.get_watchtower_stub().GetInfo(watchtower.GetInfoRequest())
        return response