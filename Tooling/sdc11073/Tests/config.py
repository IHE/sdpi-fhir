"""
Configuration file.
"""
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