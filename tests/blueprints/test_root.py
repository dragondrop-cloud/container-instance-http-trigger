from unittest import TestCase
from src.blueprints.root import _generate_update_env_vars_file


# TODO: Finish implementing this unit test
def test_generate_update_env_vars_file():
    case = TestCase()
    input_existing_config = {}
    input_request_json = {}

    expected_output = {}

    output = _generate_update_env_vars_file(
        existing_config=input_existing_config,
        request_json=input_request_json,
    )

    case.assertDictEqual(expected_output, output)
