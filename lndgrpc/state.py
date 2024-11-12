from .compiled import stateservice_pb2 as stateservice                # note: API docs call this lnrpc (which is weird, maybe an error)
from .compiled import stateservice_pb2_grpc as stateservicerpc        # note: API docs call this stateservicestub
from .common import BaseClient
from .errors import handle_rpc_errors




class StateRPC(BaseClient):

    def get_state_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_state_stub'):
            self._state_stub = stateservicerpc.StateStub(self.channel)
        return self._state_stub

    @handle_rpc_errors
    def get_state(self):
        """
        GetState
        """
        response = self.get_state_stub().GetState(stateservice.GetStateRequest())
        return response

    @handle_rpc_errors
    def subscribe_state(self):
        """
        SubscribeState
        """
        response = self.get_state_stub().GetState(stateservice.SubscribeStateRequest())
        return response