from .compiled import wtclient_pb2 as wtclient                # note: API docs call this wtclientrpc
from .compiled import wtclient_pb2_grpc as wtclientrpc        # note: API docs call this wtclientstub
from .common import BaseClient
from .errors import handle_rpc_errors



class WTClientRPC(BaseClient):

    def get_wtclient_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_wtclient_stub'):
            self._wtclient_stub = wtclientrpc.WatchtowerClientStub(self.channel)
        return self._wtclient_stub




    #not yet implemented
    pass