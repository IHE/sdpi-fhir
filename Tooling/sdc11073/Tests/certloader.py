import ssl
import json
import os

DEFAULT_SSL_CIPHERS = 'HIGH:!3DES:!DSS:!aNULL@STRENGTH'

def mk_ssl_context(ca_dir):
    """ Convenience method for easy creation of SSL context.
    Create an ssl context from files 'sdccert.pem', 'userkey.pem', 'cacert.pem' and optional 'cyphers.json'
    :param ca_dir: folder where to look for files
    :return: ssl.SSLContext instance
    """
    _sslContext = ssl.SSLContext(ssl.PROTOCOL_TLS)  # pylint:disable=no-member
    device_cyphers = DEFAULT_SSL_CIPHERS
    _ssl_certfile = os.path.join(ca_dir, 'sdccert.pem')
    _ssl_keyfile = os.path.join(ca_dir, 'userkey.pem')
    _ssl_cacert = os.path.join(ca_dir, 'cacert.pem')
    _ssl_passwd = 'dummypass'
    _ssl_cypherfile = os.path.join(ca_dir, 'cyphers.json')
    if os.path.exists(_ssl_cypherfile):
        with open(_ssl_cypherfile)  as f:
            cyphers = json.load(f)
            device_cyphers = cyphers.get('device', DEFAULT_SSL_CIPHERS)
    if device_cyphers is not None:
        _sslContext.set_ciphers(device_cyphers)
    _sslContext.load_cert_chain(certfile=_ssl_certfile, keyfile=_ssl_keyfile, password=_ssl_passwd)
    _sslContext.verify_mode = ssl.CERT_REQUIRED
    _sslContext.load_verify_locations(_ssl_cacert)
    return _sslContext
