import unittest
import json
import xmlrunner

from Tests.ReferenceConsumer.TestCases import ReferenceConsumerTests, ReferenceConsumerConnectedTests
from Tests.ReferenceConsumer import TestClient

def loadConsumerConfig(config):
    try:
        with open(config) as f:
            fullConfig = json.loads(f.read())
            TestClient.config = fullConfig["reference_consumer"]
    except FileNotFoundError:
        raise Exception("Config file not found. Make sure config.json is in the path specified.")

def runReferenceConsumerTestSuite(endpoint, config, caDir, testRunner=None):
    TestClient.endpoint = endpoint
    TestClient.ca_dir = caDir
    loadConsumerConfig(config)
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
    if testRunner:
        runner = testRunner
    else:
        runner = xmlrunner.XMLTestRunner()
    return runner.run(suite)
