"""
Root url app blueprint.
"""
import os
import traceback
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.identity import ManagedIdentityCredential
from flask import Blueprint, request, current_app

root = Blueprint("root", __name__)


@root.route("/", methods=["POST"])
def execute_container_instance():
    """
    Execute the container instance which is hosting the dragondrop.cloud
    core compute engine.
    """
    try:
        request_json = request.get_json()

        CONTAINER_GROUP_ID = os.getenv("CONTAINER_INSTANCE_ID")
        RESOURCE_GROUP = os.getenv("RESOURCE_GROUP")
        SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")
        MANAGED_ID_CLIENT_ID = os.getenv("MANAGED_ID_CLIENT_ID")

        current_app.logger.info(
            f"Authentication with the Azure Container Instance's managed identity."
        )
        default_credential = ManagedIdentityCredential(client_id=MANAGED_ID_CLIENT_ID)
        current_app.logger.info(f"Default Azure Credential received without error.")

        container_instance_client = ContainerInstanceManagementClient(
            credential=default_credential,
            subscription_id=SUBSCRIPTION_ID,
        )

        container_group_def = container_instance_client.container_groups.get(
            RESOURCE_GROUP, CONTAINER_GROUP_ID
        )

        new_env_vars = _generate_env_vars(request_json=request_json)

        container_group_def.containers[0].environment_variables = new_env_vars

        current_app.logger.info(
            f"Updating the container instance with definition:\n{container_group_def}"
        )
        current_app.logger.info(f"New environment variables to set:\n{new_env_vars}")

        container_group = (
            container_instance_client.container_groups.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                container_group_name=CONTAINER_GROUP_ID,
                container_group=container_group_def,
            ).result()
        )

        current_app.logger.info(
            f"Done updating the container instance: {container_group}"
        )

        return "Azure Container Instance successfully updated and triggered", 201
    except Exception as e:
        stack_trace = traceback.format_exc()
        current_app.logger.info(f"Server error w/stack trace:\n{stack_trace}")
        return f"Server Error: {e}", 500


def _generate_env_vars(request_json: dict) -> list:
    """
    Helper function to generate the right string for the update-env-vars feature flag.
    """
    if "DRAGONDROP_JOBID" not in request_json:
        raise ValueError(
            "'DRAGONDROP_JOBID' must be included in the JSON body sent to this endpoint."
        )

    new_environment_variables = []

    # TODO: Debugging what is going on with the duplicated environment variables:
    current_app.logger.info(
        f"Within _generate_env_vars:\nrequest_json values:\n{request_json}"
    )
    current_app.logger.info(f"environment values:\n{os.environ}\n\n")

    # Setting secret environment variables
    for key, value in os.environ.items():
        if key.startswith("DRAGONDROP_"):
            new_environment_variables.append({"name": key, "secureValue": value})

    # Setting non-secret environment variables
    for key, value in request_json.items():
        new_environment_variables.append({"name": key, "value": value})

    return new_environment_variables
