from .compiled import router_pb2 as router                        # note: API docs call this routerrpc
from .compiled import router_pb2_grpc as routerrpc                # note: API docs call this routerstub
from .compiled import lightning_pb2 as lightning                  # note: API docs call this lnrpc
from .common import BaseClient
from .errors import handle_rpc_errors




class RouterRPC(BaseClient):

    def get_router_stub(self):
        # only create a new stub if it does not already exist, otherwise re-use the existing one
        if not hasattr(self, '_router_stub'):
            self._router_stub = routerrpc.RouterStub(self.channel)
        return self._router_stub

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
            response = self.get_router_stub().BuildRoute(request)
        except Exception as error:
            print(error)
            raise error

        return response

    @handle_rpc_errors
    def send_to_route(self, pay_hash, route):
        request = router.SendToRouteRequest(
            payment_hash=pay_hash,
            route=route,
        )

        response = self.get_router_stub().SendToRouteV2(request)
        return response

    @handle_rpc_errors
    def send_payment_v2(self, **kwargs):
        request = router.SendPaymentRequest(**kwargs)
        for response in self.get_router_stub().SendPaymentV2(request):
            yield response

    @handle_rpc_errors
    def send_payment_v1(self, **kwargs):
        request = router.SendPaymentRequest(**kwargs)
        response = self.get_router_stub().SendPayment(request)
        return response

    @handle_rpc_errors
    def reset_mission_control(self):
        request = router.ResetMissionControlRequest()
        response = self.get_router_stub().ResetMissionControl(request)
        return response

    @handle_rpc_errors
    def update_chan_status(self, chan_point, action):
        """
        Router.UpdateChanStatus
        Update
        ENABLE 0
        DISABLE 1
        AUTO 2
        """
        funding_txid_str, output_index = chan_point.split(":")
        output_index = int(output_index)
        channel_point = lightning.ChannelPoint(funding_txid_str=funding_txid_str, output_index=output_index)

        request = router.UpdateChanStatusRequest(
            chan_point=channel_point,
            action=action
        )
        response = self.get_router_stub().UpdateChanStatus(request)
        return response

    @handle_rpc_errors
    def track_payment_v2(self, payment_hash, no_inflight_updates=False):
        """Subscribe to the state of a single outbound payment"""
        request = router.TrackPaymentRequest(payment_hash=bytes.fromhex(payment_hash), no_inflight_updates=no_inflight_updates)
        for response in self.get_router_stub().TrackPaymentV2(request):
            yield response

    @handle_rpc_errors
    def track_payments(self, no_inflight_updates=False):
        """Subscribe to the state of all outbound payments"""
        request = router.TrackPaymentsRequest(no_inflight_updates=no_inflight_updates)
        for response in self.get_router_stub().TrackPayments(request):
            yield response

