import webbrowser
from boto3.session import Session


def get_oidc_token(session: Session):
    start_url = "https://uk-digital-identity.awsapps.com/start"
    sso_oidc = session.client("sso-oidc")
    client_creds = sso_oidc.register_client(
        clientName="joe-roberts",
        clientType="public",
    )
    device_authorization = sso_oidc.start_device_authorization(
        clientId=client_creds["clientId"],
        clientSecret=client_creds["clientSecret"],
        startUrl=start_url,
    )
    url = device_authorization["verificationUriComplete"]
    device_code = device_authorization["deviceCode"]
    expires_in = device_authorization["expiresIn"]
    interval = device_authorization["interval"]
    webbrowser.open(url, autoraise=True)
    for _ in range(1, expires_in // interval + 1):
        try:
            return sso_oidc.create_token(
                grantType="urn:ietf:params:oauth:grant-type:device_code",
                deviceCode=device_code,
                clientId=client_creds["clientId"],
                clientSecret=client_creds["clientSecret"],
            )
        except sso_oidc.exceptions.AuthorizationPendingException:
            pass


def get_account_roles(session: Session, access_token: str, account_id: str):
    sso = session.client("sso")
    paginator = sso.get_paginator("list_account_roles").paginate(
        accessToken=access_token, accountId=account_id
    )

    for page in paginator:
        for role in page["roleList"]:
            yield role


def get_accounts(session: Session, access_token: str):
    sso = session.client("sso")
    paginator = sso.get_paginator("list_accounts").paginate(accessToken=access_token)

    for page in paginator:
        for account in page["accountList"]:
            yield account
