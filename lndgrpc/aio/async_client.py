from lndgrpc.common import router, ln, BaseClient, invoices
from lndgrpc.errors import handle_rpc_errors

import aiogrpc

class AsyncLNDClient(BaseClient):
    grpc_module = aiogrpc

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @handle_rpc_errors
    async def get_info(self):
        response = await self._ln_stub.GetInfo(ln.GetInfoRequest())
        return response

    @handle_rpc_errors
    async def wallet_balance(self):
        response = await self._ln_stub.WalletBalance(ln.WalletBalanceRequest())
        return response

    @handle_rpc_errors
    async def channel_balance(self):
        response = await self._ln_stub.ChannelBalance(ln.ChannelBalanceRequest())
        return response

    @handle_rpc_errors
    async def list_peers(self):
        """List all active, currently connected peers"""
        response = await self._ln_stub.ListPeers(ln.ListPeersRequest())
        return response

    @handle_rpc_errors
    async def list_channels(self):
        """List all open channels"""
        response = await self._ln_stub.ListChannels(ln.ListChannelsRequest())
        return response

    @handle_rpc_errors
    async def open_channel(self, node_pubkey, local_funding_amount, sat_per_vbyte, **kwargs):
        """Open a channel to an existing peer"""
        request = ln.OpenChannelRequest(
            node_pubkey=bytes.fromhex(node_pubkey),
            local_funding_amount=local_funding_amount,
            # sat_per_vbyte=sat_per_vbyte,
            **kwargs
        )
        response = [ print(x.psbt_fund.psbt) async for x in self._ln_stub.OpenChannel(request)]
        return response

    @handle_rpc_errors
    async def list_invoices(self):
        request = ln.ListInvoiceRequest()
        response = await self._ln_stub.ListInvoices(request)
        return response

    @handle_rpc_errors
    async def subscribe_invoices(self, add_index=None, settle_index=None):
        """ Open a stream of invoices """
        request = ln.InvoiceSubscription(
            add_index=add_index,
            settle_index=settle_index,
        )
        async for response in self._ln_stub.SubscribeInvoices(request):
            yield response

    @handle_rpc_errors
    async def add_invoice(self, value, memo=''):
        request = ln.Invoice(value=value, memo=memo)
        response = await self._ln_stub.AddInvoice(request)
        return response

    @handle_rpc_errors
    async def unlock(self, password):
        """Unlock encrypted wallet at lnd startup"""
        request = ln.UnlockWalletRequest(wallet_password=password.encode())
        response = await self._wallet_stub.UnlockWallet(request)
        return response

    @handle_rpc_errors
    async def new_address(self, address_type=0):
        """Generates a new witness address"""
        request = ln.NewAddressRequest(type=address_type)
        response = await self._ln_stub.NewAddress(request)
        return response

    @handle_rpc_errors
    async def connect_peer(self, pub_key, host, permanent=False):
        """Connect to a remote lnd peer"""
        ln_address = ln.LightningAddress(pubkey=pub_key, host=host)
        request = ln.ConnectPeerRequest(addr=ln_address, perm=permanent)
        response = await self._ln_stub.ConnectPeer(request)
        return response

    @handle_rpc_errors
    async def disconnect_peer(self, pub_key):
        """Disconnect a remote lnd peer identified by public key"""
        request = ln.DisconnectPeerRequest(pub_key=pub_key)
        response = await self._ln_stub.DisconnectPeer(request)
        return response

    @handle_rpc_errors
    async def close_channel(self, channel_point, force=False, target_conf=None, sat_per_byte=None):
        """Close an existing channel"""
        funding_txid, output_index = channel_point.split(':')
        channel_point = ln.ChannelPoint(
            funding_txid_str=funding_txid,
            output_index=int(output_index)
        )
        request = ln.CloseChannelRequest(
            channel_point=channel_point,
            force=force,
            target_conf=target_conf,
            sat_per_byte=sat_per_byte
        )
        response = await self._ln_stub.CloseChannel(request)
        return response

    @handle_rpc_errors
    async def pending_channels(self):
        """Display information pertaining to pending channels"""
        request = ln.PendingChannelsRequest()
        response = await self._ln_stub.PendingChannels(request)
        return response

    @handle_rpc_errors
    async def send_payment(self, payment_request):
        """Send a payment over lightning"""
        request = ln.SendRequest(payment_request=payment_request)
        response = await self._ln_stub.SendPaymentSync(request)
        return response

    # ROUTERRPC
    @handle_rpc_errors
    async def send_payment_v2(self, payment_request):
        """Send a payment over lightning"""
        request = router.SendPaymentRequest(payment_request=payment_request,**kwargs)
        response = await self._router_stub.SendPaymentV2(request)
        return response


    @handle_rpc_errors
    async def lookup_invoice(self, r_hash):
        """Lookup an existing invoice by its payment hash"""
        request = ln.PaymentHash(r_hash=r_hash)
        response = await self._ln_stub.LookupInvoice(request)
        return response

    @handle_rpc_errors
    async def list_payments(self):
        """List all outgoing payments"""
        request = ln.ListPaymentsRequest()
        response = await self._ln_stub.ListPayments(request)
        return response

    @handle_rpc_errors
    async def describe_graph(self):
        """Describe the network graph"""
        request = ln.ChannelGraphRequest()
        response = await self._ln_stub.DescribeGraph(request)
        return response

    @handle_rpc_errors
    async def get_channel_info(self, channel_id):
        """Get the state of a specific channel"""
        requset = ln.ChanInfoRequest(chan_id=channel_id)
        response = await self._ln_stub.GetChanInfo(requset)
        return response

    @handle_rpc_errors
    async def get_node_info(self, pub_key):
        """Get information on a specific node"""
        request = ln.NodeInfoRequest(pub_key=pub_key)
        response = await self._ln_stub.GetNodeInfo(request)
        return response

    @handle_rpc_errors
    async def query_routes(self, pub_key, amt, num_routes=5):
        """Query a route to a destination"""
        request = ln.QueryRoutesRequest(pub_key=pub_key, amt=amt, num_routes=num_routes)
        response = await self._ln_stub.QueryRoutes(request)
        return response

    @handle_rpc_errors
    async def get_network_info(self):
        """Returns basic stats about the known channel graph for this node"""
        request = ln.NetworkInfoRequest()
        response = await self._ln_stub.GetNetworkInfo(request)
        return response

    @handle_rpc_errors
    async def decode_payment_request(self, payment_request):
        """Decode a payment request"""
        request = ln.PayReqString(pay_req=payment_request)
        response = await self._ln_stub.DecodePayReq(request)
        return response

    @handle_rpc_errors
    async def list_transactions(self):
        """List on chain transactions from the wallet"""
        request = ln.GetTransactionsRequest()
        response = await self._ln_stub.GetTransactions(request)
        return response

    @handle_rpc_errors
    async def stop_daemon(self):
        """Stop and shutdown the daemon"""
        request = ln.StopRequest()
        response = await self._ln_stub.StopDaemon(request)
        return response

    @handle_rpc_errors
    async def sign_message(self, msg):
        """Sign a message with the node's private key"""
        request = ln.SignMessageRequest(msg=msg)
        response = await self._ln_stub.SignMessage(request)
        return response

    @handle_rpc_errors
    async def verify_message(self, msg, signature):
        """Verify a message signed with the signature"""
        request = ln.VerifyMessageRequest(msg=msg, signature=signature)
        response = await self._ln_stub.VerifyMessage(request)
        return response

    @handle_rpc_errors
    async def fee_report(self):
        """Display the current fee policies of all active channels"""
        request = ln.FeeReportRequest()
        response = await self._ln_stub.FeeReport(request)
        return response

    @handle_rpc_errors
    async def update_channel_policy(self, base_fee_msat=None, fee_rate=None, time_lock_delta=None,
                                    channel_point=None, all_channels=False):
        """Update the channel policy for all channels, or a single channel"""
        pass  # TODO

    @handle_rpc_errors
    async def send_on_chain(self, address, amount, sat_ber_byte=None, target_conf=None):
        """Send bitcoin on-chain to a single address"""
        optional_kwargs = {}
        if sat_ber_byte is not None:
            optional_kwargs['sat_ber_byte'] = sat_ber_byte
        if target_conf is not None:
            optional_kwargs['target_conf'] = target_conf

        request = ln.SendCoinsRequest(addr=address, amount=amount, **optional_kwargs)
        response = await self._ln_stub.SendCoins(request)
        return response

    @handle_rpc_errors
    async def subscribe_single_invoice(self, r_hash):
        """Subscribe to state of a single invoice"""
        request = invoices.SubscribeSingleInvoiceRequest(r_hash=r_hash)
        response = [print(x) async for x in self._invoices_stub.SubscribeSingleInvoice(request)]
        return response

    @handle_rpc_errors
    async def track_payment_v2(self, payment_hash, no_inflight_updates=False):
        """Subscribe to state of a single invoice"""
        request = router.TrackPaymentRequest(
            payment_hash=bytes.fromhex(payment_hash),
            no_inflight_updates=no_inflight_updates
        )
        response = [print(x) async for x in self._router_stub.TrackPaymentV2(request)]
        return response

    @handle_rpc_errors
    async def subscribe_htlc_events(self):
        """
        SubscribeHtlcEvents creates a uni-directional stream
        from the server to the client which delivers a stream of htlc events.
        """
        def handle_htlc(htlc):
            print("new htlc event!")
            print(htlc)
            
        request = router.SubscribeHtlcEventsRequest()
        response = [handle_htlc(x) async for x in self._router_stub.SubscribeHtlcEvents(request)]
        return response