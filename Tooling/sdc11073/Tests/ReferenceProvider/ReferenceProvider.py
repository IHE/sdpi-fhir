import unittest
import json
import xmlrunner

from Tests.ReferenceProvider.TestCases import ReferenceProviderTests
from Tests.ReferenceProvider import TestDevice
from sdc11073.location import SdcLocation
from sdc11073.pysoap.soapenvelope import DPWSThisDevice, DPWSThisModel


def loadProviderConfig(config):
    try:
        with open(config) as f:
            fullConfig = json.loads(f.read())
            TestDevice.config = fullConfig["reference_provider"]

        dpwsModel = DPWSThisModel(manufacturer=TestDevice.config["dpwsModel"]["manufacturer"],
                                  manufacturerUrl=TestDevice.config["dpwsModel"]["manufacturerUrl"],
                                  modelName=TestDevice.config["dpwsModel"]["modelName"],
                                  modelNumber=TestDevice.config["dpwsModel"]["modelNumber"],
                                  modelUrl=TestDevice.config["dpwsModel"]["modelUrl"],
                                  presentationUrl=TestDevice.config["dpwsModel"]["presentationUrl"])

        dpwsDevice = DPWSThisDevice(friendlyName=TestDevice.config["dpwsDevice"]["friendlyName"],
                                    firmwareVersion=TestDevice.config["dpwsDevice"]["firmwareVersion"],
                                    serialNumber=TestDevice.config["dpwsDevice"]["serialNumber"])

        sdcLocation = SdcLocation(fac=TestDevice.config["location"]["fac"],
                                  poc=TestDevice.config["location"]["poc"],
                                  bed=TestDevice.config["location"]["bed"],
                                  flr=TestDevice.config["location"]["flr"],
                                  rm=TestDevice.config["location"]["rm"],
                                  bld=TestDevice.config["location"]["bld"])

        TestDevice.config["dpwsModel"] = dpwsModel
        TestDevice.config["dpwsDevice"] = dpwsDevice
        TestDevice.config["location"] = sdcLocation
    except FileNotFoundError:
        raise Exception("Config file not found. Make sure config.json is in the path specified.")


def runReferenceProviderTestSuite(endpoint, config, ca_dir):
    TestDevice.endpoint = endpoint
    TestDevice.ca_dir = ca_dir
    loadProviderConfig(config)
    suite = unittest.TestSuite()
    suite.addTest(ReferenceProviderTests('consumerConnection'))
    suite.addTest(ReferenceProviderTests('produceMetricUpdates'))
    suite.addTest(ReferenceProviderTests('produceAlertUpdates'))
    suite.addTest(ReferenceProviderTests('operationsExecuted'))

    runner = xmlrunner.XMLTestRunner()
    runner.run(suite)
