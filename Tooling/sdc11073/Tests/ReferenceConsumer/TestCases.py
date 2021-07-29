import unittest
import random
import time
from queue import Queue, Full
from sdc11073 import observableproperties
from sdc11073 import wsdiscovery
from sdc11073.mdib import ClientMdibContainer
from sdc11073.namespaces import domTag
from sdc11073.mdib.descriptorcontainers import (NumericMetricDescriptorContainer, EnumStringMetricDescriptorContainer,
                                                StringMetricDescriptorContainer, AlertConditionDescriptorContainer)
from sdc11073.pmtypes import InvocationState
from Tests.TestLogger import logger
from Tests.ReferenceConsumer import TestClient
from Tests.config import REFERENCE_CONSUMER


class ReferenceConsumerTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resolveQueue = Queue(maxsize=1)

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
        self.assertIsNotNone(TestClient.sdcClient.metaData, msg="Test that metadata is retrieved successfully.")


class ReferenceConsumerConnectedTests(unittest.TestCase):
    OPERATION_TIMEOUT = 10
    UPDATE_TEST_TIME = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updatesQueue = Queue()
        self.testMetric = None
        self.testAlert = None

    def setUp(self):
        self.assertIsNotNone(TestClient.sdcClient, msg="Test client connection is established.")

    def readMdibOfProvider(self):
        """
        Read MDIB of the provider
        """
        logger.info("Running read Mdib of the provider provider test.")
        TestClient.clientMdib = ClientMdibContainer(TestClient.sdcClient)
        TestClient.clientMdib.initMdib()
        self.assertIsNotNone(TestClient.clientMdib, msg="Test that mdib of the provider exists.")

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
            self.assertIn(report, reports, msg="Test that report subscriptions exist.")

    def checkPatientContextExists(self):
        """
        Check that at least one patient context exists
        """
        logger.info("Running patient context test.")
        patientContextStates = TestClient.clientMdib.contextStates.NODETYPE.get(domTag('PatientContextState'), [])
        self.assertTrue(len(patientContextStates) >= 1, msg="Test that at least one patient context exists.")

    def checkLocationContextExists(self):
        """
        Check that at least one location context exists
        """
        logger.info("Running location context test.")
        locationContextStates = TestClient.clientMdib.contextStates.NODETYPE.get(domTag('LocationContextState'), [])
        self.assertTrue(len(locationContextStates) >= 1, msg="Test that at least one location context exists.")

    def checkMetricUpdates(self):
        """
        Check that metric updates for one metric arrive at least 5 times in 30 seconds
        """
        logger.info("Running metric updates test.")
        with self.updatesQueue.mutex:
            self.updatesQueue.queue.clear()

        ctp = REFERENCE_CONSUMER["metrics"]["containmentTreePath"]
        if ctp:
            handles = self._getItemsByContainmentTree(ctp)
            if handles:
                self.testMetric = handles.pop()  # take any if more than one found
        else:
            metrics = [m for m in TestClient.clientMdib.descriptions.objects
                       if isinstance(m, (NumericMetricDescriptorContainer, EnumStringMetricDescriptorContainer,
                                         StringMetricDescriptorContainer))]
            self.assertTrue(bool(metrics), msg="Test that there is at least one metric to select from.")
            self.testMetric = random.choice(metrics).handle

        self.assertTrue(bool(self.testMetric), msg="Found test metric.")
        logger.info("Running metric updates test for metric with handle %s", self.testMetric)
        with observableproperties.boundContext(TestClient.clientMdib, metricsByHandle=self._onMetricUpdate):
            updateCount = self._receiveUpdates()
            logger.info("Received %s metric updates", updateCount)
            self.assertTrue(updateCount >= 5, msg="Test that metric updates for one metric arrive at least 5 times in 30 seconds")

    def _getItemsByContainmentTree(self, ctp):
        try:
            codes = ctp.split(".")
            handles = {mds.handle for mds in TestClient.clientMdib.descriptions.codeId.get(codes[0], [])}
            for code in codes[1:]:
                children = TestClient.clientMdib.descriptions.codeId.get(code, [])
                children = [c for c in children if c.parentHandle in handles]
                handles = {c.handle for c in children}
            logger.info("Found handles %s for containment tree path %s", handles, ctp)
            return handles
        except:
            logger.error("Failed to find an Mdib item by containment tree path %s", ctp)
            return None

    def _receiveUpdates(self):
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

        code = REFERENCE_CONSUMER["alerts"]["code"]
        sourceCtp = REFERENCE_CONSUMER["alerts"]["sourceContainmentTreePath"]
        if code and sourceCtp:
            sources = self._getItemsByContainmentTree(sourceCtp)
            alertConditions = TestClient.clientMdib.descriptions.codeId.get(code, [])
            for alertCondition in alertConditions:
                if not isinstance(alertCondition, AlertConditionDescriptorContainer):
                    logger.warning("%s is not an AlertCondition", alertCondition.handle)
                    continue

                if {s.text for s in alertCondition.Source} == sources:
                    self.testAlert = alertCondition.handle
                    break
        else:
            alerts = [a for a in TestClient.clientMdib.descriptions.objects if isinstance(a, AlertConditionDescriptorContainer)]
            self.assertTrue(bool(alerts), msg="Test that there is at least one alert condition to select from.")
            self.testAlert = random.choice(alerts).handle

        self.assertTrue(bool(self.testAlert), msg="Found test alert.")
        logger.info("Executing AlertCondition update test for %s", self.testAlert)

        with observableproperties.boundContext(TestClient.clientMdib, alertByHandle=self._onAlertUpdate):
            updateCount = self._receiveUpdates()
            self.assertTrue(updateCount >= 5, msg="Test that alert updates of one alert condition arrive at least 5 times in 30 seconds")

    def _findOperation(self, operationType):
        testOp = None
        code = REFERENCE_CONSUMER["operations"][operationType]["code"]
        targetCtp = REFERENCE_CONSUMER["operations"][operationType]["targetContainmentTreePath"]
        logger.info("Searching for %s. Code provided %s with target containment tree path %s.", operationType, code, targetCtp)
        if code and targetCtp:
            target = self._getItemsByContainmentTree(targetCtp)
            operations = TestClient.clientMdib.descriptions.codeId.get(code, [])
            for operation in operations:
                if operationType not in operation.NODETYPE.text:
                    logger.warning("%s is not an %s", operation.handle, type)
                    continue

                if operation.OperationTarget in target:
                    testOp = operation
                    break
        else:
            ops = [o for o in TestClient.clientMdib.descriptions.objects if operationType in o.NODETYPE.text]
            if ops:
                testOp = random.choice(ops)

        return testOp

    def executeSetStringOperation(self):
        """
           Execute external control operations (any SetString operation that exists in the
           containment tree, if none exist: skip test) by checking the ultimate transaction
           result is "finished"
       """
        logger.info("Executing test for SetStringOperation.")
        testOp = self._findOperation("SetStringOperation")

        if testOp:
            logger.info("SetStringOperation found %s.", testOp.handle)

            operationTimeout = self.OPERATION_TIMEOUT
            if testOp.MaxTimeToFinish:
                operationTimeout = testOp.MaxTimeToFinish

            state = TestClient.clientMdib.states.descriptorHandle.getOne(testOp.handle, allowNone=True)
            value = "test"
            if state.AllowedValues:
                value = random.choice(state.AllowedValues)
            setService = TestClient.sdcClient.client('Set')
            future = setService.setString(operationHandle=testOp.handle, requestedString=value)
            result = future.result(timeout=operationTimeout)
            self.assertEqual(InvocationState.FINISHED, result.state,
                             msg="Test that SetStringOperation execution ends with the transaction result is 'finished'")
        else:
            logger.warning("No SetStringOperation found.")

    def executeSetValueOperation(self):
        """
            Execute external control operations (any SetValue operation that exists in the
            containment tree, if none exist: skip test) by checking the ultimate transaction
            result is "finished"
        """
        logger.info("Executing test for SetValueOperation.")
        testOp = self._findOperation("SetValueOperation")

        if testOp:
            logger.info("SetValueOperation found %s.", testOp.handle)

            operationTimeout = self.OPERATION_TIMEOUT
            if testOp.MaxTimeToFinish:
                operationTimeout = testOp.MaxTimeToFinish

            state = TestClient.clientMdib.states.descriptorHandle.getOne(testOp.handle, allowNone=True)
            value = 0
            if state.AllowedRange:
                value = self._getValueFromRange(state.AllowedRange)
            setService = TestClient.sdcClient.client('Set')
            future = setService.setNumericValue(operationHandle=testOp.handle, requestedNumericValue=value)
            result = future.result(timeout=operationTimeout)
            self.assertEqual(InvocationState.FINISHED, result.state,
                             msg="Test that SetValueOperation execution ends with the transaction result is 'finished'")
        else:
            logger.warning("No SetValueOperation found.")

    def _getValueFromRange(self, allowedRange):
        anyRange = random.choice(allowedRange)
        if anyRange.Upper:
            return anyRange.Upper
        if anyRange.Lower:
            return anyRange.Lower
        return 0

    def executeActivateOperation(self):
        """
            Execute external control operations (any Activate operation that exists in the
            containment tree, if none exist: skip test) by checking the ultimate transaction
            result is "finished"
        """
        logger.info("Executing test for ActivateOperation.")
        testOp = self._findOperation("ActivateOperation")

        if testOp:
            logger.info("ActivateOperation found %s.", testOp.handle)

            operationTimeout = self.OPERATION_TIMEOUT
            if testOp.MaxTimeToFinish:
                operationTimeout = testOp.MaxTimeToFinish

            setService = TestClient.sdcClient.client('Set')
            future = setService.activate(operationHandle=testOp.handle, value=None)
            result = future.result(timeout=operationTimeout)
            self.assertEqual(InvocationState.FINISHED, result.state,
                             msg="Test that ActivateOperation execution ends with the transaction result is 'finished'")
        else:
            logger.warning("No ActivateOperation found.")

    def shutdownConnection(self):
        """
        Shutdown connection (cancel subscription, close connection)
        """
        logger.info("Running shutdown connection test.")
        TestClient.sdcClient.stopAll()
        self.assertIsNone(TestClient.sdcClient._mdib, msg="Test that connection shutdown is successful.")
