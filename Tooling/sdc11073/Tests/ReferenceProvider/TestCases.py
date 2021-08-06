import logging
import random
import time
import unittest
from queue import Queue, Full, Empty
from uuid import UUID

from sdc11073 import pmtypes
from sdc11073 import wsdiscovery
from sdc11073.mdib import DeviceMdibContainer
from sdc11073.mdib.descriptorcontainers import (NumericMetricDescriptorContainer, EnumStringMetricDescriptorContainer,
                                                StringMetricDescriptorContainer, AlertConditionDescriptorContainer)
from sdc11073.namespaces import domTag
from sdc11073.roles.providerbase import ProviderRole

from Tests.ReferenceProvider import TestDevice
from Tests.TestLogger import logger
from Tests.config import REFERENCE_PROVIDER
from Tests.utils import getItemsByContainmentTree


class ReferenceProviderTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testMetric = None
        self.testAlert = None
        self.probeQueue = Queue(maxsize=1)
        self.subscribedQueue = Queue(maxsize=1)

    def setupTestDevice(self):
        TestDevice.deviceMdib = DeviceMdibContainer.fromMdibFile(REFERENCE_PROVIDER["mdibPath"])
        TestDevice.publishingDevice = TestDevice.PublishingSdcDevice(ws_discovery=self.wsDiscovery,
                                                                     my_uuid=UUID(TestDevice.endpoint),
                                                                     model=REFERENCE_PROVIDER["dpwsModel"],
                                                                     device=REFERENCE_PROVIDER["dpwsDevice"],
                                                                     deviceMdibContainer=TestDevice.deviceMdib,
                                                                     logLevel=logging.INFO)

    def consumerConnection(self):
        """
        Discovery of a provider with a specific endpoint reference address
        See that Probe is answered
        See that Resolve is answered
        """
        logger.info("Running discovery of provider test.")
        # self.wsDiscovery = wsdiscovery.WSDiscoveryBlacklist()
        self.wsDiscovery = wsdiscovery.WSDiscoverySingleAdapter("Loopback Pseudo-Interface 1")
        self.setupTestDevice()
        self.wsDiscovery.setOnProbeCallback(self._onProbe)
        self.wsDiscovery.start()
        TestDevice.publishingDevice.startAll()
        TestDevice.publishingDevice.setLocation(REFERENCE_PROVIDER["location"], [])

        probeAnswered = self._getItemFromQueue(self.probeQueue, timeout=REFERENCE_PROVIDER["probeTimeout"])
        self.assertTrue(probeAnswered, msg="Test that probe answered.")
        secs = 0
        hasSubsciptions = False
        while secs < REFERENCE_PROVIDER["consumerConnectionTimeout"]:
            hasSubsciptions = bool(TestDevice.publishingDevice.subscriptionsManager._subscriptions._idxDefs['netloc'])
            if hasSubsciptions:
                break
            secs += 1
            time.sleep(1)
        self.assertTrue(hasSubsciptions, msg="Client connected.")
        self.allowOperationControl()

    def allowOperationControl(self):
        # find all operations
        allOps = TestDevice.deviceMdib.descriptions.nodeName.get(domTag('Operation'))
        if allOps is None:
            logger.warning("No operations found int the Mdib")
            return

        p = ProviderRole(None)
        for operationDescriptor in allOps:
            operation = p._mkOperationFromOperationDescriptor(operationDescriptor,
                                                  currentArgumentHandler=self._handleOperation)
            TestDevice.publishingDevice.registerOperation(operation)

    def _handleOperation(self, operation, value):
        logger.debug("Handling of operation %s with value %s", operation, value)
        TestDevice.operationsQueue.put_nowait(True)

    def _getItemFromQueue(self, queue, timeout=5):
        try:
            return queue.get(timeout=timeout)
        except:
            return None

    def _onProbe(self, netloc, _):
        logger.info("Received probe from %s", netloc)
        try:
            self.probeQueue.put_nowait(True)
        except Full:
            logger.debug("More than one probe received %s", netloc)

    def produceMetricUpdates(self):
        ctp = REFERENCE_PROVIDER["metrics"]["containmentTreePath"]
        if ctp:
            handles = getItemsByContainmentTree(TestDevice.deviceMdib, ctp)
            if handles:
                self.testMetric = TestDevice.deviceMdib.descriptions.handle.getOne(handles.pop())
        else:
            metrics = [m for m in TestDevice.deviceMdib.descriptions.objects
                       if isinstance(m, (NumericMetricDescriptorContainer, EnumStringMetricDescriptorContainer,
                                         StringMetricDescriptorContainer))]
            self.assertTrue(bool(metrics), msg="Test that there is at least one metric to select from.")
            self.testMetric = random.choice(metrics)

        value = 0
        with self.assertLogs('sdc.device.subscrMgr', level='ERROR') as cm:
            # TODO: this to be replaced with python 3.10 https://bugs.python.org/issue39385
            logging.getLogger('sdc.device.subscrMgr').error("TEST")
            for x in range(REFERENCE_PROVIDER["stateUpdates"]):
                if self.testMetric.TechnicalRange:
                    # if both Upper and Lower available
                    if self.testMetric.TechnicalRange[0].Lower and self.testMetric.TechnicalRange[0].Upper:
                        if x % 2 == 0:
                            value = self.testMetric.TechnicalRange[0].Lower
                        else:
                            value = self.testMetric.TechnicalRange[0].Upper

                    # if only lower range is available
                    elif self.testMetric.TechnicalRange[0].Lower:
                        value = self.testMetric.TechnicalRange[0].Lower + x
                    # if only upper range is available
                    elif self.testMetric.TechnicalRange[0].Upper:
                        value = self.testMetric.TechnicalRange[0].Upper - x
                # if no range available
                else:
                    value = random.randint()

                with TestDevice.deviceMdib.mdibUpdateTransaction(setDeterminationTime=True) as mgr:
                    st = mgr.getMetricState(self.testMetric.handle)
                    if st.metricValue is None:
                        st.mkMetricValue()
                    st.metricValue.Validity = pmtypes.MeasurementValidity.VALID
                    st.metricValue.Value = value
                    logger.debug("Setting metric %s value to %s", self.testMetric.handle, value)

                time.sleep(REFERENCE_PROVIDER["stateUpdateTimeout"])
            self.assertEqual(cm.output, ["ERROR:sdc.device.subscrMgr:TEST"])

    def produceAlertUpdates(self):
        code = REFERENCE_PROVIDER["alerts"]["code"]
        sourceCtp = REFERENCE_PROVIDER["alerts"]["sourceContainmentTreePath"]
        if code and sourceCtp:
            sources = getItemsByContainmentTree(TestDevice.deviceMdib, sourceCtp)
            alertConditions = TestDevice.deviceMdib.descriptions.codeId.get(code, [])
            for alertCondition in alertConditions:
                if not isinstance(alertCondition, AlertConditionDescriptorContainer):
                    logger.warning("%s is not an AlertCondition", alertCondition.handle)
                    continue

                if {s.text for s in alertCondition.Source} == sources:
                    self.testAlert = alertCondition.handle
                    break
        else:
            alerts = [a for a in TestDevice.deviceMdib.descriptions.objects if
                      isinstance(a, AlertConditionDescriptorContainer)]
            self.assertTrue(bool(alerts), msg="Test that there is at least one alert condition to select from.")
            self.testAlert = random.choice(alerts).handle
        with self.assertLogs('sdc.device.subscrMgr', level='ERROR') as cm:
            # TODO: this to be replaced with python 3.10 https://bugs.python.org/issue39385
            logging.getLogger('sdc.device.subscrMgr').error("TEST")
            for x in range(REFERENCE_PROVIDER["stateUpdates"]):
                with TestDevice.deviceMdib.mdibUpdateTransaction(setDeterminationTime=True) as mgr:
                    st = mgr.getAlertState(self.testAlert)
                    st.Presence = True
                    st.ActivationState = pmtypes.AlertActivation.ON
                logger.debug("State update for %s", self.testAlert)
                time.sleep(REFERENCE_PROVIDER["stateUpdateTimeout"])
            self.assertEqual(cm.output, ["ERROR:sdc.device.subscrMgr:TEST"])

    def operationsExecuted(self):
        opExecutionTimeout = REFERENCE_PROVIDER["operationExecutionTimeout"]
        opExecuted = False
        while opExecutionTimeout > 0:
            try:
                opExecuted = TestDevice.operationsQueue.get_nowait()
            except Empty:
                pass
            time.sleep(1)
            opExecutionTimeout -= 1
        self.assertTrue(opExecuted, msg="At least one operation was executed.")
