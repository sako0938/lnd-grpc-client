
from .common import BaseClient

from .router import RouterRPC
from .walletunlocker import WalletUnlockerRPC
from .walletkit import WalletRPC
from .versioner import VersionerRPC
from .signer import SignerRPC
from .lightning import LightningRPC
from .invoices import InvoicesRPC
from .peers import PeersRPC
from .dev import DevRPC
from .neutrinokit import NeutrinoRPC
from .autopilot import AutoPilotRPC
from .chainnotifier import ChainNotifierRPC
from .chainkit import ChainKitRPC
from .watchtower import WatchTowerRPC
from .watchtowerclient import WTClientRPC
from .state import StateRPC

from threading import Thread
import logging


logger = logging.getLogger(__name__)


class AddAndWatchInvoiceClass(Thread):
	"""create a seperate thread that creates, monitors, and controls invoice state, logging the state changes"""

	def __init__(self, lndInstance, value, memo='', expiry=60*10, InvoiceType='Regular', **kwargs):
		super(AddAndWatchInvoiceClass, self).__init__()
		self.daemon=True		# using daemon mode so control-C will stop the script and the threads.

		self.lndInstance=lndInstance
		self.value=value
		self.expiry=expiry
		self.memo=memo
		if 'cltv_expiry' in kwargs:
			self.cltv_expiry=kwargs['cltv_expiry']
		else:
			self.cltv_expiry='default'

		logger.debug('getting new '+InvoiceType+' invoice for '+ str(self.value)+' sat with memo '+self.memo+', expiry '+str(self.expiry)+', and cltv_expiry '+str(self.cltv_expiry))

		if InvoiceType=='HOLD':
			Invoice, self.r_hash, self.preimage = self.lndInstance.add_hold_invoice(value=self.value,memo=self.memo,expiry=self.expiry, **kwargs)
		elif InvoiceType=='Regular':
			Invoice=self.lndInstance.add_invoice(value=self.value,memo=self.memo,expiry=self.expiry, **kwargs)
			self.r_hash=Invoice.r_hash
		else:
			raise Exception('invalid InvoiceType')

		self.payment_request=Invoice.payment_request
		self.state=0		# it is open because it's never been given to anyone yet

		logger.debug('new invoice r_hash='+self.r_hash.hex()+' , payment_request='+self.payment_request)
		logger.debug('state is now '+str(self.state)+' for invoice with r_hash='+self.r_hash.hex())

		self.start()			# auto start on initialization


	def cancel(self):
		logger.debug('canceling invoice with r_hash='+self.r_hash.hex())
		self.lndInstance.cancel_invoice(self.r_hash)


	def settle(self):
		logger.debug('settling invoice with r_hash='+self.r_hash.hex())
		self.lndInstance.settle_invoice(self.preimage)



	def run(self):
		while True:
			try:
				logger.debug('watching invoice with r_hash='+self.r_hash.hex() +' for state changes')
				for InvoiceUpdate in self.lndInstance.subscribe_single_invoice(self.r_hash):
					self.state=InvoiceUpdate.state
					self.htlcs=InvoiceUpdate.htlcs
					logger.debug('state is now '+str(self.state)+' for invoice with r_hash='+self.r_hash.hex())

				logger.debug('done watching invoice with r_hash='+self.r_hash.hex() +' for state changes')
				break

			except:
				logger.exception('something went wrong with the LND connection for invoice with r_hash='+self.r_hash.hex()+'. retrying.....')
				sleep(2)









class LNDClient(
			RouterRPC,
			WalletUnlockerRPC,
			WalletRPC,
			VersionerRPC,
			SignerRPC,
			LightningRPC,
			InvoicesRPC,
			PeersRPC,
			DevRPC,
			NeutrinoRPC,
			AutoPilotRPC,
			ChainNotifierRPC,
			ChainKitRPC,
			WatchTowerRPC,
			WTClientRPC,
			StateRPC
		):
	"""merge all classes into a main class that connects to an lnd instance and provides all available function calls to that node"""

	def AddAndWatchInvoice(self, value, **kwargs):
		"""use the current node and create a seperate thread that creates, monitors, and controls invoice state"""
		return AddAndWatchInvoiceClass(self, value, **kwargs)





# def cli():
#     import code
#     # LNDClient gets all configuration parameters from environment variables!
#     lnd = LNDClient()

#     # Enter a shell for interacting with LND
#     code.interact(local=dict(globals(), **locals()))  