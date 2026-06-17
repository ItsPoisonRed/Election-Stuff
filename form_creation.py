from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


def get_candidate_names():
    candidate_names = []
    while True:
        name = input("Enter a candidate name, or leave blank to finish: ").strip()
        if not name:
            break
        candidate_names.append(name)
    return candidate_names


def get_rank_string(n):
    if 11 <= (n % 100) <= 13:
        return str(n) + "th"
    return str(n) + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
]
DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

store = file.Storage("token.json")
creds = None
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

description = input("Enter the description of the Candidates (leave blank to skip): ")

description += (
    " \nEach candidate is ranked to the level of preference, so the highest rank is 1."
)

NEW_FORM = {
    "info": {
        "title": "Whitefish High School Election",
    }
}

number_of_positions = int(input("Enter the number of positions: "))

candidate_dict = {}

for i in range(number_of_positions):
    position = input("Enter the Position Name: ").strip()
    candidate_dict[position] = get_candidate_names()

result = form_service.forms().create(body=NEW_FORM).execute()
form_id = result["formId"]

requests = [
    {
        "updateFormInfo": {
            "info": {
                "description": description,
                "documentTitle": "Whitefish High School Election",
            },
            "updateMask": "description",
        }
    }
]
index = 0

for position, candidates in candidate_dict.items():
    for rank in range(1, len(candidates) + 1):
        requests.append(
            {
                "createItem": {
                    "item": {
                        "title": f"{position} - {get_rank_string(rank)} Choice",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [{"value": c} for c in candidates],
                                },
                            }
                        },
                    },
                    "location": {"index": index},
                }
            }
        )
    index += 1

if requests:
    update_body = {"requests": requests}
    form_service.forms().batchUpdate(formId=form_id, body=update_body).execute()
