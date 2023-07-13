from .common import ln, BaseClient
from .errors import handle_rpc_errors
from datetime import datetime
import binascii

class LightningRPC(BaseClient):
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
    def subscribe_invoices(self, add_index=None, settle_index=None):
        request = ln.InvoiceSubscription(
            add_index=add_index,
            settle_index=settle_index,
        )
        for invoice in self._ln_stub.SubscribeInvoices(request):
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
    def connect_peer(self, pub_key, host, ln_at_url=None, perm=True, timeout=0):
        """Connect to a remote lnd peer"""
        if ln_at_url:
            pub_key, host = ln_at_url.split("@")
        ln_address = ln.LightningAddress(pubkey=pub_key, host=host)
        request = ln.ConnectPeerRequest(addr=ln_address, perm=perm, timeout=timeout)
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
    def closed_channels(self):
        """ClosedChannels"""
        request = ln.ClosedChannelsRequest(
            cooperative=True,
            local_force=True,
            remote_force=True,
            breach=True,
            funding_canceled=True,
            abandoned=True
        )
        response = self._ln_stub.ClosedChannels(request)
        return response

    @handle_rpc_errors
    def pending_channels(self):
        """Display information pertaining to pending channels"""
        request = ln.PendingChannelsRequest()
        response = self._ln_stub.PendingChannels(request)
        return response

    @handle_rpc_errors
    def send_payment(self, payment_request, fee_limit_sat=None, fee_limit_msat=None, fee_limit_percent=None, **kwargs):
        """Send a payment over lightning"""
        fee_limit = ln.FeeLimit(fixed=fee_limit_sat,fixed_msat=fee_limit_msat,percent=fee_limit_percent)
        request = ln.SendRequest(payment_request=payment_request, fee_limit=fee_limit, **kwargs)
        response = self._ln_stub.SendPaymentSync(request)
        return response

    @handle_rpc_errors
    def lookup_invoice(self, r_hash):
        """Lookup an existing invoice by its payment hash"""
        request = ln.PaymentHash(r_hash=r_hash)
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
    def get_chan_info(self, channel_id):
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
                        raise e


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


    @handle_rpc_errors
    def debug_level(self, show, level_spec):
        """DebugLevel"""
        request = ln.DebugLevelRequest(show=show, level_spec=level_spec)
        response = self._ln_stub.DebugLevel(request)
        return response

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