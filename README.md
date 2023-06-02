# container-instance-http-trigger
Azure Container App service that provides an HTTPS endpoint for triggering an Azure Container instance.

## Purpose
Azure Container Instances are the easiest way to host the dragondrop.cloud core container. Unfortunately, it is
not possible to trigger an Azure Container Instance via an HTTPS request.

Instead, we can make an https request to an Azure Container App-hosted service, which in turn handles executing the Container Instance.

## Quick Start (with Terraform)
Our Terraform module for the dragondrop.cloud container creates a Azure Container App service that hosts the container created by this repository.

The repository that defines this module can be found [here](https://github.com/dragondrop-cloud/terraform-azurerm-dragondrop-compute).
