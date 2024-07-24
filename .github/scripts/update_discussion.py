from github import Github
import re
import os

# Initialize GitHub client
token = os.getenv('GITHUB_TOKEN')
label = os.getenv('TRANSFERRED_LABEL')
g = Github(token)

# Get repository
repo = g.get_repo(os.getenv('GITHUB_REPOSITORY'))

# Get the issue from the environment
issue_number = int(os.getenv('ISSUE_NUMBER'))
issue = repo.get_issue(number=issue_number)

# Regular expression to find GitHub Discussions links
discussions_pattern = re.compile(r'https://github.com/.*/discussions/(\d+)')

# Search for discussions link in the issue body
match = discussions_pattern.search(issue.body)

if match:
    discussion_number = match.group(1)
    discussion = repo.get_discussion(discussion_number)
    
    # Add label to the discussion
    discussion.edit(labels=[label])  # Replace 'your-label' with the desired label

print(f'Updated discussion #{discussion_number} with label.')