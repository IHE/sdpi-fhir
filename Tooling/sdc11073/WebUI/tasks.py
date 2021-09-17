import os
import re
import shutil
import tempfile
from threading import Lock
from urllib.parse import urlparse, parse_qs

import HtmlTestRunner
from flask_socketio import emit
from sdc11073 import wsdiscovery
from sdc11073.definitions_sdc import SDC_v1_Definitions

from Tests.ReferenceConsumer import ReferenceConsumer


class WebSdcClient:

    def __init__(self):
        self.wsdiscovery = None
        self.deviceList = {}
        self.deviceListLock = Lock()

    def startDiscovery(self):
        self.deviceList = {}
        self.wsdiscovery = wsdiscovery.WSDiscoveryBlacklist()

        self.wsdiscovery.setRemoteServiceHelloCallback(self.onHello)
        self.wsdiscovery.setRemoteServiceResolveMatchCallback(self.onResolve)
        self.wsdiscovery.setRemoteServiceByeCallback(self.onBye)

        self.wsdiscovery.start()
        self.wsdiscovery.clearRemoteServices()
        services = self.wsdiscovery.searchMultipleTypes(timeout=1, typesList=[SDC_v1_Definitions.MedicalDeviceTypesFilter])
        self.deviceList = {}
        self.processDiscoveredServices(services)

    def processDiscoveredServices(self, services):
        if not services:
            return

        for service in services:
            try:
                if len(service.getXAddrs()) != 0:
                    xaddrs = service.getXAddrs()[0]
                    ipAddr = re.findall(r'[0-9]+(?:\.[0-9]+){3}', str(xaddrs))[0]
                else:
                    xaddrs, ipAddr = '', ''

                uuid = service.getEPR()
                location = {}
                try:
                    locationScope = ''
                    for scope in service.getScopes():
                        if 'sdc.ctxt.loc' in str(scope):
                            locationScope = str(scope)

                    location = parse_qs(urlparse(locationScope).query)
                except:
                    pass

                self.deviceList[uuid] = {'fac': location.get("fac", [''])[0],
                                         'poc': location.get("poc", [''])[0],
                                         'bed': location.get("bed", [''])[0],
                                         'ip': ipAddr,
                                         'uuid': uuid,
                                         'xaddr': xaddrs,
                                         'service': str(service)}  # service is not displayed, but needed for start of client

            except Exception:
                pass
        emit('devices', {'data': self.deviceList}, broadcast=True)


    def onHello(self, addr, service):
        with self.deviceListLock:
            self.processDiscoveredServices([service])

    def onResolve(self, service):
        with self.deviceListLock:
            self.processDiscoveredServices([service])

    def onBye(self, addr, uuid):
        with self.deviceListLock:
            try:
                del self.deviceList[uuid]
            except KeyError:
                pass


def discoveryTask():
    sdcClient = WebSdcClient()
    sdcClient.startDiscovery()


def consumerTestTask(endpoint, config, ca, socketio, reportsDir):
    with tempfile.TemporaryDirectory() as dir:
        testRunner = HtmlTestRunner.HTMLTestRunner(output=dir)
        ReferenceConsumer.runReferenceConsumerTestSuite(endpoint, config, ca, testRunner=testRunner)
        results = _copyReports(dir, reportsDir)
    socketio.emit('reports', {'data': results}, broadcast=True)


def _copyReports(dir, reportsDir):
    results = []
    for filename in os.listdir(dir):
        if filename.endswith(".html"):
            report = os.path.join(dir, filename)
            shutil.copyfile(report, os.path.join(reportsDir, filename))
            results.append({"name": filename})
    return results
