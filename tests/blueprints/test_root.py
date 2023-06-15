"""
Unit tests for helper functions within the root blueprint.
"""
import os
from unittest import TestCase
from src.blueprints.root import _generate_env_vars


def test_generate_update_env_vars_file():
    case = TestCase()
    input_request_json = {"DRAGONDROP_JOBID": "new_var_value"}

    os.environ["DRAGONDROP_NEWSECUREENVVAR"] = "new_secure_value"
    expected_output = [
        {
            "name": "DRAGONDROP_NEWSECUREENVVAR",
            "secureValue": "new_secure_value",
        },
        {"name": "DRAGONDROP_JOBID", "value": "new_var_value"},
    ]

    output = _generate_env_vars(
        request_json=input_request_json,
    )

    case.assertListEqual(expected_output, output)
