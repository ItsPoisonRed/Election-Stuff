from socialchoice import RankedChoiceBallotBox, Election
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from collections import defaultdict

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

form_decision=input('\nEnter a form id or press Enter to create a new form: ').strip()

if form_decision=='':
    from form_creation import form_id
else:
    form_id=form_decision

print(f"https://docs.google.com/forms/d/{form_id}")

input("Press Enter after all responses are submitted...")


form_info = form_service.forms().get(formId=form_id).execute()

position_to_qids = {}
qid_to_candidate = {}

for item in form_info.get('items', []):
    if 'questionGroupItem' in item:
        position = item.get('title', 'Unknown Position')
        position_to_qids[position] = []
        
        for question in item['questionGroupItem'].get('questions', []):
            q_id = question['questionId']
            cand_name = question['rowQuestion']['title']
            
            position_to_qids[position].append(q_id)
            qid_to_candidate[q_id] = cand_name

result = form_service.forms().responses().list(formId=form_id).execute()
responses = result.get('responses', [])

if not responses:
    print("No responses found yet.")
else:
    for position, qids in position_to_qids.items():
        election_results = []
        
        for response in responses:
            answers = response.get('answers', {})
            rank_to_candidates = defaultdict(set)
            
            for q_id in qids:
                if q_id in answers:
                    answer_details = answers[q_id]
                    answer_text = answer_details.get('textAnswers', {}).get('answers', [{}])[0].get('value', '')
                    
                    digits = ''.join(filter(str.isdigit, answer_text))
                    if digits:
                        rank_number = int(digits)
                        cand_name = qid_to_candidate[q_id]
                        
                        rank_to_candidates[rank_number].add(cand_name)
            
            if not rank_to_candidates:
                continue 
                
            elector_result = []
            for rank in sorted(rank_to_candidates.keys()):
                cands = rank_to_candidates[rank]
                if len(cands) == 1:
                    elector_result.append(list(cands)[0])
                else:
                    elector_result.append(cands)
                    
            election_results.append(elector_result)
        if election_results:
            ranked_ballots = RankedChoiceBallotBox(election_results)
            election = Election(ranked_ballots)
            print(f"Winner Ranking of {position[24:]}:")
            election_result=election.ranking_by_ranked_pairs()
            for i in range(len(election_result)):
                print(f"{i+1}. {election_result[i]}")
        else:
            print("No valid votes for this position.")
        print("\n")
