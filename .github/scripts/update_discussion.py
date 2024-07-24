from github import Github
import re
import os
import requests

# Get environment variables
issue_body = os.getenv('ISSUE_BODY')
transferred_label = os.getenv('TRANSFERRED_LABEL')
repo_name = os.getenv('GITHUB_REPOSITORY')
token = os.getenv('GITHUB_TOKEN')

# Extract discussion ID from the issue body
match = re.search(r'https://github.com/.*/discussions/(\d+)', issue_body)
if match:
    discussion_id = match.group(1)
    
    # GitHub API URL for discussions
    api_url = f"https://api.github.com/repos/{repo_name}/discussions/{discussion_id}/labels"
    
    # Headers for API request
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Data for adding a label
    data = {
        "labels": [transferred_label]
    }
    
    # Make the API request to add the label
    response = requests.post(api_url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"Label added to discussion {discussion_id}.")
    else:
        print(f"Failed to add label: {response.status_code}, {response.text}")
else:
    print("No discussion link found in the issue body.")
