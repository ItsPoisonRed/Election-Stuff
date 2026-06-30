from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


def login_google() -> discovery.Resource:
    """
    Logs in to Google Forms API and returns the form service object.
    """

    SCOPES: list[str] = [
        "https://www.googleapis.com/auth/forms.body",
        "https://www.googleapis.com/auth/forms.responses.readonly",
    ]
    DISCOVERY_DOC: str = "https://forms.googleapis.com/$discovery/rest?version=v1"

    store: file.Storage = file.Storage("token.json")
    creds: client.OAuth2Credentials | None = None
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("client_secrets.json", SCOPES)
        creds = tools.run_flow(flow, store)

    form_service = discovery.build(
        "forms",
        "v1",
        http=creds.authorize(Http()),
        discoveryServiceUrl=DISCOVERY_DOC,
        static_discovery=False,
    )

    return form_service
