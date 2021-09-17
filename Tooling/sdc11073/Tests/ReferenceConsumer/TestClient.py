import logging

from sdc11073.sdcclient.sdcclientimpl import SdcClient as _SdcClient

from Tests import certloader


config = {}
endpoint = None
service = None
sdcClient = None
clientMdib = None
ca_dir = None


class SdcClient(_SdcClient):

    @classmethod
    def fromWsdService(cls, wsdService, validate=True, sslEvents='auto',
                       allowSSL=True, sslContext=None, my_ipaddress=None, logLevel=logging.INFO,
                       ident='', soap_notifications_handler_class=None):
        if allowSSL and not sslContext:
            sslContext = certloader.mk_ssl_context(ca_dir)
        return super().fromWsdService(wsdService, validate, sslEvents,
                       sslContext, my_ipaddress, logLevel,
                       ident, soap_notifications_handler_class)
