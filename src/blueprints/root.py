"""
Root url app blueprint.
"""
import os
import subprocess
import yaml
from azure.cli.core import get_default_cli
from azure.identity import DefaultAzureCredential
from flask import Blueprint, request, current_app

root = Blueprint("root", __name__)


@root.route("/", methods=["POST"])
def execute_cloud_run_job():
    """
    Execute the Cloud Run Job which is hosting the dragondrop.cloud
    core compute engine.
    """
    try:
        request_json = request.get_json()
        container_instance_id = os.getenv("CONTAINER_INSTANCE_ID")
        resource_group = os.getenv("RESOURCE_GROUP")

        current_app.logger.info(
            f"Authentication with the Azure Container Instance's managed identity."
        )
        default_credential = DefaultAzureCredential(managed_identity_client_id=os.getenv("USER_ASSIGNED_IDENTITY_ID"))
        current_app.logger.info(
            f"Default Azure Credential received without error."
        )
        # TODO: Test case here
        current_app.logger.info(f"Getting container instance configuration as .yml, test #1")
        result = subprocess.run(
            [
                "az",
                "container",
                "export",
                "--ids",
                container_instance_id,
                "-f",
                "./config.yml",
            ],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(
            f"#1 Std. Out: {result.stdout}\nStd. Error: {result.stderr}"
        )

        # TODO: Attempt number two, use the azure-cli command line to invoke the command
        current_app.logger.info(
            f"#2 Attempt:"
        )
        az_cli = get_default_cli()
        az_cli.invoke([
                "container",
                "export",
                "--ids",
                container_instance_id,
                "-f",
                "./config.yml",
            ])
        current_app.logger.info(
            f"#2 CLI Result: {az_cli.result.result}\nCLI Result Error: {az_cli.result.error}"
        )

        # TODO: Attempt number three, use the azure-cli to authenticate, and then invoke the command
        current_app.logger.info(
            f"#3 Attempt:"
        )
        # https://github.com/Azure/azure-cli/issues/22677#issuecomment-1384954612
        os.environ["APPSETTING_WEBSITE_SITE_NAME"] = "placeholder"

        az_cli = get_default_cli()
        az_cli.invoke([
            "login",
            "--identity",
            # "-u",
            # os.getenv("USER_ASSIGNED_IDENTITY_ID"),
        ])
        current_app.logger.info(
            f"#3 CLI Result: {az_cli.result.result}\nCLI Result Error: {az_cli.result.error}"
        )

        az_cli = get_default_cli()
        az_cli.invoke([
            "login",
            "--i",
            # "-u",
            # os.getenv("USER_ASSIGNED_IDENTITY_ID"),
        ])
        current_app.logger.info(
            f"#3 CLI Result: {az_cli.result.result}\nCLI Result Error: {az_cli.result.error}"
        )

        # result = subprocess.run(
        #     [
        #         "az",
        #         "login",
        #         "--identity",
        #         "-u",
        #         os.getenv("USER_ASSIGNED_IDENTITY_ID"),
        #     ],
        #     capture_output=True,
        #     text=True,
        # )
        # current_app.logger.info(
        #     f"Std. Out: {result.stdout}\nStd. Error: {result.stderr}"
        # )

        # Triggering the job to actually run
        current_app.logger.info(f"Getting container instance configuration as .yml")
        result = subprocess.run(
            [
                "az",
                "container",
                "export",
                "--ids",
                container_instance_id,
                "-f",
                "./config.yml",
            ],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(
            f"Std. Out: {result.stdout}\nStd. Error: {result.stderr}"
        )

        with open("./config.yml", "r") as f:
            existing_config = yaml.load(f, Loader=yaml.FullLoader)

        updated_config = _generate_update_env_vars_file(
            existing_config=existing_config, request_json=request_json
        )

        with open("./updated-config.yml", "w") as f:
            yaml.dump(updated_config, f)

        # Note: This command can take 1-2 minutes to run and as a result is a bit slow.
        result = subprocess.run(
            [
                "az",
                "container",
                "create",
                "-g",
                resource_group,
                "-f",
                "./updated-config.yml",
            ],
            capture_output=True,
            text=True,
        )
        current_app.logger.info(
            f"Std. Out: {result.stdout}\nStd. Error: {result.stderr}"
        )

        return "Azure Container Instance successfully updated and triggered", 201
    except Exception as e:
        return f"Server Error: {e}", 500


def _generate_update_env_vars_file(existing_config: dict, request_json: dict) -> dict:
    """
    Helper function to generate the right string for the update-env-vars feature flag.
    """
    updated_config = existing_config.copy()

    if "DRAGONDROP_JOBID" not in request_json:
        raise ValueError(
            "'DRAGONDROP_JOBID' must be included in the JSON body sent to this endpoint."
        )

    new_environment_variables = []

    # Setting secret environment variables
    for key, value in os.environ.items():
        if key.startswith("DRAGONDROP_"):
            new_environment_variables.append(
                {"name": key, "secureValue": value}
            )

    # Setting non-secret environment variables
    for key, value in request_json.items():
        new_environment_variables.append({"name": key, "value": value})

    updated_config["properties"]["containers"][0]["properties"][
        "environmentVariables"
    ] = new_environment_variables

    return updated_config
