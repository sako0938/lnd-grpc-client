from .compiled import verrpc_pb2 as ver                # note: API docs call this verrpc
from .compiled import verrpc_pb2_grpc as verrpc        # note: API docs call this verrpcstub
from .common import BaseClient
from .errors import handle_rpc_errors




class VersionerRPC(BaseClient):

    def get_version_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_version_stub'):
            self._version_stub = verrpc.VersionerStub(self.channel)
        return self._version_stub

    @handle_rpc_errors
    def get_version(self, **kwargs):
        """
        GetVersion
        """
        request = ver.VersionRequest()
        response = self.get_version_stub().GetVersion(request)
        return response
