import asyncio

from azure.identity import DeviceCodeCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.item.user_item_request_builder import UserItemRequestBuilder

from template_fastapi.settings.microsoft_graphs import get_microsoft_graph_settings


async def main():
    # Load settings
    settings = get_microsoft_graph_settings()
    scopes = settings.microsoft_graph_user_scopes.split(" ")

    print(settings.model_dump_json(indent=2))
    print(scopes)

    # Add authentication
    device_code_credential = DeviceCodeCredential(
        client_id=settings.microsoft_graph_client_id,
        tenant_id=settings.microsoft_graph_tenant_id,
    )
    # access_token = device_code_credential.get_token(*scopes)
    # print(f"Access Token: {access_token.token}")

    # Get user profile
    # Only request specific properties using $select
    query_params = UserItemRequestBuilder.UserItemRequestBuilderGetQueryParameters(
        select=[
            "displayName",
            "mail",
            "userPrincipalName",
        ]
    )
    request_config = UserItemRequestBuilder.UserItemRequestBuilderGetRequestConfiguration(query_parameters=query_params)
    user_client = GraphServiceClient(
        credentials=device_code_credential,
        scopes=scopes,
    )

    user = await user_client.me.get(request_configuration=request_config)
    print(f"User: {user.display_name} ({user.mail})")


# Run main
asyncio.run(main())
