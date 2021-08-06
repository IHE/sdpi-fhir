import unittest

import xmlrunner

from Tests.ReferenceProvider.TestCases import ReferenceProviderTests
from Tests.ReferenceProvider import TestDevice

def runReferenceProviderTestSuite(endpoint):
    TestDevice.endpoint = endpoint
    suite = unittest.TestSuite()
    suite.addTest(ReferenceProviderTests('consumerConnection'))
    suite.addTest(ReferenceProviderTests('produceMetricUpdates'))
    suite.addTest(ReferenceProviderTests('produceAlertUpdates'))
    suite.addTest(ReferenceProviderTests('operationsExecuted'))

    runner = xmlrunner.XMLTestRunner()
    runner.run(suite)
