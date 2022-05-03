from .common import walletunlocker, ver, walletkit, signer, router, ln, BaseClient, invoices
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class LNDClient(BaseClient):

    #WALLETUNLOCKERRPC
    def unlock(self, password):
        """Unlock encrypted wallet at lnd startup"""
        request = ln.UnlockWalletRequest(wallet_password=password.encode())
        response = self._wallet_stub.UnlockWallet(request)
        return response

    def init_wallet(self, **kwargs):
        request = walletunlocker.InitWalletRequest(**kwargs)
        response = self._walletunlocker_stub.InitWallet(request)
        return response

    def gen_seed(self, aezeed_passphrase, seed_entropy):
        request = walletunlocker.GenSeedRequest(
            aezeed_passphrase=aezeed_passphrase,
            seed_entropy=seed_entropy
        )
        response = self._walletunlocker_stub.GenSeed(request)
        return response

    def change_password(self, current_password, new_password, stateless_init, new_macaroon_root_key):
        request = walletunlocker.ChangePasswordRequest(
            current_password=current_password,
            new_password=new_password,
            stateless_init=stateless_init,
            new_macaroon_root_key=new_macaroon_root_key
        )
        response = self._walletunlocker_stub.ChangePassword(request)
        return response
    
    @handle_rpc_errors
    def unlock_wallet(self, **kwargs):
        request = walletunlocker.UnlockWalletRequest(**kwargs)
        try:
            response = self._walletunlocker_stub.UnlockWallet(request)
            return response
        except Exception as e:
            print(e)
            print("Wallet might already be unlocked")


    #WALLETRPC
    @handle_rpc_errors
    def next_addr(self, account=""):
        request = walletkit.AddrRequest(account=account)
        response = self._walletkit_stub.NextAddr(request)
        return response

    @handle_rpc_errors
    def list_accounts(self, **kwargs):
        request = walletkit.ListAccountsRequest(**kwargs)
        response = self._walletkit_stub.ListAccounts(request)
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


    #VERRPC
    @handle_rpc_errors
    def get_version(self, **kwargs):
        request = ver.VersionRequest()
        response = self._version_stub.GetVersion(request)
        return response

    # ROUTERRPC
    @handle_rpc_errors
    def build_route(self, amt_msat, oid, hop_pubkeys, **kwargs):
        hop_pubkeys_bytes = [ bytes.fromhex(pk) for pk in hop_pubkeys ]
        hop_pubkeys_check = [ pk.hex() for pk in hop_pubkeys_bytes ]
        #print(hop_pubkeys_bytes)
        #print("\n".join(map(str, hop_pubkeys_check)))

        request = router.BuildRouteRequest(
            amt_msat=amt_msat,
            outgoing_chan_id=oid,
            hop_pubkeys=hop_pubkeys_bytes,
            final_cltv_delta=400,
            **kwargs
        )
        try:
            response = self._router_stub.BuildRoute(request)
        except Exception as error:
            print(error)

        return response

    @handle_rpc_errors
    def send_to_route(self, pay_hash, route):
        request = router.SendToRouteRequest(
            payment_hash=pay_hash,
            route=route,
        )

        response = self._router_stub.SendToRouteV2(request)
        return response

    @handle_rpc_errors
    def send_payment_v2(self, **kwargs):
        request = router.SendPaymentRequest(**kwargs)
        responses = []
        for response in self._router_stub.SendPaymentV2(request):
            responses.append(response)
        return responses

    @handle_rpc_errors
    def send_payment_v1(self, **kwargs):
        request = router.SendPaymentRequest(**kwargs)
        response = self._router_stub.SendPayment(request)
        return response

    @handle_rpc_errors
    def reset_mission_control(self):
        request = router.ResetMissionControlRequest()
        response = self._router_stub.ResetMissionControl(request)
        return response


    # SIGNERRPC
    @handle_rpc_errors
    def signer_sign_message(self, msg, key_family, key_index):
        key_loc = signer.KeyLocator(key_family=key_family,key_index=key_index)
        request = signer.SignMessageReq(
            msg=msg,
            key_loc=key_loc
        )
        response = self._signer_stub.SignMessage(request)
        return response

    @handle_rpc_errors
    def signer_verify_message(self, msg, signature, pubkey):
        request = signer.VerifyMessageReq(
            msg=msg,
            signature=signature,
            pubkey=pubkey
        )
        response = self._signer_stub.VerifyMessage(request)
        return response


    # LIGHTNINGRPC
    @handle_rpc_errors
    def get_info(self):
        response = self._ln_stub.GetInfo(ln.GetInfoRequest())
        return response

    @handle_rpc_errors
    def bake_macaroon(self, permissions, root_key_id, allow_external_permissions=False):
        response = self._ln_stub.BakeMacaroon(
            ln.BakeMacaroonRequest(
                permissions=permissions,
                root_key_id=root_key_id,
                allow_external_permissions=allow_external_permissions
            )
        )
        return response

    @handle_rpc_errors
    def list_macaroon_ids(self):
        response = self._ln_stub.ListMacaroonIDs(ln.ListMacaroonIDsRequest())
        return response

    @handle_rpc_errors
    def forwarding_history(self, **kwargs):
        response = self._ln_stub.ForwardingHistory(ln.ForwardingHistoryRequest(**kwargs))
        return response

    @handle_rpc_errors
    def wallet_balance(self):
        response = self._ln_stub.WalletBalance(ln.WalletBalanceRequest())
        return response

    @handle_rpc_errors
    def channel_balance(self):
        response = self._ln_stub.ChannelBalance(ln.ChannelBalanceRequest())
        return response

    @handle_rpc_errors
    def list_peers(self):
        """List all active, currently connected peers"""
        response = self._ln_stub.ListPeers(ln.ListPeersRequest())
        return response

    @handle_rpc_errors
    def list_permissions(self):
        """List all permissions available"""
        response = self._ln_stub.ListPermissions(ln.ListPermissionsRequest())
        return response

    @handle_rpc_errors
    def get_transactions(self, start_height, end_height, **kwargs):
        """List all open channels"""
        request = ln.GetTransactionsRequest(
            start_height=start_height,
            end_height=end_height,
            **kwargs,
        )
        response = self._ln_stub.GetTransactions(request)
        return response

    @handle_rpc_errors
    def list_channels(self, **kwargs):
        """List all open channels"""
        response = self._ln_stub.ListChannels(ln.ListChannelsRequest(**kwargs))
        return response

    @handle_rpc_errors
    def abandon_channel(self, **kwargs):
        """ ***danger*** Abandon a channel"""
        response = self._ln_stub.AbandonChannel(ln.AbandonChannelRequest(**kwargs))
        return response

    @handle_rpc_errors
    def export_all_channel_backups(self):
        """List all open channels"""
        request = ln.ChanBackupExportRequest()
        response = self._ln_stub.ExportAllChannelBackups(request)
        return response

    @handle_rpc_errors
    def export_channel_backup(self, chan_point):
        """List all open channels"""
        request = ln.ExportChannelBackupRequest(
            chan_point=chan_point
        )
        response = self._ln_stub.ExportChannelBackup(request)
        return response

    @handle_rpc_errors
    def restore_channel_backups(self, chan_backups=None, multi_chan_backup=None):
        """List all open channels"""
        request = ln.RestoreChanBackupRequest(
            chan_backups=chan_backups,
            multi_chan_backup=multi_chan_backup
        )
        response = self._ln_stub.RestoreChannelBackups(request)
        return response

    @handle_rpc_errors
    def get_recovery_info(self):
        """List all open channels"""
        request = ln.GetRecoveryInfoRequest()
        response = self._ln_stub.GetRecoveryInfo(request)
        return response

    @handle_rpc_errors
    def open_channel(self, node_pubkey, local_funding_amount, sat_per_byte, **kwargs):
        """Open a channel to an existing peer"""
        request = ln.OpenChannelRequest(
            node_pubkey=bytes.fromhex(node_pubkey),
            local_funding_amount=local_funding_amount,
            sat_per_byte=sat_per_byte,
            **kwargs
        )
        last_response = None
        start = datetime.now().timestamp()
        for r in self._ln_stub.OpenChannel(request, timeout=30):
            return r
            last_response = r
            print(last_response)
            if datetime.now().timestamp() > 5:
                return last_response

        #     print(response)
        #     last_response = response
        # return response

    @handle_rpc_errors
    def list_invoices(self, **kwargs):
        request = ln.ListInvoiceRequest(**kwargs)
        response = self._ln_stub.ListInvoices(request)
        return response

    @handle_rpc_errors
    def funding_state_step(self, shim_register=None, shim_cancel=None, psbt_verify=None, psbt_finalize=None):
        request = ln.FundingTransitionMsg(shim_register=shim_register, shim_cancel=shim_cancel, psbt_verify=psbt_verify, psbt_finalize=psbt_finalize)
        response = self._ln_stub.FundingStateStep(request)
        return response

    @handle_rpc_errors
    def subscribe_invoices(self):
        for invoice in self._ln_stub.SubscribeInvoices(ln.InvoiceSubscription()):
            yield invoice

    @handle_rpc_errors
    def add_invoice(self, value, memo='', **kwargs):
        request = ln.Invoice(value=value, memo=memo, **kwargs)
        response = self._ln_stub.AddInvoice(request)
        return response

    @handle_rpc_errors
    def new_address(self, address_type=0):
        """Generates a new witness address"""
        request = ln.NewAddressRequest(type=address_type)
        response = self._ln_stub.NewAddress(request)
        return response

    @handle_rpc_errors
    def connect_peer(self, pub_key, host, ln_at_url=None, permanent=False):
        """Connect to a remote lnd peer"""
        if ln_at_url:
            pub_key, host = ln_at_url.split("@")
        ln_address = ln.LightningAddress(pubkey=pub_key, host=host)
        request = ln.ConnectPeerRequest(addr=ln_address, perm=permanent)
        response = self._ln_stub.ConnectPeer(request)
        return response

    @handle_rpc_errors
    def disconnect_peer(self, pub_key):
        """Disconnect a remote lnd peer identified by public key"""
        request = ln.DisconnectPeerRequest(pub_key=pub_key)
        response = self._ln_stub.DisconnectPeer(request)
        return response

    @handle_rpc_errors
    def close_channel(self, channel_point, force=False, sat_per_vbyte=None, **kwargs):
        """Close an existing channel"""
        funding_txid, output_index = channel_point.split(':')
        channel_point = ln.ChannelPoint(
            funding_txid_str=funding_txid,
            output_index=int(output_index)
        )
        request = ln.CloseChannelRequest(
            channel_point=channel_point,
            force=force,
            sat_per_vbyte=sat_per_vbyte,
            **kwargs
        )
        response = self._ln_stub.CloseChannel(request)
        return response

    @handle_rpc_errors
    def pending_channels(self):
        """Display information pertaining to pending channels"""
        request = ln.PendingChannelsRequest()
        response = self._ln_stub.PendingChannels(request)
        return response

    @handle_rpc_errors
    def send_payment(self, payment_request, fee_limit_msat, **kwargs):
        """Send a payment over lightning"""
        fee_limit = ln.FeeLimit(fixed_msat=fee_limit_msat)
        request = ln.SendRequest(payment_request=payment_request, fee_limit=fee_limit, **kwargs)
        response = self._ln_stub.SendPaymentSync(request)
        return response

    @handle_rpc_errors
    def lookup_invoice(self, r_hash_str):
        """Lookup an existing invoice by its payment hash"""
        request = ln.PaymentHash(r_hash_str=r_hash_str)
        response = self._ln_stub.LookupInvoice(request)
        return response

    @handle_rpc_errors
    def list_payments(self, **kwargs):
        """List all outgoing payments"""
        request = ln.ListPaymentsRequest(**kwargs)
        response = self._ln_stub.ListPayments(request)
        return response

    @handle_rpc_errors
    def describe_graph(self):
        """Describe the network graph"""
        request = ln.ChannelGraphRequest()
        response = self._ln_stub.DescribeGraph(request)
        return response

    @handle_rpc_errors
    def get_channel_info(self, channel_id):
        """Get the state of a specific channel"""
        requset = ln.ChanInfoRequest(chan_id=channel_id)
        response = self._ln_stub.GetChanInfo(requset)
        return response

    @handle_rpc_errors
    def get_node_info(self, pub_key, include_channels=False):
        """Get information on a specific node"""
        request = ln.NodeInfoRequest(pub_key=pub_key, include_channels=include_channels)
        response = self._ln_stub.GetNodeInfo(request)
        return response

    @handle_rpc_errors
    def query_routes(self, pub_key, amt, **kwargs):
        """Query a route to a destination"""
        request = ln.QueryRoutesRequest(pub_key=pub_key, amt=amt, **kwargs)
        response = self._ln_stub.QueryRoutes(request)
        return response

    @handle_rpc_errors
    def get_network_info(self):
        """Returns basic stats about the known channel graph for this node"""
        request = ln.NetworkInfoRequest()
        response = self._ln_stub.GetNetworkInfo(request)
        return response

    @handle_rpc_errors
    def decode_pay_req(self, payment_request):
        """Decode a payment request"""
        request = ln.PayReqString(pay_req=payment_request)
        response = self._ln_stub.DecodePayReq(request)
        return response

    @handle_rpc_errors
    def list_transactions(self):
        """List on chain transactions from the wallet"""
        request = ln.GetTransactionsRequest()
        response = self._ln_stub.GetTransactions(request)
        return response

    @handle_rpc_errors
    def stop_daemon(self):
        """Stop and shutdown the daemon"""
        request = ln.StopRequest()
        response = self._ln_stub.StopDaemon(request)
        return response

    ## TODO: This has been moved to a subsystem
    # @handle_rpc_errors
    def sign_message(self, msg):
        """Sign a message with the node's private key"""
        request = ln.SignMessageRequest(msg=msg)
        response = self._ln_stub.SignMessage(request)
        return response

    ## TODO: This has been moved to a subsystem
    @handle_rpc_errors
    def verify_message(self, msg, signature):
        """Verify a message signed with the signature"""
        request = ln.VerifyMessageRequest(msg=msg, signature=signature)
        response = self._ln_stub.VerifyMessage(request)
        return response

    @handle_rpc_errors
    def fee_report(self):
        """Display the current fee policies of all active channels"""
        request = ln.FeeReportRequest()
        response = self._ln_stub.FeeReport(request)
        return response

    @handle_rpc_errors
    def update_channel_policy(self, base_fee_msat=None, fee_rate=None, time_lock_delta=None,
                              chan_point=None, all_channels=False):
        """Update the channel policy for all channels, or a single channel"""
        kwargs = {
            'global': all_channels
        }
        if base_fee_msat:
            kwargs['base_fee_msat'] = base_fee_msat
        if fee_rate:
            kwargs['fee_rate'] = fee_rate
        if chan_point:
            txid, out_index = chan_point.split(":")
            txid_reversed = bytearray(bytes.fromhex(txid))
            txid_reversed.reverse()
            cp = ln.ChannelPoint(funding_txid_bytes=bytes(txid_reversed), output_index=int(out_index))
            kwargs['chan_point'] = cp
        if time_lock_delta:
            kwargs['time_lock_delta'] = time_lock_delta

        request = ln.PolicyUpdateRequest(**kwargs)
        response = self._ln_stub.UpdateChannelPolicy(request)
        return response

    @handle_rpc_errors
    def send_on_chain_many(self, address_amount_map, sat_ber_byte=None, target_conf=None):
        """Send bitcoin on-chain to multiple addresses"""
        pass  # TODO


    @handle_rpc_errors
    def send_coins(self, address, amount, **kwargs):
        """Send bitcoin on-chain to a single address"""
        request = ln.SendCoinsRequest(addr=address, amount=amount, **kwargs)
        response = self._ln_stub.SendCoins(request)
        return response

    @handle_rpc_errors
    def channel_acceptor(self, **kwargs):
        """Bi-directional streaming api to accept or reject channels"""
        from time import sleep
        import secrets
        import traceback
        cid = None
        def request_generator():
                while True:
                    print("Request Generator")
                    # global cid
                    # global response_msg
                    try:
                        print(cid)
                        sleep(3)
                        response = ln.ChannelAcceptResponse(
                            accept=False,
                            error="get your BOS score up, simple pleb",
                            pending_chan_id=cid
                        )
                        print("Before yield...")
                        yield response
                    except Exception as e:
                        print(e)
                        print(traceback.format_exc())


        response_msg = None
        request_iterable = request_generator()
        it = self._ln_stub.ChannelAcceptor(request_iterable)

        for response in it:
            print("Response Iterator")
            cid = response.pending_chan_id
            reponse_msg = response
            print(f"pending cid: {response.pending_chan_id.hex()}")
            print(f"pubkey: {response.node_pubkey.hex()}")
        return response

    # INVOICES
    @handle_rpc_errors
    def subscribe_single_invoice(self, r_hash):
        """Subscribe to state of a single invoice"""
        request = invoices.SubscribeSingleInvoiceRequest(r_hash=r_hash)
        response = self._invoices_stub.SubscribeSingleInvoice(request)
        for first in response:
            return first

    #Open Batch Channels
    @handle_rpc_errors
    def batch_open_channel(self,channels, sat_per_vbyte, label ,**kwargs):
        """BatchOpenChannel attempts to open multiple single-funded channels in a single transaction in an atomic way."""
        #Convert Channel Pubkey into bytes
        for channel in channels:
            channel['node_pubkey']=bytes.fromhex(channel['node_pubkey'])

        request = ln.BatchOpenChannelRequest(
            channels=channels,
            sat_per_vbyte=sat_per_vbyte,
            label=label,
            **kwargs
            )

        response =  self._ln_stub.BatchOpenChannel(request)

        return response.pending_channels
