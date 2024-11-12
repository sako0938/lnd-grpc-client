from .compiled import dev_pb2 as dev                # note: API docs call this devrpc
from .compiled import dev_pb2_grpc as devrpc        # note: API docs call this devstub
from .common import BaseClient
from .errors import handle_rpc_errors


class DevRPC(BaseClient):

    def get_dev_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_dev_stub'):
            self._dev_stub = devrpc.DevStub(self.channel)
        return self._dev_stub

    @handle_rpc_errors
    def import_graph(self, nodes, edges):
        """
        ImportGraph
        """
        request = dev.ChannelGraph(
            nodes=nodes,
            edges=edges
        )
        response = self.get_dev_stub().ImportGraph(request)
        return response