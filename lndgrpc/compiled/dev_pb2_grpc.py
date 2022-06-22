# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from lndgrpc.compiled import dev_pb2 as lndgrpc_dot_compiled_dot_dev__pb2
from lndgrpc.compiled import lightning_pb2 as lndgrpc_dot_compiled_dot_lightning__pb2


class DevStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ImportGraph = channel.unary_unary(
                '/devrpc.Dev/ImportGraph',
                request_serializer=lndgrpc_dot_compiled_dot_lightning__pb2.ChannelGraph.SerializeToString,
                response_deserializer=lndgrpc_dot_compiled_dot_dev__pb2.ImportGraphResponse.FromString,
                )


class DevServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ImportGraph(self, request, context):
        """
        ImportGraph imports a ChannelGraph into the graph database. Should only be
        used for development.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DevServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ImportGraph': grpc.unary_unary_rpc_method_handler(
                    servicer.ImportGraph,
                    request_deserializer=lndgrpc_dot_compiled_dot_lightning__pb2.ChannelGraph.FromString,
                    response_serializer=lndgrpc_dot_compiled_dot_dev__pb2.ImportGraphResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'devrpc.Dev', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Dev(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ImportGraph(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/devrpc.Dev/ImportGraph',
            lndgrpc_dot_compiled_dot_lightning__pb2.ChannelGraph.SerializeToString,
            lndgrpc_dot_compiled_dot_dev__pb2.ImportGraphResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
