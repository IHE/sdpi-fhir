import unittest

import xmlrunner

from Tests.ReferenceConsumer.TestCases import ReferenceConsumerTests, ReferenceConsumerConnectedTests
from Tests.ReferenceConsumer import TestClient

def runReferenceConsumerTestSuite(endpoint):
    TestClient.endpoint = endpoint
    suite = unittest.TestSuite()
    suite.addTest(ReferenceConsumerTests('discoverProvider'))
    suite.addTest(ReferenceConsumerTests('connectToProvider'))
    suite.addTest(ReferenceConsumerConnectedTests('readMdibOfProvider'))
    suite.addTest(ReferenceConsumerConnectedTests('testSubscribeToReports'))
    suite.addTest(ReferenceConsumerConnectedTests('checkPatientContextExists'))
    suite.addTest(ReferenceConsumerConnectedTests('checkLocationContextExists'))
    suite.addTest(ReferenceConsumerConnectedTests('checkMetricUpdates'))
    suite.addTest(ReferenceConsumerConnectedTests('checkAlertUpdates'))
    suite.addTest(ReferenceConsumerConnectedTests('executeSetStringOperation'))
    suite.addTest(ReferenceConsumerConnectedTests('executeActivateOperation'))
    suite.addTest(ReferenceConsumerConnectedTests('executeSetValueOperation'))
    suite.addTest(ReferenceConsumerConnectedTests('shutdownConnection'))

    runner = xmlrunner.XMLTestRunner()
    runner.run(suite)
