from typing import List, Dict
import requests

class BaseGitClient:
    """Abstract base class for all Git providers."""
    def get_pr_files(self, repo: str, pr_number: int) -> List[Dict]:
        """Return list of files changed in a PR."""
        raise NotImplementedError


# --- GitHub ---
class GitHubClient(BaseGitClient):
    def __init__(self, token: str):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        })

    def get_pr_files(self, repo: str, pr_number: int):
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/files"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()


# --- GitLab ---
class GitLabClient(BaseGitClient):
    def __init__(self, token: str):
        self.base_url = "https://gitlab.com/api/v4"
        self.session = requests.Session()
        self.session.headers.update({"PRIVATE-TOKEN": token})

    def get_pr_files(self, repo: str, pr_number: int):
        # GitLab uses "merge_requests" terminology
        url = f"{self.base_url}/projects/{repo}/merge_requests/{pr_number}/changes"
        r = self.session.get(url)
        r.raise_for_status()
        # GitLab returns changes under 'changes'
        return r.json().get("changes", [])


# --- Bitbucket ---
class BitbucketClient(BaseGitClient):
    def __init__(self, username: str, app_password: str):
        self.base_url = "https://api.bitbucket.org/2.0"
        self.session = requests.Session()
        self.session.auth = (username, app_password)

    def get_pr_files(self, repo: str, pr_number: int):
        url = f"{self.base_url}/repositories/{repo}/pullrequests/{pr_number}/diffstat"
        r = self.session.get(url)
        r.raise_for_status()
        # Bitbucket returns diffs under 'values'
        return r.json().get("values", [])
