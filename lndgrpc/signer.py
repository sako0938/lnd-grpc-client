from .compiled import signer_pb2 as signer                # note: API docs call this signrpc
from .compiled import signer_pb2_grpc as signerrpc        # note: API docs call this signerstub
from .common import BaseClient
from .errors import handle_rpc_errors




class SignerRPC(BaseClient):

    def get_signer_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_signer_stub'):
            self._signer_stub = signerrpc.SignerStub(self.channel)
        return self._signer_stub

    # SIGNERRPC
    @handle_rpc_errors
    def signer_sign_message(self, msg, key_family, key_index):
        key_loc = signer.KeyLocator(key_family=key_family,key_index=key_index)
        request = signer.SignMessageReq(
            msg=msg,
            key_loc=key_loc
        )
        response = self.get_signer_stub().SignMessage(request)
        return response

    @handle_rpc_errors
    def signer_verify_message(self, msg, signature, pubkey):
        request = signer.VerifyMessageReq(
            msg=msg,
            signature=signature,
            pubkey=pubkey
        )
        response = self.get_signer_stub().VerifyMessage(request)
        return response