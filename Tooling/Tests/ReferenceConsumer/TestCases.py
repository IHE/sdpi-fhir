import unittest
import random
import time
from queue import Queue, Full
from sdc11073 import observableproperties
from sdc11073 import wsdiscovery
from sdc11073.mdib import ClientMdibContainer
from sdc11073.namespaces import domTag
from sdc11073.mdib.descriptorcontainers import (NumericMetricDescriptorContainer, EnumStringMetricDescriptorContainer,
                                                StringMetricDescriptorContainer, AlertConditionDescriptorContainer,
                                                SetStringOperationDescriptorContainer, SetValueOperationDescriptorContainer,
                                                ActivateOperationDescriptorContainer)
from sdc11073.pmtypes import InvocationState
from Tooling.Tests.TestLogger import logger
from Tooling.Tests.ReferenceConsumer import TestClient


class ReferenceConsumerTests(unittest.TestCase):
    OPERATION_TIMEOUT = 10
    UPDATE_TEST_TIME = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updatesQueue = Queue()
        self.resolveQueue = Queue(maxsize=1)
        self.testMetric = None
        self.testAlert = None

    def discoverProvider(self):
        """
        Discovery of a provider with a specific endpoint reference address
        See that Probe is answered
        See that Resolve is answered
        """
        logger.info("Running discovery of provider test.")
        self.wsdclient = wsdiscovery.WSDiscoveryBlacklist()
        self.wsdclient.setRemoteServiceResolveMatchCallback(self._onResolve)
        self.wsdclient.start()

        # timeout required to discover all services
        services = self.wsdclient.searchServices(timeout=10)
        probeAnswered = False
        resolveAnswered = False

        for service in [s for s in services if TestClient.endpoint == s.getEPR()]:
            probeAnswered = True
            self.wsdclient._sendResolve(service.getEPR())
            TestClient.service = service
            resolveAnswered = self._getItemFromQueue(self.resolveQueue)

        self.assertTrue(probeAnswered, msg="Test that probe answered.")
        self.assertTrue(resolveAnswered, msg="Test that resolve answered.")

    def _getItemFromQueue(self, queue, timeout=5):
        try:
            return queue.get(timeout=timeout)
        except:
            return None

    def _onResolve(self, service):
        if TestClient.endpoint == service.getEPR():
            logger.info("Received resolve from device with endpoint %s.", TestClient.endpoint)
            try:
                self.resolveQueue.put_nowait(True)
            except Full:
                logger.warning("Received more than one resolve from device with endpoint %s.", TestClient.endpoint)

    def connectToProvider(self):
        """
        Connect to the provider with specific endpoint, i.e. establish TCP connection(s)
            and retrieve endpoint metadata
        """
        logger.info("Running connect to provider test.")
        TestClient.sdcClient = TestClient.SdcClient.fromWsdService(TestClient.service,  allowSSL=True)
        TestClient.sdcClient.getMetaData()
        TestClient.sdcClient.startAll()
        self.assertIsNotNone(TestClient.sdcClient.metaData)

    def readMdibOfProvider(self):
        """
        Read MDIB of the provider
        """
        logger.info("Running read Mdib of the provider provider test.")
        TestClient.clientMdib = ClientMdibContainer(TestClient.sdcClient)
        TestClient.clientMdib.initMdib()
        self.assertIsNotNone(TestClient.clientMdib)

    def testSubscribeToReports(self):
        """
        Subscribe at least metrics, alerts, waveforms and operation invoked reports of
        the provider
        """
        logger.info("Running subscribe to reports test.")
        # Client startAll method creates subscriptions so we can check clients subscriptions for
        # reports in interest
        expectedReports = [TestClient.sdcClient.sdc_definitions.Actions.EpisodicMetricReport,
                           TestClient.sdcClient.sdc_definitions.Actions.EpisodicAlertReport,
                           TestClient.sdcClient.sdc_definitions.Actions.Waveform,
                           TestClient.sdcClient.sdc_definitions.Actions.OperationInvokedReport]
        self.assertTrue(TestClient.sdcClient._subscriptionMgr.allSubscriptionsOkay)
        reports = ' '.join([report for report in TestClient.sdcClient._subscriptionMgr.subscriptions.keys()])
        for report in expectedReports:
            self.assertIn(report, reports)

    def checkPatientContextExists(self):
        """
        Check that at least one patient context exists
        """
        logger.info("Running patient context test.")
        patientContextStates = TestClient.clientMdib.contextStates.NODETYPE.get(domTag('PatientContextState'))
        self.assertTrue(len(patientContextStates) >= 1, msg="Test that at least one patient context exists.")

    def checkLocationContextExists(self):
        """
        Check that at least one location context exists
        """
        logger.info("Running location context test.")
        patientContextStates = TestClient.clientMdib.contextStates.NODETYPE.get(domTag('PatientContextState'))
        self.assertTrue(len(patientContextStates) >= 1, msg="Test that at least one patient context exists.")

    def checkMetricUpdates(self):
        """
        Check that metric updates for one metric arrive at least 5 times in 30 seconds
        """
        logger.info("Running metric updates test.")
        with self.updatesQueue.mutex:
            self.updatesQueue.queue.clear()

        metrics = [m for m in TestClient.clientMdib.descriptions.objects
                   if isinstance(m, (NumericMetricDescriptorContainer, EnumStringMetricDescriptorContainer, StringMetricDescriptorContainer))]
        self.testMetric = random.choice(metrics).handle
        with observableproperties.boundContext(TestClient.clientMdib, metricsByHandle=self._onMetricUpdate):
            updateCount = self._receiveUpdates(self.updatesQueue)
            self.assertTrue(updateCount >= 5)

    def _receiveUpdates(self, queue):
        start = time.time()
        updateCount = 0
        while time.time() - start < self.UPDATE_TEST_TIME:
            try:
                self.updatesQueue.get(timeout=1)
                updateCount += 1
                if updateCount >= 5:
                    return updateCount
            except:
                pass
        return updateCount

    def _onMetricUpdate(self, states):
        if self.testMetric in states:
            self.updatesQueue.put(True)

    def _onAlertUpdate(self, states):
        if self.testAlert in states:
            self.updatesQueue.put(True)

    def checkAlertUpdates(self):
        """
        Check that alert updates of one alert condition arrive at least 5 times in 30
        seconds
        """
        logger.info("Running alert updates test.")
        with self.updatesQueue.mutex:
            self.updatesQueue.queue.clear()

        alerts = [a for a in TestClient.clientMdib.descriptions.objects if isinstance(a, AlertConditionDescriptorContainer)]
        self.testAlert = random.choice(alerts).handle
        with observableproperties.boundContext(TestClient.clientMdib, alertByHandle=self._onAlertUpdate):
            updateCount = self._receiveUpdates(self.updatesQueue)
            self.assertTrue(updateCount >= 5)

    def executeOperation(self):
        """
        Execute external control operations (any operation that exists in the
        containment tree, if none exist: skip test) by checking the ultimate transaction
        result is "finished"
        a. Any Activate
        b. Any SetString
        c. Any SetValue
        """
        logger.info("Running execute operation test.")
        setService = TestClient.sdcClient.client('Set')
        self._executeSetStringOperation(setService)
        self._executeActivateOperation(setService)
        self._executeSetValueOperation(setService)

    def _executeSetStringOperation(self, setService):
        ops = [o for o in TestClient.clientMdib.descriptions.objects if isinstance(o, SetStringOperationDescriptorContainer)]
        testOp = random.choice(ops)

        operationTimeout = self.OPERATION_TIMEOUT
        if testOp.MaxTimeToFinish:
            operationTimeout = testOp.MaxTimeToFinish

        state = TestClient.clientMdib.states.descriptorHandle.getOne(testOp.handle, allowNone=True)
        value = "test"
        if state.AllowedValues:
            value = random.choice(state.AllowedValues)

        future = setService.setString(operationHandle=testOp.handle, requestedString=value)
        result = future.result(timeout=operationTimeout)
        self.assertEqual(InvocationState.FINISHED, result.state)

    def _executeSetValueOperation(self, setService):
        ops = [o for o in TestClient.clientMdib.descriptions.objects if
               isinstance(o, SetValueOperationDescriptorContainer)]
        testOp = random.choice(ops)

        operationTimeout = self.OPERATION_TIMEOUT
        if testOp.MaxTimeToFinish:
            operationTimeout = testOp.MaxTimeToFinish

        state = TestClient.clientMdib.states.descriptorHandle.getOne(testOp.handle, allowNone=True)
        value = 0
        if state.AllowedRange:
            value = self._getValueFromRange(state.AllowedRange)

        future = setService.setNumericValue(operationHandle=testOp.handle, requestedNumericValue=value)
        result = future.result(timeout=operationTimeout)
        self.assertEqual(InvocationState.FINISHED, result.state)

    def _getValueFromRange(self, allowedRange):
        anyRange = random.choice(allowedRange)
        if anyRange.Upper:
            return anyRange.Upper
        if anyRange.Lower:
            return anyRange.Lower
        return 0

    def _executeActivateOperation(self, setService):
        ops = [o for o in TestClient.clientMdib.descriptions.objects if
               isinstance(o, ActivateOperationDescriptorContainer)]
        testOp = random.choice(ops)

        operationTimeout = self.OPERATION_TIMEOUT
        if testOp.MaxTimeToFinish:
            operationTimeout = testOp.MaxTimeToFinish

        future = setService.activate(operationHandle=testOp.handle, value=None)
        result = future.result(timeout=operationTimeout)
        self.assertEqual(InvocationState.FINISHED, result.state)

    def shutdownConnection(self):
        """
        Shutdown connection (cancel subscription, close connection)
        """
        logger.info("Running shutdown connection test.")
        TestClient.sdcClient.stopAll()
        self.assertIsNone(TestClient.sdcClient._mdib)
