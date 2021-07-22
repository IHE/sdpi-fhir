import unittest

import xmlrunner

from Tooling.Tests.ReferenceConsumer.TestCases import ReferenceConsumerTests
from Tooling.Tests.ReferenceConsumer import TestClient

def runReferenceConsumerTestSuite(endpoint):
    TestClient.endpoint = endpoint
    suite = unittest.TestSuite()
    suite.addTest(ReferenceConsumerTests('discoverProvider'))
    suite.addTest(ReferenceConsumerTests('connectToProvider'))
    suite.addTest(ReferenceConsumerTests('readMdibOfProvider'))
    suite.addTest(ReferenceConsumerTests('testSubscribeToReports'))
    suite.addTest(ReferenceConsumerTests('checkPatientContextExists'))
    suite.addTest(ReferenceConsumerTests('checkLocationContextExists'))
    suite.addTest(ReferenceConsumerTests('checkMetricUpdates'))
    suite.addTest(ReferenceConsumerTests('checkAlertUpdates'))
    suite.addTest(ReferenceConsumerTests('executeOperation'))
    suite.addTest(ReferenceConsumerTests('shutdownConnection'))

    runner = xmlrunner.XMLTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    runReferenceConsumerTestSuite("24639edc-c215-11eb-bd49-f8cab80f9344")
