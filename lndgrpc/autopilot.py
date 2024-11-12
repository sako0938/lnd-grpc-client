from .compiled import autopilot_pb2 as autopilot                # note: API docs call this autopilotrpc
from .compiled import autopilot_pb2_grpc as autopilotrpc        # note: API docs call this autopilotstub
from .common import BaseClient
from .errors import handle_rpc_errors



class AutoPilotRPC(BaseClient):

    def get_autopilot_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_autopilot_stub'):
            self._autopilot_stub = autopilotrpc.AutopilotStub(self.channel)
        return self._autopilot_stub

    @handle_rpc_errors
    def modify_status(self):
        """
        ModifyStatus
        """
        response = self.get_autopilot_stub().GetState(stateservice.GetStateRequest())
        return response

    @handle_rpc_errors
    def query_scores(self):
        """
        QueryScores
        """
        response = self.get_autopilot_stub().GetState(stateservice.GetStateRequest())
        return response

    @handle_rpc_errors
    def set_scores(self):
        """
        SetScores
        """
        response = self.get_autopilot_stub().GetState(stateservice.GetStateRequest())
        return response


    @handle_rpc_errors
    def status(self):
        """
        Status
        """
        response = self.get_autopilot_stub().Status(autopilot.StatusRequest())
        return response