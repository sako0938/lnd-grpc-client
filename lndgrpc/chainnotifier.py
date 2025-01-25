from .compiled import chainnotifier_pb2 as chainnotifier              # note: API docs call this chainrpc
from .compiled import chainnotifier_pb2_grpc as chainnotifierrpc      # note: API docs call this chainnotifierstub
from .common import BaseClient
from .errors import handle_rpc_errors

class ChainNotifierRPC(BaseClient):

    def get_chainnotifier_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_chainnotifier_stub'):
            self._chainnotifier_stub = chainnotifierrpc.ChainNotifierStub(self.channel)
        return self._chainnotifier_stub

    #not yet implemented
    pass