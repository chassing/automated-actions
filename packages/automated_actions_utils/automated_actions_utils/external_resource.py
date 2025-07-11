import logging
from enum import StrEnum

from automated_actions.config import settings
from pydantic import BaseModel

from automated_actions_utils.gql_client import GQLClient
from automated_actions_utils.gql_definitions.tasks.external_resources_namespaces import (
    NamespaceTerraformProviderResourceAWSV1,
    NamespaceTerraformResourceAWSV1,
)
from automated_actions_utils.gql_definitions.tasks.external_resources_namespaces import (
    query as external_resources_namespaces,
)

log = logging.getLogger(__name__)


class ExternalResourceAppInterfaceError(Exception):
    """Exception raised when an external resource is not found in app-interface."""


class VaultSecret(BaseModel):
    """Represents a Vault secret with its path, field, version, and format."""

    path: str
    field: str
    version: int | None
    q_format: str | None


class AwsAccount(BaseModel):
    """Represents an AWS account with its name, automation token, and region."""

    name: str
    automation_token: VaultSecret
    region: str


class ExternalResource(BaseModel):
    """Represents an external resource with its identifier, region, and AWS account information."""

    identifier: str
    region: str | None
    account: AwsAccount
    cluster: str
    namespace: str
    output_resource_name: str | None


class ExternalResourceProvider(StrEnum):
    """Enum representing the provider of an external resource."""

    RDS = "rds"
    ELASTICACHE = "elasticache"


def is_searched_resource(
    identifier: str,
    provider: ExternalResourceProvider,
    resource: NamespaceTerraformResourceAWSV1,
) -> bool:
    """Determines if the current resource is the one being searched for."""
    return (
        resource.identifier == identifier
        and resource.provider == provider.value
        and not getattr(resource, "delete", False)
    )


def get_external_resource(
    account: str, identifier: str, provider: ExternalResourceProvider
) -> ExternalResource:
    """Retrieves external resource information from app-interface.

    Args:
        account: The AWS account name.
        identifier: The identifier of the external resource.

    Returns:
        An ExternalResource object containing the resource's details.

    Raises:
        ExternalResourceAppInterfaceError: If no external resources are found,
                                           or if the specified resource is not found.
    """
    gql_client = GQLClient(
        url=settings.qontract_server_url, token=settings.qontract_server_token
    )
    namespaces = external_resources_namespaces(gql_client.query).namespaces

    if not namespaces:
        raise ExternalResourceAppInterfaceError(
            "No external resources found in app-interface."
        )

    for namespace in namespaces:
        if namespace.delete:
            # exclude deleted namespaces
            continue

        for er in namespace.external_resources or []:
            if not isinstance(er, NamespaceTerraformProviderResourceAWSV1):
                continue
            if er.provisioner.name == account:
                for r in er.resources:
                    if not is_searched_resource(
                        identifier=identifier, provider=provider, resource=r
                    ):
                        continue

                    return ExternalResource(
                        identifier=identifier,
                        region=getattr(r, "region", None),
                        account=AwsAccount(
                            name=account,
                            automation_token=VaultSecret(
                                path=er.provisioner.automation_token.path,
                                field=er.provisioner.automation_token.field,
                                version=er.provisioner.automation_token.version,
                                q_format=er.provisioner.automation_token.q_format,
                            ),
                            region=er.provisioner.resources_default_region,
                        ),
                        cluster=namespace.cluster.name,
                        namespace=namespace.name,
                        output_resource_name=r.output_resource_name,
                    )

    raise ExternalResourceAppInterfaceError(
        f"External resource {identifier} not found in account {account}."
    )
