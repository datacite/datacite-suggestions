import requests
import os
import re

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GH_API_URL = "https://api.github.com/"
DEST_REPO = os.environ.get("DEST_REPO")
GH_REPO = os.environ.get("GH_REPO")
NAME = os.environ.get("NAME")
FROM_NAME = os.environ.get("FROM_NAME")
NEW_NAME = os.environ.get("NEW_NAME")
EVENT_TYPE = os.environ.get("EVENT_TYPE")

def get_label_in_repo(label_name, repo):
    response = requests.get(GH_API_URL + "repos/" + repo + "/labels/" + label_name, headers={"Authorization": "bearer " + GITHUB_TOKEN})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"{label_name} not found in {repo}")
        return {}

def update_label_in_dest_repo(label_name, local_label):
    payload = {"new_name": local_label.get("name"), "color": local_label.get("color"), "description": local_label.get("description", "")}
    response = requests.patch(GH_API_URL + "repos/" + DEST_REPO + "/labels/" + label_name, headers={"Authorization": "bearer " + GITHUB_TOKEN}, json=payload)
    if response.status_code == 200:
        print("Success")
    else:
        print("Failed")

def delete_label_in_dest_repo(label_name):
    response = requests.delete(GH_API_URL + "repos/" + DEST_REPO + "/labels/" + label_name, headers={"Authorization": "bearer " + GITHUB_TOKEN})
    if response.status_code == 204:
        print("Success")
    else:
        print("Failed")

if EVENT_TYPE == "edited":
    from_name = FROM_NAME if FROM_NAME else NAME

    dest_label = get_label_in_repo(from_name, DEST_REPO)
    local_label = get_label_in_repo(NEW_NAME, GH_REPO)

    changed = dest_label.get("name") != local_label.get("name") or dest_label.get("color") != local_label.get("color") or dest_label.get("description") != local_label.get("description")
    
    if dest_label and changed:
        update_label_in_dest_repo(from_name, local_label)

if EVENT_TYPE == "deleted":
    label_name = NAME
    if get_label_in_repo(label_name, DEST_REPO):
        delete_label_in_dest_repo(label_name)