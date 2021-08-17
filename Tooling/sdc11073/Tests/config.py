"""
Configuration file.
"""
from sdc11073.location import SdcLocation
from sdc11073.pysoap.soapenvelope import DPWSThisDevice, DPWSThisModel

REFERENCE_CONSUMER = {
    "metrics": {
        "containmentTreePath": None  # containment tree path by codes for example: 12324.555666.777888.991010
    },
    "alerts": {
        "code": None,  # codeId of the AlertCondition for Example: 12345
        "sourceContainmentTreePath": None  # containment tree path by codes for example: 12324.555666.777888.991010
    },
    "operations": {
        "SetStringOperation":
             {
                "code": None,  # codeId of the SetStringOperation for Example: 12345
                "targetContainmentTreePath": None,  # containment tree path by codes for example: 12324.555666.777888.991010
             },
        "SetValueOperation":
             {
                "code": None,  # codeId of the SetValueOperation for Example: 12345
                "targetContainmentTreePath": None,  # containment tree path by codes for example: 12324.555666.777888.991010
             },
        "ActivateOperation":
             {
                "code": None,  # codeId of the ActivateOperation for Example: 12345
                "targetContainmentTreePath": None,  # containment tree path by codes for example: 12324.555666.777888.991010
             }
    }
}

REFERENCE_PROVIDER = {
    "network":"Loopback Pseudo-Interface 1",
    "dpwsModel": DPWSThisModel(manufacturer="Manufacturer",
                              manufacturerUrl="ManufacturerUrl",
                              modelName="ModelName",
                              modelNumber="ModelNumber",
                              modelUrl="ModelUrl",
                              presentationUrl="PresentationUrl"),

    "dpwsDevice": DPWSThisDevice(friendlyName="FriendlyName",
                                firmwareVersion="FirmwareVersion",
                                serialNumber="SerialNumber"),

    "mdibPath": "path to mdib.xml",

    "location": SdcLocation(fac="FAC",
                            poc="POC",
                            bed="BED",
                            flr="FLR",
                            rm="ROOM",
                            bld="BLD"),

    "probeTimeout": 10,
    "stateUpdateTimeout": 2,
    "stateUpdates": 5,
    "consumerConnectionTimeout": 10,
    "operationExecutionTimeout": 10,
    "metrics": {
        "containmentTreePath": None  # containment tree path by codes for example: 12324.555666.777888.991010
    },
    "alerts": {
        "code": None,  # codeId of the AlertCondition for Example: 12345
        "sourceContainmentTreePath": None  # containment tree path by codes for example: 12324.555666.777888.991010
    }
}
