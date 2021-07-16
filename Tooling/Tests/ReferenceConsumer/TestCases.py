import unittest
from queue import Queue
from sdc11073 import observableproperties
from sdc11073 import wsdiscovery
from sdc11073.mdib import ClientMdibContainer
from sdc11073.namespaces import domTag
from sdc11073.mdib.descriptorcontainers import NumericMetricDescriptorContainer, EnumStringMetricDescriptorContainer
from Tooling.Tests.ReferenceConsumer import TestClient


class ReferenceConsumerTests(unittest.TestCase):


    def discoverProvider(self):
        """
        Discovery of a provider with a specific endpoint reference address
        See that Probe is answered
        See that Resolve is answered
        """

        self.wsdclient = wsdiscovery.WSDiscoveryBlacklist()
        self.wsdclient.setRemoteServiceResolveMatchCallback(self._onResolve)
        self.wsdclient.start()
        # sends probe
        # timeout required to discover all services
        services = self.wsdclient.searchServices(timeout=10)
        probeAnswered = False
        resolveAnswered = False

        for service in services:
            if TestClient.endpoint in service.getXAddrs():
                probeAnswered = True
                self.wsdclient._sendResolve(service.getEPR())
                TestClient.service = service
                self.resolveQueue = Queue(maxsize=1)
                resolveAnswered = self._getItemFromQueue(self.resolveQueue)

        self.assertTrue(probeAnswered, msg="Test that probe answered.")
        self.assertTrue(resolveAnswered, msg="Test that resolve answered.")

    def _getItemFromQueue(self, queue, timeout=5):
        try:
            return queue.get(timeout=timeout)
        except:
            return None

    def _onResolve(self, service):
        self.resolveQueue.put_nowait(True)

    def connectToProvider(self):
        """
        Connect to the provider with specific endpoint, i.e. establish TCP connection(s)
            and retrieve endpoint metadata
        :return:
        """
        TestClient.sdcClient = TestClient.SdcClient.fromWsdService(TestClient.service,  allowSSL=True)
        TestClient.sdcClient.getMetaData()
        TestClient.sdcClient.startAll()
        self.assertIsNotNone(TestClient.sdcClient.metaData)

    def readMdibOfProvider(self):
        """
        Read MDIB of the provider
        :return:
        """
        TestClient.clientMdib = ClientMdibContainer(TestClient.sdcClient)
        TestClient.clientMdib.initMdib()
        self.assertIsNotNone(TestClient.clientMdib)

    def testSubscribeToReports(self):
        """
        Subscribe at least metrics, alerts, waveforms and operation invoked reports of
        the provider
        """
        observableproperties.bind(TestClient.sdcClient, waveFormReport=self.onReportMessage)
        observableproperties.bind(TestClient.sdcClient, episodicMetricReport=self.onReportMessage)
        observableproperties.bind(TestClient.sdcClient, episodicAlertReport=self.onReportMessage)
        observableproperties.bind(TestClient.sdcClient, episodicOperationalStateReport=self.onReportMessage)
        # TODO: clarify

    def onReportMessage(self):
        pass

    def checkPatientContextExists(self):

        patientContextStates = TestClient.clientMdib.contextStates.NODETYPE.get(domTag('PatientContextState'))
        self.assertTrue(len(patientContextStates) >= 1, msg="Test that at least one patient context exists.")

    def checkLocationContextExists(self):
        """
        Check that at least one location context exists
        """
        patientContextStates = TestClient.clientMdib.contextStates.NODETYPE.get(domTag('PatientContextState'))
        self.assertTrue(len(patientContextStates) >= 1, msg="Test that at least one patient context exists.")

    def checkMetricUpdates(self):
        """
        Check that metric updates for one metric arrive at least 5 times in 30 seconds
        # TODO: clarify
        """
        self.metricsQueue = Queue()
        # metrics = [m for m in TestClient.clientMdib.descriptions.objects if isinstance(m, AbstractMetricDescriptorContainer)]
        # observableproperties.bind(TestClient.clientMdib, metricsByHandle=self.onMetricUpdate)


    def onMetricUpdate(self):
        pass

    def checkAlertUpdates(self):
        """
        Check that alert updates of one alert condition arrive at least 5 times in 30
        seconds
        :return:
        """
        observableproperties.bind(TestClient.clientMdib, alertByHandle=self.onStateUpdate)

    def executeOperation(self):
        """
        Execute external control operations (any operatoin that exists in the
        containment tree, if none exist: skip test) by checking the ultimate transaction
        result is "finished"
        a. Any Activate
        b. Any SetString
        c. Any SetValue
        :return:
        """
        observableproperties.bind(TestClient.clientMdib, operationByHandle=self.onStateUpdate)

    def shutdownConnection(self):
        """
        Shutdown connection (cancel subscription, close connection)
        :return:
        """

