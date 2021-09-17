from queue import Queue
from sdc11073.sdcdevice.sdcdeviceimpl import SdcDevice as _SdcDevice
from Tests import certloader


config = {}
ca_dir = None
endpoint = None
deviceMdib = None
publishingDevice = None
operationsQueue = Queue()


class PublishingSdcDevice(_SdcDevice):
    def __init__(self, ws_discovery, my_uuid, model, device, deviceMdibContainer, validate=True,
                 roleProvider=None, useSSL=True, sslContext=None, logLevel=None, max_subscription_duration=7200,
                 log_prefix='', handler_cls=None): #pylint:disable=too-many-arguments
        """ Creates an ssl context if needed and calls super class"""
        if useSSL and not sslContext:
            sslContext = certloader.mk_ssl_context(ca_dir)
        super().__init__(ws_discovery, my_uuid, model, device, deviceMdibContainer, validate, roleProvider,
                         sslContext, logLevel, max_subscription_duration, log_prefix, handler_cls)
