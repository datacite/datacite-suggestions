
import requests
import os
import re

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GH_API_URL = "https://api.github.com/"
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
ISSUE_BODY = os.environ.get("ISSUE_BODY")
TRANSFERRED_LABEL = os.environ.get("TRANSFERRED_LABEL")


def get_discussion_number_from_issue_body(issue_body):
    discussion_url_pattern = re.compile(r'https://github.com/{}/discussions/(\d+)'.format(GITHUB_REPOSITORY))
    match = discussion_url_pattern.search(issue_body)
    
    if match:
        discussion_number = match.group(1)
        return discussion_number
    return None

def get_label_id(label_name): 
    response = requests.get(GH_API_URL + "repos/" + GITHUB_REPOSITORY + "/labels/" + label_name, headers={"Authorization": "token " + GITHUB_TOKEN})

    if response.status_code == 200:
        return response.json()["node_id"]
    else:
        return None

def get_discussion_id(discussion_number):
    owner = GITHUB_REPOSITORY.split('/')[0]
    name = GITHUB_REPOSITORY.split('/')[1]
    query = f"""
        {
            repository(owner: "{owner}", name: "{name}") {
                    discussion(number: {discussion_number}) {
                    id
                }
            }
        }
    """
    response = requests.post(GH_API_URL + "graphql", json={"query": query}, headers={"Authorization": "bearer " + GITHUB_TOKEN})

    if response.status_code == 200:
        return response.json().get("data").get("repository").get("discussion").get("id")
    else:
        return None

def update_discussion_with_label(discussion_id, label_id):
    query = f"""
        mutation {{
            addLabelsToLabelable(
                input:{{
                labelableId: "{discussion_id}",
                labelIds: "{label_id}"
                }}
            ) {{
                clientMutationId
            }}
    }}
    """
    response = requests.post(GH_API_URL + "graphql", json={"query": query}, headers={"Authorization": "bearer " + GITHUB_TOKEN})
    return

discussion_number = get_discussion_number_from_issue_body(ISSUE_BODY)
label_id = get_label_id(TRANSFERRED_LABEL)
discussion_id = get_discussion_id(discussion_number)
update_discussion_with_label(discussion_id, label_id)
