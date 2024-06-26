from .common import invoices, BaseClient
from .errors import handle_rpc_errors
from hashlib import sha256
from secrets import token_bytes

class InvoicesRPC(BaseClient):
    @handle_rpc_errors
    def subscribe_single_invoice(self, r_hash):
        """Subscribe to state of a single invoice"""
        request = invoices.SubscribeSingleInvoiceRequest(r_hash=r_hash)
        for response in self._invoices_stub.SubscribeSingleInvoice(request):
            yield response

    @handle_rpc_errors
    def cancel_invoice(self, payment_hash):
        """CancelInvoice"""
        request = invoices.CancelInvoiceMsg(payment_hash=payment_hash)
        response = self._invoices_stub.CancelInvoice(request)
        return response

    @handle_rpc_errors
    def lookup_invoice_v2(self, payment_hash=None, payment_addr=None, set_id=None, lookup_modifier=None):
        """LookupInvoiceV2"""
        request = invoices.LookupInvoiceMsg(
            payment_hash=payment_hash,
            payment_addr=payment_addr,
            set_id=set_id,
            lookup_modifier=lookup_modifier
        )
        response = self._invoices_stub.LookupInvoiceV2(request)
        return response

    @handle_rpc_errors
    def settle_invoice(self, preimage):
        """SettleInvoice"""
        request = invoices.SettleInvoiceMsg(preimage=preimage)
        response = self._invoices_stub.SettleInvoice(request)
        return response

    @handle_rpc_errors
    def add_hold_invoice(self, **kwargs):
        """AddHoldInvoice"""
        preimage = token_bytes(32)
        r_hash = sha256(preimage).digest()
        request = invoices.AddHoldInvoiceRequest(hash=r_hash, **kwargs)
        response = self._invoices_stub.AddHoldInvoice(request)
        return response, r_hash, preimage

