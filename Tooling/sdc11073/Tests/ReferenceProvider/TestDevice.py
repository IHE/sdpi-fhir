import os
from queue import Queue
from sdc11073.sdcdevice.sdcdeviceimpl import SdcDevice as _SdcDevice
from Tests import certloader


class PublishingSdcDevice(_SdcDevice):
    def __init__(self, ws_discovery, my_uuid, model, device, deviceMdibContainer, validate=True,
                 roleProvider=None, useSSL=True, sslContext=None, logLevel=None, max_subscription_duration=7200,
                 log_prefix='', handler_cls=None): #pylint:disable=too-many-arguments
        """ Creates an ssl context if needed and calls super class"""

        if useSSL and not sslContext:
            ca_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..\ca')
            sslContext = certloader.mk_device_ssl_context(ca_folder)
        super().__init__(ws_discovery, my_uuid, model, device, deviceMdibContainer, validate, roleProvider,
                         sslContext, logLevel, max_subscription_duration, log_prefix, handler_cls)


endpoint = None
deviceMdib = None
publishingDevice = None
operationsQueue = Queue()
