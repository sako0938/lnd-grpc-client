from .compiled import walletkit_pb2 as walletkit                # note: API docs call this walletrpc
from .compiled import walletkit_pb2_grpc as walletkitrpc        # note: API docs call this walletkitstub
from .common import BaseClient
from .errors import handle_rpc_errors




class WalletRPC(BaseClient):

    def get_walletkit_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_walletkit_stub'):
            self._walletkit_stub = walletkitrpc.WalletKitStub(self.channel)
        return self._walletkit_stub

    @handle_rpc_errors
    def bump_fee(self, outpoint, sat_per_vbyte, force=False):
        """
        BumpFee
        """
        txid_str, output_index = outpoint.split(":")
        outpoint_obj = ln.OutPoint(txid_str=txid_str, output_index=int(output_index))
        request = walletkit.BumpFeeRequest(
            outpoint=outpoint_obj,
            sat_per_vbyte=sat_per_vbyte,
            force=force,
        )
        response = self.get_walletkit_stub().BumpFee(request)
        return response

    @handle_rpc_errors
    def estimate_fee(self, conf_target):
        """
        EstimateFee
        """
        request = walletkit.EstimateFeeRequest(conf_target=conf_target)
        response = self.get_walletkit_stub().EstimateFee(request)
        return response


    @handle_rpc_errors
    def next_addr(self, account="", address_type=1, change=False):
        request = walletkit.AddrRequest(
            account=account,
            type=address_type,
            change=change
        )
        response = self.get_walletkit_stub().NextAddr(request)
        return response

    @handle_rpc_errors
    def list_accounts(self, **kwargs):
        request = walletkit.ListAccountsRequest(**kwargs)
        response = self.get_walletkit_stub().ListAccounts(request)
        return response

    @handle_rpc_errors
    def list_unspent(self, min_confs=0,max_confs=100000, **kwargs):
        # Default to these min/max for convenience
        request = walletkit.ListUnspentRequest(min_confs=min_confs, max_confs=max_confs, **kwargs)
        response = self.get_walletkit_stub().ListUnspent(request)
        return response

    @handle_rpc_errors
    def label_transaction(self, txid, label, overwrite=False):
        """
        Label an on-chain txn known to the wallet
            txid: hex-string
            label: string
            overwrite: bool
        """
        request = walletkit.LabelTransactionRequest(txid=bytes.fromhex(txid)[::-1], label=label, overwrite=overwrite)
        response = self.get_walletkit_stub().LabelTransaction(request)
        return response

    @handle_rpc_errors
    def publish_transaction(self, tx_hex, label=""):
        # Default to these min/max for convenience
        request = walletkit.Transaction(tx_hex=tx_hex, label=label)
        response = self.get_walletkit_stub().PublishTransaction(request)
        return response

    @handle_rpc_errors
    def fund_psbt(self, psbt, raw, **kwargs):
        # Default to these min/max for convenience
        request = walletkit.FundPsbtRequest(psbt=psbt, raw=raw, **kwargs)
        response = self.get_walletkit_stub().FundPsbt(request)
        return response

    @handle_rpc_errors
    def finalize_psbt(self, signed_psbt, raw_final_tx):
        # Default to these min/max for convenience
        request = walletkit.FinalizePsbtRequest(
            signed_psbt=signed_psbt,
            raw_final_tx=raw_final_tx
        )
        response = self.get_walletkit_stub().FinalizePsbt(request)
        return response


    @handle_rpc_errors
    def list_sweeps(self, verbose=True):
        """
        ListSweeps
        """
        request = walletkit.ListSweepsRequest(verbose=verbose)
        response = self.get_walletkit_stub().ListSweeps(request)
        return response

    @handle_rpc_errors
    def pending_sweeps(self):
        """
        PendingSweeps
        """
        request = walletkit.PendingSweepsRequest()
        response = self.get_walletkit_stub().PendingSweeps(request)
        return response

    @handle_rpc_errors
    def list_leases(self):
        """
        ListLeases
        """
        request = walletkit.ListLeasesRequest()
        response = self.get_walletkit_stub().ListLeases(request)
        return response

    @handle_rpc_errors
    def required_reserve(self, additional_public_channels=0):
        """
        RequiredReserve
        """
        request = walletkit.RequiredReserveRequest(additional_public_channels=additional_public_channels)
        response = self.get_walletkit_stub().RequiredReserve(request)
        return response
