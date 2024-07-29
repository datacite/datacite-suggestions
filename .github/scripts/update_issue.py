import requests
import os
import re
import csv

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GH_API_URL = "https://api.github.com/"
DEST_REPO = os.environ.get("DEST_REPO")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
ISSUE_BODY = os.environ.get("ISSUE_BODY")
ISSUE_NUMBER = os.environ.get("ISSUE_NUMBER")
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

def get_discussion_details(discussion_number):
    owner = GITHUB_REPOSITORY.split('/')[0]
    name = GITHUB_REPOSITORY.split('/')[1]
    query = f"""
        {{
            repository(owner: "{owner}", name: "{name}") {{
                    discussion(number: {discussion_number}) {{
                    id
                    body
                    labels(first:100) {{
                        nodes {{
                            name
                        }}
                    }}
                }}
            }}
        }}
    """
    response = requests.post(GH_API_URL + "graphql", json={"query": query}, headers={"Authorization": "bearer " + GITHUB_TOKEN})

    if response.status_code == 200:
        return response.json().get("data").get("repository").get("discussion")
    else:
        return None

def add_labels_to_issue(label_names):
    url = GH_API_URL + "repos/" + GITHUB_REPOSITORY + "/issues/" + ISSUE_NUMBER + "/labels"

    response = requests.post(url, json={"labels": label_names}, headers={"Authorization": "token " + GITHUB_TOKEN})
    if response.status_code == 200:
        print("Success")
    else:
        print("Failure")
    return

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
    if response.ok:
        print("Success")
    else:
        print("Failure")
    return

def get_matching_labels(discussion_body):
    reader = list(csv.DictReader(open("label_mapping.csv", "r")))

    matching_labels = []
    for row in reader:
        row_type = row.get("type")
        match row_type:
            case "check":
                text_to_match = "- [X] " + row.get("text")
                if text_to_match in discussion_body:
                    matching_labels.append(row.get("label"))
    return matching_labels

# Update source discussion as logged
discussion_number = get_discussion_number_from_issue_body(ISSUE_BODY)
label_id = get_label_id(TRANSFERRED_LABEL)
discussion = get_discussion_details(discussion_number)
discussion_id = discussion.get("id")
discussion_body = discussion.get("body")
discussion_labels = discussion.get("labels").get("nodes")
update_discussion_with_label(discussion_id, label_id)

# Update issue with discussion labels
label_names = [label['name'] for label in discussion_labels]
if TRANSFERRED_LABEL in label_names:
    label_names.remove(TRANSFERRED_LABEL)
add_labels_to_issue(label_names)

# Update issue with matching labels from mapping
print(os. getcwd())
matching_labels = get_matching_labels(discussion_body)
add_labels_to_issue(matching_labels)
