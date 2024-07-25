
import requests
import os
import re

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GH_API_URL = "https://api.github.com/"
FRONT_API_URL = "https://api2.frontapp.com/"
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
DISCUSSION_URL = os.environ.get("DISCUSSION_URL")
DISCUSSION_TITLE = os.environ.get("DISCUSSION_TITLE")
DISCUSSION_NUMBER = os.environ.get("DISCUSSION_NUMBER")
GITHUB_USER = os.environ.get("GITHUB_USER")
FRONT_USER = os.environ.get("FRONT_USER", "")
DISCUSSION_BODY = os.environ.get("DISCUSSION_BODY")
FRONT_TOKEN = os.environ.get("FRONT_TOKEN")

def get_front_link_ids_from_dicussion_body(discussion_body):
    front_link_pattern = re.compile(r'https://app.frontapp.com/open/((?:cnv|msg)\_.*)\?key=.*')
    matches = front_link_pattern.findall(discussion_body)
    
    if matches:
        return matches
    return None

def convert_messages_to_conversations(front_link_ids):
    for index, front_link_datum in enumerate(front_link_ids):
        if front_link_datum.startswith("msg"):
            response = requests.get(FRONT_API_URL + "messages/" + front_link_datum, headers={"Authorization": "Bearer " + FRONT_TOKEN})
            if response.status_code == 200:
                conversation_link = response.json().get("_links").get("related").get("conversation")
                conversation_id = conversation_link.split("/")[-1]
                front_link_ids[index] = conversation_id
    return front_link_ids

def get_discussion_number_from_issue_body(issue_body):
    discussion_url_pattern = re.compile(r'https://github.com/{}/discussions/(\d+)'.format(GITHUB_REPOSITORY))
    match = discussion_url_pattern.search(issue_body)
    
    if match:
        discussion_number = match.group(1)
        return discussion_number
    return None

def add_comment_to_conversation(conversation_id):
    comment = f"""**🎀 Product Suggestion Posted 🎀**\n\n#{DISCUSSION_NUMBER} "{DISCUSSION_TITLE}\"\n_{GITHUB_USER}_\n\n{DISCUSSION_URL}"""
    api_url = FRONT_API_URL + "conversations/" + conversation_id + "/comments"

    response = requests.post(api_url, json={"body": comment, "author_id": FRONT_USER}, headers={"Authorization": "Bearer " + FRONT_TOKEN})
    if response.ok:
        print(f"Added comment to conversation {conversation_id}")
    else:
        print(f"Failed to add comment to conversation {conversation_id}")

front_link_ids = get_front_link_ids_from_dicussion_body(DISCUSSION_BODY)
if front_link_ids:
    front_link_ids = convert_messages_to_conversations(front_link_ids)
    for front_link_id in front_link_ids:
        add_comment_to_conversation(front_link_id)

