from .common import walletkit, ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class WalletRPC(BaseClient):
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
        response = self._walletkit_stub.BumpFee(request)
        return response

    @handle_rpc_errors
    def estimate_fee(self, conf_target):
        """
        EstimateFee
        """
        request = walletkit.EstimateFeeRequest(conf_target=conf_target)
        response = self._walletkit_stub.EstimateFee(request)
        return response


    @handle_rpc_errors
    def next_addr(self, account="", address_type=1, change=False):
        request = walletkit.AddrRequest(
            account=account,
            type=address_type,
            change=change
        )
        response = self._walletkit_stub.NextAddr(request)
        return response

    @handle_rpc_errors
    def list_accounts(self, **kwargs):
        request = walletkit.ListAccountsRequest(**kwargs)
        response = self._walletkit_stub.ListAccounts(request)
        return response
    
    @handle_rpc_errors
    def list_addresses(self, **kwargs):
        """
        ListAddresses
        """
        request = walletkit.ListAddressesRequest(**kwargs)
        response = self._walletkit_stub.ListAddresses(request)
        return response

    @handle_rpc_errors
    def list_unspent(self, min_confs=0,max_confs=100000, **kwargs):
        # Default to these min/max for convenience
        request = walletkit.ListUnspentRequest(min_confs=min_confs, max_confs=max_confs, **kwargs)
        response = self._walletkit_stub.ListUnspent(request)
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
        response = self._walletkit_stub.LabelTransaction(request)
        return response

    @handle_rpc_errors
    def publish_transaction(self, tx_hex, label=""):
        # Default to these min/max for convenience
        request = walletkit.Transaction(tx_hex=tx_hex, label=label)
        response = self._walletkit_stub.PublishTransaction(request)
        return response

    @handle_rpc_errors
    def fund_psbt(self, psbt, raw, **kwargs):
        # Default to these min/max for convenience
        request = walletkit.FundPsbtRequest(psbt=psbt, raw=raw, **kwargs)
        response = self._walletkit_stub.FundPsbt(request)
        return response

    @handle_rpc_errors
    def finalize_psbt(self, signed_psbt, raw_final_tx):
        # Default to these min/max for convenience
        request = walletkit.FinalizePsbtRequest(
            signed_psbt=signed_psbt,
            raw_final_tx=raw_final_tx
        )
        response = self._walletkit_stub.FinalizePsbt(request)
        return response


    @handle_rpc_errors
    def list_sweeps(self, verbose=True):
        """
        ListSweeps
        """
        request = walletkit.ListSweepsRequest(verbose=verbose)
        response = self._walletkit_stub.ListSweeps(request)
        return response

    @handle_rpc_errors
    def pending_sweeps(self):
        """
        PendingSweeps
        """
        request = walletkit.PendingSweepsRequest()
        response = self._walletkit_stub.PendingSweeps(request)
        return response

    @handle_rpc_errors
    def list_leases(self):
        """
        ListLeases
        """
        request = walletkit.ListLeasesRequest()
        response = self._walletkit_stub.ListLeases(request)
        return response

    @handle_rpc_errors
    def required_reserve(self, additional_public_channels=0):
        """
        RequiredReserve
        """
        request = walletkit.RequiredReserveRequest(additional_public_channels=additional_public_channels)
        response = self._walletkit_stub.RequiredReserve(request)
        return response