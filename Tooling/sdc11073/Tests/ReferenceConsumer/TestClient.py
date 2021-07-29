import logging
import os

from sdc11073.sdcclient.sdcclientimpl import SdcClient as _SdcClient

from Tests import certloader


class SdcClient(_SdcClient):
    """ Implement the default SSL Context handling of pysdc"""
    def __init__(self, devicelocation, deviceType, validate=True, allowSSL=True, sslEvents='auto', sslContext=None,
                 my_ipaddress=None, logLevel=None, ident='',
                 soap_notifications_handler_class=None):  # pylint:disable=too-many-arguments

        if allowSSL and not sslContext:
            ca_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ca')
            sslContext = certloader.mk_client_ssl_context(ca_folder)

        super().__init__(devicelocation, deviceType, validate, sslEvents, sslContext,
                 my_ipaddress, logLevel, ident, soap_notifications_handler_class)

    @classmethod
    def fromWsdService(cls, wsdService, validate=True, sslEvents='auto',
                       allowSSL=True, sslContext=None, my_ipaddress=None, logLevel=logging.INFO,
                       ident='', soap_notifications_handler_class=None):
        if allowSSL and not sslContext:
            ca_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..\ca')
            sslContext = certloader.mk_client_ssl_context(ca_folder)
        return super().fromWsdService(wsdService, validate, sslEvents,
                       sslContext, my_ipaddress, logLevel,
                       ident, soap_notifications_handler_class)


endpoint = None
wsdClient = None
service = None
sdcClient = None
clientMdib = None
