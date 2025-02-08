from .compiled import walletunlocker_pb2 as walletunlocker               # note: API docs call this lnrpc (which is weird, maybe an error)
from .compiled import walletunlocker_pb2_grpc as walletunlockerrpc       # note: API docs call this walletunlockerstub
from .common import BaseClient
from .errors import handle_rpc_errors




class WalletUnlockerRPC(BaseClient):

    def get_walletunlocker_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_walletunlocker_stub'):
            self._walletunlocker_stub = walletunlockerrpc.WalletUnlockerStub(self.channel)
        return self._walletunlocker_stub

    #WALLETUNLOCKERRPC
    @handle_rpc_errors
    def unlock(self, password):
        """Unlock encrypted wallet at lnd startup"""
        request = walletunlocker.UnlockWalletRequest(wallet_password=password.encode())
        response = self.get_walletunlocker_stub().UnlockWallet(request)
        return response

    @handle_rpc_errors
    def init_wallet(self, **kwargs):
        request = walletunlocker.InitWalletRequest(**kwargs)
        response = self.get_walletunlocker_stub().InitWallet(request)
        return response

    @handle_rpc_errors
    def gen_seed(self, aezeed_passphrase, seed_entropy):
        request = walletunlocker.GenSeedRequest(
            aezeed_passphrase=aezeed_passphrase,
            seed_entropy=seed_entropy
        )
        response = self.get_walletunlocker_stub().GenSeed(request)
        return response

    @handle_rpc_errors
    def change_password(self, current_password, new_password, stateless_init, new_macaroon_root_key):
        request = walletunlocker.ChangePasswordRequest(
            current_password=current_password,
            new_password=new_password,
            stateless_init=stateless_init,
            new_macaroon_root_key=new_macaroon_root_key
        )
        response = self.get_walletunlocker_stub().ChangePassword(request)
        return response
    
    @handle_rpc_errors
    def unlock_wallet(self, **kwargs):
        request = walletunlocker.UnlockWalletRequest(**kwargs)
        try:
            response = self.get_walletunlocker_stub().UnlockWallet(request)
            return response
        except Exception as e:
            print(e)
            print("Wallet might already be unlocked")