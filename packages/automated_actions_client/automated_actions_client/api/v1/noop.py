from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.action import Action
from ...models.http_validation_error import HTTPValidationError
from ...models.noop_param import NoopParam
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: NoopParam,
    labels: None | Unset | list[str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    json_labels: None | Unset | list[str]
    if isinstance(labels, Unset):
        json_labels = UNSET
    elif isinstance(labels, list):
        json_labels = labels

    else:
        json_labels = labels
    params["labels"] = json_labels

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/noop",
        "params": params,
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Action | HTTPValidationError | None:
    if response.status_code == 202:
        response_202 = Action.from_dict(response.json())

        return response_202
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Action | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: NoopParam,
    labels: None | Unset | list[str] = UNSET,
) -> Response[Action | HTTPValidationError]:
    """Run Noop

     Run a noop action

    Args:
        labels (Union[None, Unset, list[str]]):
        body (NoopParam):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Action, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        labels=labels,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: NoopParam,
    labels: None | Unset | list[str] = UNSET,
) -> Action | HTTPValidationError | None:
    """Run Noop

     Run a noop action

    Args:
        labels (Union[None, Unset, list[str]]):
        body (NoopParam):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Action, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        labels=labels,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: NoopParam,
    labels: None | Unset | list[str] = UNSET,
) -> Response[Action | HTTPValidationError]:
    """Run Noop

     Run a noop action

    Args:
        labels (Union[None, Unset, list[str]]):
        body (NoopParam):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Action, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        labels=labels,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: NoopParam,
    labels: None | Unset | list[str] = UNSET,
) -> Action | HTTPValidationError | None:
    """Run Noop

     Run a noop action

    Args:
        labels (Union[None, Unset, list[str]]):
        body (NoopParam):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Action, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            labels=labels,
        )
    ).parsed


from typing import Annotated

import typer
from rich import print as rich_print

app = typer.Typer()


@app.command(help="Run a noop action")
def noop(
    ctx: typer.Context,
    alias: Annotated[str, typer.Option(help="")],
    description: Annotated[str, typer.Option(help="")] = "no description",
    labels: Annotated[
        None | list[str],
        typer.Option(
            help="""

    """
        ),
    ] = None,
) -> None:
    rich_print(
        sync(
            labels=labels,
            body=NoopParam(
                alias=alias,
                description=description,
            ),
            client=ctx.obj["client"],
        )
    )
