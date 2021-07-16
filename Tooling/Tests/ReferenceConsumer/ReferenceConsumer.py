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
    suite.addTest(ReferenceConsumerTests('checkPatientContextExists'))
    suite.addTest(ReferenceConsumerTests('checkLocationContextExists'))
    # suite.addTest(ReferenceConsumerTests('checkMetricUpdates'))
    runner = xmlrunner.XMLTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    runReferenceConsumerTestSuite("https://127.0.0.1:58591/24639edcc21511ebbd49f8cab80f9344")
