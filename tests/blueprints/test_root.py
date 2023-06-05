"""
Unit tests for helper functions within the root blueprint.
"""
import os
from unittest import TestCase
from src.blueprints.root import _generate_update_env_vars_file


def test_generate_update_env_vars_file():
    case = TestCase()
    input_existing_config = {
        "properties": {
            "containers": [
                {
                    "name": "dragondrop-engine-container-instance",
                    "properties": {
                        "command": [],
                        "environmentVariables": [
                            {"name": "DRAGONDROP_OLDENVVAR", "value": "old_var_value"},
                            {"name": "DRAGONDROP_OLDSECUREENVVAR"},
                        ],
                    },
                }
            ],
            "initContainers": [],
            "sku": "Standard",
        },
        "type": "Microsoft.ContainerInstance/containerGroups",
    }

    input_request_json = {"DRAGONDROP_JOBID": "new_var_value"}

    os.environ["DRAGONDROP_NEWSECUREENVVAR"] = "new_secure_value"
    expected_output = {
        "properties": {
            "containers": [
                {
                    "name": "dragondrop-engine-container-instance",
                    "properties": {
                        "command": [],
                        "environmentVariables": [
                            {
                                "name": "DRAGONDROP_NEWSECUREENVVAR",
                                "secureValue": "new_secure_value",
                            },
                            {"name": "DRAGONDROP_JOBID", "value": "new_var_value"},
                        ],
                    },
                }
            ],
            "initContainers": [],
            "sku": "Standard",
        },
        "type": "Microsoft.ContainerInstance/containerGroups",
    }

    output = _generate_update_env_vars_file(
        existing_config=input_existing_config,
        request_json=input_request_json,
    )

    case.assertDictEqual(expected_output, output)
