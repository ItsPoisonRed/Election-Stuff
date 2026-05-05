from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


def get_candidate_names():
    candidate_names=[]
    while True:
        name=input("Enter a candidate name, or leave blank to finish: ").strip()
        if not name:
            break
        candidate_names.append(name)
    return candidate_names

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly"
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

NEW_FORM = {
    "info": {
        "title": "Whitefish High School Election",
    }
}

number_of_positions=int(input("Enter the number of positions: "))

candidate_dict={}

for i in range(number_of_positions):
    position=input("Enter the Position Name: ").strip()
    candidate_dict[position]=get_candidate_names()

result = form_service.forms().create(body=NEW_FORM).execute()
form_id = result["formId"]

requests = [
    {
        "updateFormInfo": {
            "info": {
                "description": "Each candidate is ranked to the level of preference, so the highest rank is 1."
            },
            "updateMask": "description"
        }
    }
]
index = 0

def get_rank_string(n):
    if 11 <= (n % 100) <= 13:
        return str(n) + 'th'
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')

for position, candidates in candidate_dict.items():
    num_candidates = len(candidates)
    columns = [{"value": get_rank_string(i + 1)} for i in range(num_candidates)]
    questions = [{"required": True, "rowQuestion": {"title": candidate}} for candidate in candidates]
    requests.append({
        "createItem": {
            "item": {
                "title": f"Rank the candidates for {position}",
                "questionGroupItem": {
                    "grid": {
                        "columns": {
                            "type": "RADIO",
                            "options": columns
                        }
                    },
                    "questions": questions
                }
            },
            "location": {"index": index}
        }
    })
    index += 1

if requests:
    update_body = {"requests": requests}
    form_service.forms().batchUpdate(formId=form_id, body=update_body).execute()


